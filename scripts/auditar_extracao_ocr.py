import argparse
import csv
import datetime
import hashlib
import json
import re
import unicodedata
from pathlib import Path


EXTENSOES_PERMITIDAS = {".jpg", ".jpeg", ".png"}
CAMPOS_AUDITADOS = ["empresa", "numero_nf", "chave_acesso", "vencimento", "valor_total"]
TERMOS_EMPRESA_SUSPEITA = [
    "NOTA FISCAL",
    "DOCUMENTO AUXILIAR",
    "DANFE",
    "ELETRONICA",
    "ELETRÔNICA",
    "EE EE",
    "EEE",
    "CHAVE DE ACESSO",
]


def normalizar_texto(texto):
    texto = texto or ""
    texto = unicodedata.normalize("NFKD", texto)
    texto = "".join(ch for ch in texto if not unicodedata.combining(ch))
    return texto.upper()


def hash_arquivo(caminho):
    digest = hashlib.sha256()
    with Path(caminho).open("rb") as arquivo:
        for bloco in iter(lambda: arquivo.read(65536), b""):
            digest.update(bloco)
    return digest.hexdigest()


def nome_seguro(nome):
    stem = Path(nome).stem
    seguro = re.sub(r"[^A-Za-z0-9_-]+", "_", stem).strip("_")
    return seguro or "documento"


def listar_amostras(amostras_dir):
    amostras = []
    avisos = []
    for path in sorted(Path(amostras_dir).iterdir(), key=lambda p: p.name.lower()):
        if not path.is_file():
            continue
        if path.suffix.lower() not in EXTENSOES_PERMITIDAS:
            avisos.append(f"Ignorado arquivo com extensão não permitida: {path.name}")
            continue
        amostras.append(path)
    return amostras, avisos


def obter_valor_campo(doc_json, campo):
    dados = (doc_json.get("documento") or {}).get(campo) or {}
    if isinstance(dados, dict):
        return dados.get("valor"), dados.get("confianca"), dados.get("fonte")
    return dados, None, None


def executar_ocr_parser_atual(caminho):
    from models.documento_extraido import montar_documento_fiscal
    from ocr_pipeline_s1 import carregar_config, configurar_tesseract, extract_text
    from parser_nf import parse_ocr

    config = carregar_config()
    idioma = configurar_tesseract(config)
    texto = extract_text(str(caminho), idioma)
    parsed = parse_ocr(texto)
    doc = montar_documento_fiscal(
        cliente_id=0,
        parsed=parsed,
        texto_extraido=texto,
        arquivo_nome=Path(caminho).name,
        arquivo_origem=str(caminho),
        arquivo_hash=hash_arquivo(caminho),
        arquivo_destino=None,
        idiomas=idioma.split("+"),
    )
    return texto, doc.to_dict()


def empresa_suspeita(valor):
    texto = normalizar_texto(valor).strip()
    if not texto:
        return False
    if len(texto) < 6:
        return True
    if re.fullmatch(r"[E\s]+", texto):
        return True
    if len(re.sub(r"[^A-Z0-9]", "", texto)) <= 3:
        return True
    return any(termo in texto for termo in [normalizar_texto(t) for t in TERMOS_EMPRESA_SUSPEITA])


def detectar_numeros_nf(texto):
    texto_norm = normalizar_texto(texto)
    padrao = re.compile(
        r"\b(?:N[º°O]?|NF|NFE|NOTA|DOCUMENTO|SERIE|SERIE:)\b[^0-9]{0,40}(\d{3,10})",
        re.IGNORECASE,
    )
    return sorted(set(match.group(1) for match in padrao.finditer(texto_norm)))[:10]


def detectar_datas(texto):
    datas = re.findall(r"\b\d{1,2}/\d{1,2}/\d{2,4}\b|\b\d{4}-\d{2}-\d{2}\b", texto or "")
    return sorted(set(datas))[:20]


def detectar_valores(texto):
    texto_norm = normalizar_texto(texto)
    valores = re.findall(r"(?:R\$\s*)?\d{1,3}(?:\.\d{3})*,\d{2}|(?:R\$\s*)?\d+,\d{2}", texto_norm)
    linhas_chave = [
        linha.strip()
        for linha in texto_norm.splitlines()
        if any(termo in linha for termo in ["VALOR TOTAL", "VALOR LIQUIDO", "VALOR DA NOTA", "TOTAL DA NOTA", "R$"])
    ]
    return {
        "valores": sorted(set(valores))[:20],
        "linhas": linhas_chave[:10],
    }


def detectar_imagem_suspeita(texto, caminho):
    alertas = []
    texto = texto or ""
    if len(texto.strip()) < 80:
        alertas.append("ocr_bruto_com_pouco_texto")

    if texto:
        caracteres_estranhos = sum(1 for ch in texto if not (ch.isalnum() or ch.isspace() or ch in "/-.,:;R$º°()[]"))
        if caracteres_estranhos / max(len(texto), 1) > 0.20:
            alertas.append("proporcao_alta_de_caracteres_estranhos")

    try:
        from PIL import Image

        with Image.open(caminho) as img:
            largura, altura = img.size
        proporcao = max(largura, altura) / max(min(largura, altura), 1)
        if proporcao > 3.0:
            alertas.append("proporcao_de_imagem_sugere_orientacao_ou_recorte")
    except Exception:
        alertas.append("dimensoes_da_imagem_indisponiveis")

    return alertas


def carregar_gabarito(esperado_dir, imagem_path):
    if not esperado_dir:
        return None
    caminho = Path(esperado_dir) / f"{imagem_path.stem}.json"
    if not caminho.is_file():
        return None
    return json.loads(caminho.read_text(encoding="utf-8"))


def comparar_valores(extraido, esperado):
    if esperado is None and extraido in (None, ""):
        return True
    return str(extraido or "").strip() == str(esperado or "").strip()


def auditar_campos(texto_ocr, doc_json, gabarito=None):
    campos = {}
    alertas = []
    indicios = {
        "numeros_nf": detectar_numeros_nf(texto_ocr),
        "datas": detectar_datas(texto_ocr),
        "valores": detectar_valores(texto_ocr),
    }

    for campo in CAMPOS_AUDITADOS:
        valor, confianca, fonte = obter_valor_campo(doc_json, campo)
        status = "ok" if valor not in (None, "") else "ausente"
        alertas_campo = []

        if campo == "empresa" and empresa_suspeita(valor):
            status = "suspeito"
            alertas_campo.append("empresa_suspeita")

        if campo == "numero_nf" and not valor and indicios["numeros_nf"]:
            status = "encontrado_no_ocr_mas_nao_extraido"
            alertas_campo.append("numero_nf_possivel_no_ocr")

        if campo == "vencimento" and not valor and indicios["datas"]:
            status = "encontrado_no_ocr_mas_nao_extraido"
            alertas_campo.append("data_possivel_no_ocr")

        if campo == "valor_total" and not valor and (indicios["valores"]["valores"] or indicios["valores"]["linhas"]):
            status = "encontrado_no_ocr_mas_nao_extraido"
            alertas_campo.append("valor_possivel_no_ocr")

        valor_esperado = None
        if gabarito and campo in gabarito:
            valor_esperado = gabarito.get(campo)
            if not comparar_valores(valor, valor_esperado):
                status = "divergente_do_gabarito"
                alertas_campo.append("divergente_do_gabarito")

        campos[campo] = {
            "valor_extraido": valor,
            "valor_esperado": valor_esperado,
            "confianca": confianca,
            "fonte": fonte,
            "status": status,
            "alertas": alertas_campo,
        }
        alertas.extend(f"{campo}:{alerta}" for alerta in alertas_campo)

    return campos, alertas, indicios


def classificar_provavel(alertas, imagem_alertas, campos):
    classes = []
    if imagem_alertas:
        classes.append("imagem/qualidade/orientação")
    if "ocr_bruto_com_pouco_texto" in imagem_alertas:
        classes.append("OCR bruto")
    if any("possivel_no_ocr" in alerta or "empresa_suspeita" in alerta for alerta in alertas):
        classes.append("parser")
    if any(campo["status"] == "ausente" for campo in campos.values()):
        classes.append("campo realmente ausente")
    if any(campo["status"] == "divergente_do_gabarito" for campo in campos.values()):
        classes.append("validação incompleta")
    return classes or ["sem_alerta_relevante"]


def trechos_relevantes(texto):
    termos = ["UNILIDER", "DISTRIBUIDORA", "NFE", "NF", "NOTA", "VENC", "VALOR", "TOTAL", "CHAVE", "DANFE"]
    linhas = []
    for linha in (texto or "").splitlines():
        linha_norm = normalizar_texto(linha)
        if any(termo in linha_norm for termo in termos) or re.search(r"\d{1,2}/\d{1,2}/\d{2,4}", linha):
            linhas.append(linha.strip())
    return [linha for linha in linhas if linha][:20]


def auditar_arquivo(caminho, saida_dir, esperado_dir=None, executor=None):
    executor = executor or executar_ocr_parser_atual
    texto_ocr, doc_json = executor(caminho)
    gabarito = carregar_gabarito(esperado_dir, caminho)
    campos, alertas, indicios = auditar_campos(texto_ocr, doc_json, gabarito=gabarito)
    imagem_alertas = detectar_imagem_suspeita(texto_ocr, caminho)
    alertas.extend(imagem_alertas)

    base_nome = nome_seguro(caminho.name)
    ocr_dir = Path(saida_dir) / "ocr_bruto_por_arquivo"
    json_dir = Path(saida_dir) / "json_extraido_por_arquivo"
    ocr_dir.mkdir(parents=True, exist_ok=True)
    json_dir.mkdir(parents=True, exist_ok=True)
    (ocr_dir / f"{base_nome}.txt").write_text(texto_ocr or "", encoding="utf-8")
    (json_dir / f"{base_nome}.json").write_text(
        json.dumps(doc_json, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

    return {
        "arquivo": caminho.name,
        "hash": hash_arquivo(caminho),
        "campos_extraidos": campos,
        "alertas": alertas,
        "indicios_ocr": indicios,
        "comparacao_gabarito": {campo: dados["status"] for campo, dados in campos.items()} if gabarito else None,
        "classificacao_provavel": classificar_provavel(alertas, imagem_alertas, campos),
        "trechos_relevantes_ocr": trechos_relevantes(texto_ocr),
        "json_resumido": {
            "schema": doc_json.get("schema"),
            "status": doc_json.get("status"),
            "documento": {
                campo: campos[campo]["valor_extraido"] for campo in CAMPOS_AUDITADOS
            },
        },
    }


def gerar_markdown(relatorio, caminho_saida):
    linhas = [
        "# DIAG-OCR-01 - Relatório de Auditoria da Extração",
        "",
        "Este relatório é diagnóstico local. Ele não corrige OCR/parser e não deve ser commitado quando contiver dados reais.",
        "",
        f"Data/hora da auditoria: {relatorio['gerado_em']}",
        f"Arquivos analisados: {len(relatorio['documentos'])}",
        "",
        "## Resumo geral",
        "",
        f"- Avisos seguros: {len(relatorio['avisos'])}",
        f"- Documentos com alertas: {sum(1 for doc in relatorio['documentos'] if doc['alertas'])}",
        "",
        "## Tabela por documento",
        "",
        "| arquivo | status geral | empresa | numero_nf | chave_acesso | vencimento | valor_total | alertas |",
        "|---|---|---|---|---|---|---|---|",
    ]

    for doc in relatorio["documentos"]:
        campos = doc["campos_extraidos"]
        valores = [str(campos[campo]["valor_extraido"] or "-").replace("|", " ") for campo in CAMPOS_AUDITADOS]
        linhas.append(
            "| "
            + " | ".join([
                doc["arquivo"],
                ", ".join(doc["classificacao_provavel"]),
                *valores,
                "; ".join(doc["alertas"]) or "-",
            ])
            + " |"
        )

    for doc in relatorio["documentos"]:
        linhas.extend([
            "",
            f"## Documento: {doc['arquivo']}",
            "",
            "### JSON extraído resumido",
            "",
            "```json",
            json.dumps(doc["json_resumido"], ensure_ascii=False, indent=2),
            "```",
            "",
            "### Alertas",
            "",
            *(f"- {alerta}" for alerta in (doc["alertas"] or ["sem alertas"])),
            "",
            "### Trechos relevantes do OCR bruto",
            "",
            *(f"- {trecho}" for trecho in (doc["trechos_relevantes_ocr"] or ["sem trechos relevantes"])),
            "",
            "### Indícios encontrados mas não aproveitados",
            "",
            f"- Números NF candidatos: {doc['indicios_ocr']['numeros_nf'] or '-'}",
            f"- Datas candidatas: {doc['indicios_ocr']['datas'] or '-'}",
            f"- Valores candidatos: {doc['indicios_ocr']['valores']['valores'] or '-'}",
        ])

    linhas.extend([
        "",
        "## Próxima recomendação",
        "",
        "Manter este resultado como diagnóstico e abrir AJUSTE-OCR-01 somente após revisão humana do relatório.",
        "",
    ])
    Path(caminho_saida).write_text("\n".join(linhas), encoding="utf-8")


def gerar_csv(relatorio, caminho_saida):
    with Path(caminho_saida).open("w", encoding="utf-8", newline="") as arquivo:
        writer = csv.DictWriter(
            arquivo,
            fieldnames=["arquivo", "campo", "valor_extraido", "valor_esperado", "status", "alertas"],
        )
        writer.writeheader()
        for doc in relatorio["documentos"]:
            for campo, dados in doc["campos_extraidos"].items():
                writer.writerow({
                    "arquivo": doc["arquivo"],
                    "campo": campo,
                    "valor_extraido": dados["valor_extraido"],
                    "valor_esperado": dados["valor_esperado"],
                    "status": dados["status"],
                    "alertas": ";".join(dados["alertas"]),
                })


def auditar_pasta(amostras_dir, saida_dir, esperado_dir=None, executor=None):
    amostras_path = Path(amostras_dir)
    if not amostras_path.is_dir():
        raise ValueError("Pasta de amostras não encontrada.")

    saida_path = Path(saida_dir)
    saida_path.mkdir(parents=True, exist_ok=True)
    (saida_path / "ocr_bruto_por_arquivo").mkdir(parents=True, exist_ok=True)
    (saida_path / "json_extraido_por_arquivo").mkdir(parents=True, exist_ok=True)

    amostras, avisos = listar_amostras(amostras_path)
    documentos = [
        auditar_arquivo(amostra, saida_path, esperado_dir=esperado_dir, executor=executor)
        for amostra in amostras
    ]
    relatorio = {
        "gerado_em": datetime.datetime.now().isoformat(timespec="seconds"),
        "amostras_dir": str(amostras_path),
        "saida_dir": str(saida_path),
        "avisos": avisos,
        "documentos": documentos,
    }

    (saida_path / "relatorio_extracao.json").write_text(
        json.dumps(relatorio, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    gerar_markdown(relatorio, saida_path / "relatorio_extracao.md")
    gerar_csv(relatorio, saida_path / "comparativo_campos.csv")
    return relatorio


def main(argv=None):
    parser = argparse.ArgumentParser(description="Auditoria local da extração OCR/parser")
    parser.add_argument("--amostras", required=True, help="Pasta privada com imagens .jpg/.jpeg/.png")
    parser.add_argument("--saida", required=True, help="Pasta privada de relatórios")
    parser.add_argument("--esperado", default=None, help="Pasta opcional com gabaritos JSON")
    args = parser.parse_args(argv)

    try:
        relatorio = auditar_pasta(args.amostras, args.saida, esperado_dir=args.esperado)
    except ValueError as exc:
        print(f"ERRO: {exc}")
        return 1

    print("DIAG-OCR-01 - auditoria concluída")
    print(f"Arquivos analisados: {len(relatorio['documentos'])}")
    print(f"Saída: {args.saida}")
    print("Nenhum banco, API, UI, OCR/parser/core foi alterado.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

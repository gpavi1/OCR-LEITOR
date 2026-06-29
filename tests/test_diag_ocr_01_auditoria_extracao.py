import json
from pathlib import Path
import sys

BASE_DIR = Path(__file__).resolve().parents[1]
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from scripts.auditar_extracao_ocr import (
    EXTENSOES_PERMITIDAS,
    auditar_campos,
    auditar_pasta,
    empresa_suspeita,
    main,
)

SCRIPT_PATH = BASE_DIR / "scripts" / "auditar_extracao_ocr.py"
DOC_PATH = BASE_DIR / "docs" / "diagnostico" / "DIAG-OCR-01_AUDITORIA_EXTRACAO.md"
GITIGNORE_PATH = BASE_DIR / ".gitignore"


def doc_json(empresa="EE EE EE EEE", numero_nf=None, chave="1" * 44, vencimento=None, valor_total=None):
    def campo(valor, fonte="parser_nf"):
        return {"valor": valor, "confianca": 90 if valor else 0, "fonte": fonte if valor else None}

    return {
        "schema": "ocr_leitor.documento_fiscal.v1",
        "status": "parcial",
        "documento": {
            "empresa": campo(empresa),
            "numero_nf": campo(numero_nf),
            "chave_acesso": campo(chave, "sequencia_44_digitos"),
            "vencimento": campo(vencimento, "contexto_financeiro"),
            "valor_total": campo(valor_total, "valor_total_nota_fiscal"),
        },
    }


def ocr_texto_util():
    return "\n".join([
        "UNILIDER DISTRIBUIDORA S/A",
        "DANFE Documento Auxiliar da Nota Fiscal Eletronica",
        "NF 1281694 serie 1",
        "CHAVE DE ACESSO 33260605424008000360550010012816941717629941",
        "Vencimento 11/06/2026",
        "VALOR TOTAL DA NOTA R$ 1.234,56",
    ])


def executor_fake(_caminho):
    return ocr_texto_util(), doc_json()


def criar_amostras(tmp_path):
    amostras = tmp_path / "imagens"
    amostras.mkdir()
    (amostras / "nota1.jpg").write_bytes(b"fake-jpg")
    (amostras / "ignorar.txt").write_text("nao processar", encoding="utf-8")
    return amostras


def test_script_existe():
    assert SCRIPT_PATH.is_file()


def test_documentacao_existe():
    assert DOC_PATH.is_file()


def test_script_aceita_pasta_de_amostras(tmp_path):
    amostras = criar_amostras(tmp_path)
    saida = tmp_path / "relatorios"

    relatorio = auditar_pasta(amostras, saida, executor=executor_fake)

    assert relatorio["amostras_dir"] == str(amostras)
    assert len(relatorio["documentos"]) == 1


def test_script_aceita_pasta_de_saida(tmp_path):
    amostras = criar_amostras(tmp_path)
    saida = tmp_path / "relatorios"

    auditar_pasta(amostras, saida, executor=executor_fake)

    assert saida.is_dir()


def test_script_rejeita_pasta_inexistente(tmp_path):
    codigo = main(["--amostras", str(tmp_path / "nao_existe"), "--saida", str(tmp_path / "saida")])
    assert codigo == 1


def test_script_aceita_somente_jpg_jpeg_png():
    assert EXTENSOES_PERMITIDAS == {".jpg", ".jpeg", ".png"}


def test_script_ignora_extensao_invalida_com_aviso(tmp_path):
    amostras = criar_amostras(tmp_path)
    relatorio = auditar_pasta(amostras, tmp_path / "saida", executor=executor_fake)

    assert any("extensão não permitida" in aviso for aviso in relatorio["avisos"])


def test_script_cria_relatorio_extracao_md(tmp_path):
    auditar_pasta(criar_amostras(tmp_path), tmp_path / "saida", executor=executor_fake)
    assert (tmp_path / "saida" / "relatorio_extracao.md").is_file()


def test_script_cria_relatorio_extracao_json(tmp_path):
    auditar_pasta(criar_amostras(tmp_path), tmp_path / "saida", executor=executor_fake)
    assert (tmp_path / "saida" / "relatorio_extracao.json").is_file()


def test_script_cria_comparativo_campos_csv(tmp_path):
    auditar_pasta(criar_amostras(tmp_path), tmp_path / "saida", executor=executor_fake)
    assert (tmp_path / "saida" / "comparativo_campos.csv").is_file()


def test_script_cria_ocr_bruto_por_arquivo(tmp_path):
    auditar_pasta(criar_amostras(tmp_path), tmp_path / "saida", executor=executor_fake)
    assert (tmp_path / "saida" / "ocr_bruto_por_arquivo" / "nota1.txt").is_file()


def test_script_cria_json_extraido_por_arquivo(tmp_path):
    auditar_pasta(criar_amostras(tmp_path), tmp_path / "saida", executor=executor_fake)
    assert (tmp_path / "saida" / "json_extraido_por_arquivo" / "nota1.json").is_file()


def test_detecta_empresa_suspeita_ee_ee_ee_eee():
    assert empresa_suspeita("EE EE EE EEE") is True


def test_detecta_termo_generico_como_empresa_suspeita():
    assert empresa_suspeita("DOCUMENTO AUXILIAR DA NOTA FISCAL") is True


def test_detecta_numero_possivel_no_ocr_quando_numero_nf_vazio():
    campos, alertas, indicios = auditar_campos(ocr_texto_util(), doc_json(numero_nf=None))

    assert "1281694" in indicios["numeros_nf"]
    assert campos["numero_nf"]["status"] == "encontrado_no_ocr_mas_nao_extraido"
    assert "numero_nf:numero_nf_possivel_no_ocr" in alertas


def test_detecta_data_no_ocr_quando_vencimento_vazio():
    campos, _alertas, indicios = auditar_campos(ocr_texto_util(), doc_json(vencimento=None))

    assert "11/06/2026" in indicios["datas"]
    assert campos["vencimento"]["status"] == "encontrado_no_ocr_mas_nao_extraido"


def test_detecta_valor_monetario_no_ocr_quando_valor_total_vazio():
    campos, _alertas, indicios = auditar_campos(ocr_texto_util(), doc_json(valor_total=None))

    assert "R$ 1.234,56" in indicios["valores"]["valores"]
    assert campos["valor_total"]["status"] == "encontrado_no_ocr_mas_nao_extraido"


def test_compara_com_gabarito_quando_existir(tmp_path):
    amostras = criar_amostras(tmp_path)
    esperado = tmp_path / "esperado"
    esperado.mkdir()
    (esperado / "nota1.json").write_text(
        json.dumps({"empresa": "UNILIDER DISTRIBUIDORA S/A", "numero_nf": "1281694"}),
        encoding="utf-8",
    )

    relatorio = auditar_pasta(amostras, tmp_path / "saida", esperado_dir=esperado, executor=executor_fake)

    comparacao = relatorio["documentos"][0]["comparacao_gabarito"]
    assert comparacao["empresa"] == "divergente_do_gabarito"
    assert comparacao["numero_nf"] == "divergente_do_gabarito"


def test_funciona_sem_gabarito(tmp_path):
    relatorio = auditar_pasta(criar_amostras(tmp_path), tmp_path / "saida", executor=executor_fake)
    assert relatorio["documentos"][0]["comparacao_gabarito"] is None


def test_script_nao_altera_banco():
    conteudo = SCRIPT_PATH.read_text(encoding="utf-8")
    assert "from database" not in conteudo
    assert "database.mysql_db" not in conteudo
    assert "INSERT INTO" not in conteudo
    assert "UPDATE " not in conteudo
    assert "ALTER TABLE" not in conteudo


def test_script_nao_chama_api():
    conteudo = SCRIPT_PATH.read_text(encoding="utf-8")
    assert "flask" not in conteudo.lower()
    assert "@app.route" not in conteudo
    assert "/api/" not in conteudo


def test_script_nao_altera_ocr_parser_core():
    conteudo = SCRIPT_PATH.read_text(encoding="utf-8")
    assert "def parse_ocr" not in conteudo
    assert "def extrair_" not in conteudo
    assert "write_text" in conteudo


def test_script_nao_usa_internet():
    conteudo = SCRIPT_PATH.read_text(encoding="utf-8").lower()
    assert "requests" not in conteudo
    assert "urllib" not in conteudo
    assert "openai" not in conteudo
    assert "http://" not in conteudo
    assert "https://" not in conteudo


def test_script_nao_grava_dados_reais_em_arquivos_versionados(tmp_path):
    saida = tmp_path / "relatorios"
    auditar_pasta(criar_amostras(tmp_path), saida, executor=executor_fake)
    assert saida.is_relative_to(tmp_path)
    assert not saida.is_relative_to(BASE_DIR)


def test_gitignore_protege_amostras_privadas():
    conteudo = GITIGNORE_PATH.read_text(encoding="utf-8")
    assert "_amostras_privadas/" in conteudo
    assert "relatorios_ocr/" in conteudo
    assert "diagnosticos_ocr/" in conteudo

import datetime
from pathlib import Path

from exportacao.json_validado import (
    STATUS_DOCUMENTO_EXPORTAVEL,
    montar_payload_exportacao_documento,
)


EXPORT_MARKDOWN_DIR_RELATIVO = Path("exports") / "markdown"


def gerar_nome_arquivo_markdown(documento_id, agora=None):
    momento = agora or datetime.datetime.now()
    timestamp = momento.strftime("%Y%m%d%H%M%S")
    identificador = "".join(c for c in str(documento_id) if c.isdigit()) or "0"
    return f"documento_{identificador}_{timestamp}.md"


def _texto(valor, padrao="-"):
    if valor is None:
        return padrao

    texto = str(valor).strip()
    return texto or padrao


def _mascarar_chave(chave):
    texto = _texto(chave, padrao="")
    if not texto:
        return "-"
    if len(texto) <= 12:
        return texto
    return f"{texto[:6]}...{texto[-6:]}"


def montar_relatorio_markdown_documento(documento):
    payload = montar_payload_exportacao_documento(documento)

    documento_payload = payload["documento"]
    revisao = payload["revisao"]
    integracao = payload["integracao"]
    metadados = payload["metadados"]

    gerado_em = datetime.datetime.now().isoformat(timespec="seconds")
    referencia_json = _texto(metadados.get("json_path"))

    linhas = [
        f"# Relatorio do Documento {documento.get('id')}",
        "",
        "Este relatório é apenas para leitura humana e auditoria operacional. A fonte oficial para integração é o JSON estruturado validado.",
        "",
        "## Identificacao do documento",
        "",
        f"- Documento ID: {_texto(documento.get('id'))}",
        f"- Arquivo: {_texto(metadados.get('arquivo_nome'))}",
        f"- Status do documento: {_texto(documento.get('status'))}",
        f"- Gerado em: {gerado_em}",
        "",
        "## Campos fiscais principais",
        "",
        f"- Empresa: {_texto(documento_payload.get('empresa'))}",
        f"- Numero NF: {_texto(documento_payload.get('numero_nf'))}",
        f"- Chave de acesso resumida: {_mascarar_chave(documento_payload.get('chave_acesso'))}",
        f"- Vencimento: {_texto(documento_payload.get('vencimento'))}",
        f"- Valor total: {_texto(documento_payload.get('valor_total'))}",
        "",
        "## Revisao",
        "",
        f"- Revisado: {_texto(revisao.get('revisado'))}",
        f"- Revisado por: {_texto(revisao.get('revisado_por'))}",
        f"- Revisado em: {_texto(revisao.get('revisado_em'))}",
        "",
        "## Resumo de validacao",
        "",
        f"- Contrato JSON oficial: {_texto(payload.get('versao_contrato'))}",
        f"- Origem: {_texto(payload.get('origem'))}",
        "- Resultado: payload validado com sucesso antes da geracao deste relatorio.",
        f"- Integracao local: status={_texto(integracao.get('status'))}, destino={_texto(integracao.get('destino'))}, modo={_texto(integracao.get('modo'))}",
        f"- Referencia segura ao JSON oficial: {referencia_json}",
        "",
        "## Fora de escopo",
        "",
        "- Nenhuma API foi criada nesta fase.",
        "- Nenhuma integracao externa foi executada nesta fase.",
        "- Este Markdown nao substitui o JSON validado oficial.",
        "",
    ]

    return "\n".join(linhas), payload


def gerar_markdown_documento_revisado(documento_id, obter_documento, root_dir=None, agora=None):
    if not callable(obter_documento):
        raise ValueError("obter_documento deve ser chamável")

    documento = obter_documento(documento_id)
    if not documento:
        return {
            "ok": False,
            "status": "documento_nao_encontrado",
            "caminho_relativo": None,
            "erro": "Documento não encontrado.",
        }

    try:
        markdown, _payload = montar_relatorio_markdown_documento(documento)
        base_dir = Path(root_dir or Path(__file__).resolve().parents[1]).resolve()
        destino_dir = base_dir / EXPORT_MARKDOWN_DIR_RELATIVO
        destino_dir.mkdir(parents=True, exist_ok=True)

        nome_arquivo = gerar_nome_arquivo_markdown(documento.get("id"), agora=agora)
        caminho_arquivo = destino_dir / nome_arquivo
        caminho_arquivo.write_text(markdown, encoding="utf-8")

        caminho_relativo = caminho_arquivo.relative_to(base_dir).as_posix()
        return {
            "ok": True,
            "status": "markdown_gerado_local",
            "caminho_relativo": caminho_relativo,
            "erro": None,
        }
    except ValueError as exc:
        return {
            "ok": False,
            "status": "erro_validacao",
            "caminho_relativo": None,
            "erro": str(exc),
        }
    except Exception:
        return {
            "ok": False,
            "status": "erro_markdown",
            "caminho_relativo": None,
            "erro": "Falha segura na geração local do relatório Markdown.",
        }

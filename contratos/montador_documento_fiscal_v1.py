from contratos.contrato_documento_fiscal_v1 import (
    VERSAO_CONTRATO_DOCUMENTO_FISCAL_V1,
    validar_contrato_documento_fiscal_v1,
)


def montar_payload_documento_fiscal_v1(
    dados_documento,
    destino="fechames_fiscal",
    modo="simulado",
):
    if not isinstance(dados_documento, dict):
        raise ValueError("dados_documento deve ser um dicionario")

    confianca = dados_documento.get("confianca") or {}

    payload = {
        "origem": "OCR-LEITOR",
        "versao_contrato": VERSAO_CONTRATO_DOCUMENTO_FISCAL_V1,
        "documento": {
            "empresa": dados_documento.get("empresa"),
            "numero_nf": dados_documento.get("numero_nf"),
            "chave_acesso": dados_documento.get("chave_acesso"),
            "vencimento": dados_documento.get("vencimento"),
            "valor_total": dados_documento.get("valor_total"),
        },
        "revisao": {
            "revisado": dados_documento.get("revisado", False),
            "revisado_por": dados_documento.get("revisado_por"),
            "revisado_em": dados_documento.get("revisado_em"),
        },
        "confianca": {
            "empresa": confianca.get("empresa"),
            "numero_nf": confianca.get("numero_nf"),
            "chave_acesso": confianca.get("chave_acesso"),
            "vencimento": confianca.get("vencimento"),
            "valor_total": confianca.get("valor_total"),
        },
        "integracao": {
            "status": "pronto_para_destino",
            "destino": destino,
            "modo": modo,
        },
        "metadados": {
            "arquivo_nome": dados_documento.get("arquivo_nome"),
            "json_path": dados_documento.get("json_path"),
            "gerado_em": dados_documento.get("gerado_em"),
        },
    }

    validar_contrato_documento_fiscal_v1(payload)
    return payload

from decimal import Decimal, InvalidOperation


VERSAO_CONTRATO_DOCUMENTO_FISCAL_V1 = "ocr_leitor.documento_fiscal.v1"


def _validar_campo_raiz(payload, campo):
    if campo not in payload:
        raise ValueError(f"campo raiz obrigatorio ausente: {campo}")


def validar_contrato_documento_fiscal_v1(payload):
    if not isinstance(payload, dict):
        raise ValueError("payload deve ser um dicionario")

    for campo in [
        "origem",
        "versao_contrato",
        "documento",
        "revisao",
        "integracao",
        "metadados",
    ]:
        _validar_campo_raiz(payload, campo)

    if payload["origem"] != "OCR-LEITOR":
        raise ValueError("origem deve ser OCR-LEITOR")
    if payload["versao_contrato"] != VERSAO_CONTRATO_DOCUMENTO_FISCAL_V1:
        raise ValueError("versao_contrato invalida")

    revisao = payload["revisao"]
    if not isinstance(revisao, dict):
        raise ValueError("revisao deve ser um dicionario")
    if revisao.get("revisado") is not True:
        raise ValueError("revisao.revisado deve ser True")

    integracao = payload["integracao"]
    if not isinstance(integracao, dict):
        raise ValueError("integracao deve ser um dicionario")
    if not integracao.get("status"):
        raise ValueError("integracao.status e obrigatorio")
    if not integracao.get("modo"):
        raise ValueError("integracao.modo e obrigatorio")

    documento = payload["documento"]
    if not isinstance(documento, dict):
        raise ValueError("documento deve ser um dicionario")
    if not str(documento.get("empresa") or "").strip():
        raise ValueError("documento.empresa e obrigatorio")

    numero_nf = str(documento.get("numero_nf") or "").strip()
    chave_acesso = str(documento.get("chave_acesso") or "").strip()
    if not numero_nf and not chave_acesso:
        raise ValueError("documento.numero_nf ou documento.chave_acesso e obrigatorio")

    if chave_acesso:
        if len(chave_acesso) != 44:
            raise ValueError("documento.chave_acesso deve ter 44 caracteres")
        if not chave_acesso.isdigit():
            raise ValueError("documento.chave_acesso deve conter apenas numeros")

    valor_total = documento.get("valor_total")
    if valor_total not in (None, ""):
        try:
            Decimal(str(valor_total))
        except (InvalidOperation, ValueError):
            raise ValueError("documento.valor_total deve ser convertivel para Decimal")

    return True

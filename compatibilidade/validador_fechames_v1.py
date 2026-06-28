from decimal import Decimal, InvalidOperation

from contratos.contrato_documento_fiscal_v1 import validar_contrato_documento_fiscal_v1


def _relatorio(compativel, erros, destino=None, modo=None):
    return {
        "compativel": compativel,
        "erros": erros,
        "avisos": [],
        "destino": destino,
        "modo": modo,
    }


def validar_compatibilidade_fechames_v1(payload):
    try:
        validar_contrato_documento_fiscal_v1(payload)
    except ValueError as exc:
        return _relatorio(False, [str(exc)])

    documento = payload["documento"]
    revisao = payload["revisao"]
    integracao = payload["integracao"]
    destino = integracao.get("destino")
    modo = integracao.get("modo")
    erros = []

    if destino != "fechames_fiscal":
        erros.append("integracao.destino deve ser fechames_fiscal")
    if modo != "simulado":
        erros.append("integracao.modo deve ser simulado")
    if revisao.get("revisado") is not True:
        erros.append("revisao.revisado deve ser True")
    if not str(documento.get("empresa") or "").strip():
        erros.append("documento.empresa e obrigatorio")

    valor_total = documento.get("valor_total")
    if valor_total in (None, ""):
        erros.append("documento.valor_total e obrigatorio")
    else:
        try:
            Decimal(str(valor_total))
        except (InvalidOperation, ValueError):
            erros.append("documento.valor_total deve ser convertivel para Decimal")

    numero_nf = str(documento.get("numero_nf") or "").strip()
    chave_acesso = str(documento.get("chave_acesso") or "").strip()
    if not numero_nf and not chave_acesso:
        erros.append("documento.numero_nf ou documento.chave_acesso e obrigatorio")

    if chave_acesso:
        if len(chave_acesso) != 44:
            erros.append("documento.chave_acesso deve ter 44 digitos")
        if not chave_acesso.isdigit():
            erros.append("documento.chave_acesso deve conter apenas numeros")

    return _relatorio(
        len(erros) == 0,
        erros,
        destino=destino,
        modo=modo,
    )

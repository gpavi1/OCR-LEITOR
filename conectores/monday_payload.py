"""
CONTRATO-MONDAY-01: Contrato seguro de payload Monday a partir de documento revisado.

Esta fase define apenas a transformacao de dados.
NAO envia nada para Monday.
NAO chama API externa.
Nao le arquivo de configuracao de ambiente.
"""

import re
from typing import Mapping, Tuple, List, Optional

MONDAY_PAYLOAD_VERSION = "monday_payload_revisado.v1"

STATUS_BLOQUEADOS = {"pendente_revisao", "erro_ocr", "recebido", "processando"}
STATUS_APTO = "pendente_integracao"
TIPOS_NFSE = {"nfs-e", "nfse", "nfs", "servico"}


def _texto_ou_none(valor) -> Optional[str]:
    if valor is None:
        return None
    texto = str(valor).strip()
    return texto if texto else None


def _bool_revisado(valor) -> bool:
    return valor is True


def _normalizar_data_iso(valor) -> Optional[str]:
    texto = _texto_ou_none(valor)
    if not texto:
        return None
    padrao_br = re.match(r"^(\d{2})/(\d{2})/(\d{4})$", texto)
    if padrao_br:
        dia, mes, ano = padrao_br.groups()
        return f"{ano}-{mes}-{dia}"
    padrao_iso = re.match(r"^\d{4}-\d{2}-\d{2}$", texto)
    if padrao_iso:
        return texto
    padrao_iso_dt = re.match(r"^(\d{4}-\d{2}-\d{2})", texto)
    if padrao_iso_dt:
        return padrao_iso_dt.group(1)
    return texto


def _normalizar_decimal(valor) -> Optional[str]:
    if valor is None:
        return None
    if isinstance(valor, (int, float)):
        return f"{float(valor):.2f}"
    texto = str(valor).strip()
    if not texto:
        return None
    if re.match(r"^\d{1,3}(\.\d{3})*,\d{2}$", texto):
        return texto.replace(".", "").replace(",", ".")
    if re.match(r"^\d+(\.\d+)?$", texto):
        return f"{float(texto):.2f}"
    try:
        return f"{float(texto):.2f}"
    except (ValueError, TypeError):
        return None


def _montar_item_name(documento: Mapping) -> str:
    empresa = _texto_ou_none(documento.get("empresa")) or "DOCUMENTO"
    nf = _texto_ou_none(documento.get("numero_nf"))
    doc_id = documento.get("id")
    if nf:
        return f"{empresa} - NF {nf}"
    return f"{empresa} - ID {doc_id}"


def validar_documento_apto_monday(documento: Mapping) -> Tuple[bool, List[str], List[str]]:
    bloqueios = []
    avisos = []

    if not isinstance(documento, dict):
        return False, ["Documento invalido: nao pode ser nulo"], []

    if not documento.get("id"):
        bloqueios.append("Documento sem identificador (id).")

    status = _texto_ou_none(documento.get("status"))
    if not status:
        bloqueios.append("Documento sem status.")
    elif status == STATUS_APTO:
        pass
    elif status in STATUS_BLOQUEADOS:
        bloqueios.append(f"Documento em status '{status}' nao pode ser integrado.")
    else:
        bloqueios.append(f"Status '{status}' nao permitido para integracao.")

    if not _bool_revisado(documento.get("revisado")):
        bloqueios.append("Documento nao foi revisado.")

    empresa = _texto_ou_none(documento.get("empresa"))
    if not empresa:
        bloqueios.append("Empresa nao preenchida.")

    numero_nf = _texto_ou_none(documento.get("numero_nf"))
    chave_acesso = _texto_ou_none(documento.get("chave_acesso"))
    tipo_doc = _texto_ou_none(documento.get("tipo_documento"))
    tipo_normalizado = tipo_doc.lower().strip() if tipo_doc else ""

    if not numero_nf and not chave_acesso:
        bloqueios.append("Numero NF e chave de acesso ambos vazios.")

    if tipo_normalizado in TIPOS_NFSE:
        if not numero_nf:
            bloqueios.append("NFS-e sem numero NF.")
        if not chave_acesso:
            avisos.append("Chave de acesso vazia (NFS-e).")
    else:
        if not numero_nf and chave_acesso:
            bloqueios.append("Numero NF vazio.")
        if not chave_acesso and numero_nf:
            bloqueios.append("Chave de acesso vazia.")

    if not _texto_ou_none(documento.get("valor_total")):
        avisos.append("Valor total vazio.")
    if not _texto_ou_none(documento.get("vencimento")):
        avisos.append("Vencimento vazio.")
    if not _texto_ou_none(documento.get("observacao_revisao")):
        avisos.append("Observacao da revisao vazia.")
    if not _texto_ou_none(documento.get("json_path")):
        avisos.append("Caminho do JSON vazio.")

    apto = len(bloqueios) == 0
    return apto, bloqueios, avisos


def normalizar_documento_para_monday(documento: Mapping) -> dict:
    if not isinstance(documento, dict):
        raise ValueError("documento deve ser um dicionario")

    apto, bloqueios, avisos = validar_documento_apto_monday(documento)

    campos = {
        "empresa": _texto_ou_none(documento.get("empresa")),
        "numero_nf": _texto_ou_none(documento.get("numero_nf")),
        "chave_acesso": _texto_ou_none(documento.get("chave_acesso")),
        "vencimento": _normalizar_data_iso(documento.get("vencimento")),
        "valor_total": _normalizar_decimal(documento.get("valor_total")),
        "arquivo_nome": _texto_ou_none(documento.get("arquivo_nome")),
        "status": _texto_ou_none(documento.get("status")),
        "revisado": _bool_revisado(documento.get("revisado")),
        "revisado_por": _texto_ou_none(documento.get("revisado_por")),
        "revisado_em": _texto_ou_none(documento.get("revisado_em")),
        "observacao_revisao": _texto_ou_none(documento.get("observacao_revisao")),
        "json_path": _texto_ou_none(documento.get("json_path")),
        "tipo_documento": _texto_ou_none(documento.get("tipo_documento")),
    }

    return {
        "versao": MONDAY_PAYLOAD_VERSION,
        "origem": "ocr-leitor.documentos",
        "documento_id": documento.get("id"),
        "cliente_id": documento.get("cliente_id"),
        "item_name": _montar_item_name(documento),
        "apto_envio": apto,
        "bloqueios": bloqueios,
        "avisos": avisos,
        "campos": campos,
        "metadados": {
            "integracao": "monday",
            "envio_real": False,
            "requer_confirmacao_humana": True,
        },
    }


def montar_column_values_monday(payload: Mapping, mapa_colunas: Mapping) -> dict:
    if not isinstance(mapa_colunas, dict):
        raise ValueError("mapa_colunas deve ser um dicionario")
    if not isinstance(payload, dict):
        raise ValueError("payload deve ser um dicionario")

    campos = payload.get("campos", {})
    if not isinstance(campos, dict):
        return {}

    valores = {}
    mapeamento = {
        "empresa": "empresa",
        "numero_nf": "numero_nf",
        "chave_acesso": "chave_acesso",
        "vencimento": "vencimento",
        "valor_total": "valor_total",
        "observacao_revisao": "observacao_revisao",
    }

    for campo_logico, campo_fonte in mapeamento.items():
        col_id = mapa_colunas.get(campo_logico)
        if not col_id:
            continue
        valor = campos.get(campo_fonte)
        if valor is None:
            continue
        if campo_logico == "vencimento":
            valores[col_id] = {"date": valor}
        else:
            valores[col_id] = str(valor)

    return valores

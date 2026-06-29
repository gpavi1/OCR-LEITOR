"""
MONDAY-DRYRUN-01: Simulacao segura de envio para Monday sem chamada externa.

Usa conectores/monday_payload.py para montar payload e column_values.
Nao envia nada para Monday.
Nao chama API externa.
Nao le arquivo de configuracao de ambiente.
"""

from typing import Mapping, Optional
from conectores.monday_payload import (
    normalizar_documento_para_monday,
    montar_column_values_monday,
)

DRYRUN_VERSION = "monday_dryrun.v1"

MAPA_PADRAO_DRYRUN = {
    "empresa": "dryrun_empresa",
    "numero_nf": "dryrun_numero_nf",
    "chave_acesso": "dryrun_chave_acesso",
    "vencimento": "dryrun_vencimento",
    "valor_total": "dryrun_valor_total",
    "observacao_revisao": "dryrun_observacao",
}


def gerar_dryrun_monday(
    documento: Mapping,
    mapa_colunas: Optional[Mapping] = None,
) -> dict:
    if mapa_colunas is None:
        mapa_colunas = MAPA_PADRAO_DRYRUN

    payload = normalizar_documento_para_monday(documento)

    if not payload["apto_envio"]:
        return {
            "tipo": "monday_dryrun",
            "versao": DRYRUN_VERSION,
            "envio_real": False,
            "status": "bloqueado",
            "documento_id": documento.get("id"),
            "item_name": payload.get("item_name"),
            "payload": payload,
            "column_values": {},
            "bloqueios": payload.get("bloqueios", []),
            "avisos": payload.get("avisos", []),
            "mensagem": (
                "Documento bloqueado para dry-run. "
                "Corrija os bloqueios antes de tentar novamente."
            ),
        }

    column_values = montar_column_values_monday(payload, mapa_colunas)

    return {
        "tipo": "monday_dryrun",
        "versao": DRYRUN_VERSION,
        "envio_real": False,
        "documento_id": documento.get("id"),
        "item_name": payload.get("item_name"),
        "payload": payload,
        "column_values": column_values,
        "bloqueios": [],
        "avisos": payload.get("avisos", []),
        "status": "apto",
        "mensagem": (
            "Dry-run concluido. "
            "Documento apto para envio futuro ao Monday."
        ),
    }

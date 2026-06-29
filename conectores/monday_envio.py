"""
MONDAY-ENVIO-APROVADO-01: Envio real controlado de 1 documento revisado para Monday.

Nao le arquivo de variaveis de ambiente.
Nao usa dados reais como default.
Nao implementa lote.
Nao implementa file attach.
"""

import json
from typing import Callable, Mapping, Optional

from conectores.monday_payload import (
    normalizar_documento_para_monday,
    montar_column_values_monday,
)

ENVIO_VERSION = "monday_envio_aprovado.v1"
MONDAY_API_URL = "https://api.monday.com/v2"

COLUNAS_OBRIGATORIAS = {
    "empresa",
    "numero_nf",
    "chave_acesso",
    "vencimento",
    "valor_total",
    "observacao_revisao",
}

MUTATION_CREATE_ITEM = """
mutation createItem($board_id: ID!, $item_name: String!) {
  create_item(board_id: $board_id, item_name: $item_name) {
    id
    name
  }
}
"""

MUTATION_UPDATE_COLUMNS = """
mutation updateColumns($board_id: ID!, $item_id: ID!, $column_values: JSON!) {
  change_multiple_column_values(
    board_id: $board_id,
    item_id: $item_id,
    column_values: $column_values
  ) {
    id
  }
}
"""


def _executar_mutation(
    query: str,
    variables: dict,
    token: str,
    post_func: Optional[Callable] = None,
    timeout: int = 30,
) -> dict:
    headers = {
        "Authorization": token,
        "Content-Type": "application/json",
    }
    payload = {"query": query, "variables": variables}

    if post_func is not None:
        resposta = post_func(MONDAY_API_URL, json=payload, headers=headers, timeout=timeout)
    else:
        import requests
        resposta = requests.post(
            MONDAY_API_URL, json=payload, headers=headers, timeout=timeout
        )

    dados = resposta.json()

    if "errors" in dados:
        return {"ok": False, "erro": str(dados["errors"])}

    return {"ok": True, "dados": dados}


def _validar_config(token: str, board_id: str, mapa_colunas: Mapping) -> list:
    bloqueios = []
    if not token or not isinstance(token, str) or not token.strip():
        bloqueios.append("Token Monday ausente ou invalido.")
    if not board_id or not isinstance(board_id, str) or not board_id.strip():
        bloqueios.append("Board ID Monday ausente ou invalido.")
    if not isinstance(mapa_colunas, dict):
        bloqueios.append("Mapa de colunas Monday ausente ou invalido.")
    else:
        for chave in COLUNAS_OBRIGATORIAS:
            if chave not in mapa_colunas or not mapa_colunas[chave]:
                bloqueios.append(f"Coluna '{chave}' nao configurada no mapa.")
    return bloqueios


def enviar_documento_monday(
    documento: Mapping,
    token: str,
    board_id: str,
    mapa_colunas: Mapping,
    post_func: Optional[Callable] = None,
    timeout: int = 30,
) -> dict:
    payload = normalizar_documento_para_monday(documento)

    if not payload["apto_envio"]:
        return {
            "tipo": "monday_envio_aprovado",
            "versao": ENVIO_VERSION,
            "envio_real": True,
            "status": "bloqueado",
            "documento_id": documento.get("id"),
            "item_id": None,
            "item_name": payload.get("item_name"),
            "payload": payload,
            "column_values": {},
            "bloqueios": payload.get("bloqueios", []),
            "avisos": payload.get("avisos", []),
            "erro": None,
            "mensagem": "Documento nao apto para envio.",
        }

    config_bloqueios = _validar_config(token, board_id, mapa_colunas)
    if config_bloqueios:
        return {
            "tipo": "monday_envio_aprovado",
            "versao": ENVIO_VERSION,
            "envio_real": True,
            "status": "bloqueado",
            "documento_id": documento.get("id"),
            "item_id": None,
            "item_name": payload.get("item_name"),
            "payload": payload,
            "column_values": {},
            "bloqueios": config_bloqueios,
            "avisos": payload.get("avisos", []),
            "erro": "; ".join(config_bloqueios),
            "mensagem": "Configuracao Monday incompleta.",
        }

    column_values = montar_column_values_monday(payload, mapa_colunas)
    item_name = payload["item_name"]

    try:
        resultado_create = _executar_mutation(
            MUTATION_CREATE_ITEM,
            {"board_id": board_id, "item_name": item_name},
            token,
            post_func=post_func,
            timeout=timeout,
        )

        if not resultado_create["ok"]:
            return {
                "tipo": "monday_envio_aprovado",
                "versao": ENVIO_VERSION,
                "envio_real": True,
                "status": "falha",
                "documento_id": documento.get("id"),
                "item_id": None,
                "item_name": item_name,
                "payload": payload,
                "column_values": column_values,
                "bloqueios": [],
                "avisos": payload.get("avisos", []),
                "erro": resultado_create.get("erro", "Falha ao criar item no Monday."),
                "mensagem": "Item nao foi criado no Monday.",
            }

        item_id = resultado_create["dados"]["data"]["create_item"]["id"]

        column_values_json = json.dumps(column_values, ensure_ascii=False)
        resultado_update = _executar_mutation(
            MUTATION_UPDATE_COLUMNS,
            {
                "board_id": board_id,
                "item_id": item_id,
                "column_values": column_values_json,
            },
            token,
            post_func=post_func,
            timeout=timeout,
        )

        if not resultado_update["ok"]:
            return {
                "tipo": "monday_envio_aprovado",
                "versao": ENVIO_VERSION,
                "envio_real": True,
                "status": "falha",
                "documento_id": documento.get("id"),
                "item_id": item_id,
                "item_name": item_name,
                "payload": payload,
                "column_values": column_values,
                "bloqueios": [],
                "avisos": payload.get("avisos", []),
                "erro": resultado_update.get("erro", "Falha ao atualizar colunas no Monday."),
                "mensagem": "Item criado, mas colunas nao foram preenchidas.",
            }

        return {
            "tipo": "monday_envio_aprovado",
            "versao": ENVIO_VERSION,
            "envio_real": True,
            "status": "sucesso",
            "documento_id": documento.get("id"),
            "item_id": item_id,
            "item_name": item_name,
            "payload": payload,
            "column_values": column_values,
            "bloqueios": [],
            "avisos": payload.get("avisos", []),
            "erro": None,
            "mensagem": f"Documento enviado ao Monday. Item ID: {item_id}",
        }

    except Exception as exc:
        return {
            "tipo": "monday_envio_aprovado",
            "versao": ENVIO_VERSION,
            "envio_real": True,
            "status": "falha",
            "documento_id": documento.get("id"),
            "item_id": None,
            "item_name": item_name,
            "payload": payload,
            "column_values": column_values,
            "bloqueios": [],
            "avisos": payload.get("avisos", []),
            "erro": str(exc),
            "mensagem": "Excecao local durante envio Monday.",
        }

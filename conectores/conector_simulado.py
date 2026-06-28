import json
import re
from pathlib import Path

from contratos.contrato_documento_fiscal_v1 import validar_contrato_documento_fiscal_v1


PREFIXO_ARQUIVO = "ocr_leitor_documento_fiscal_v1_"


def gerar_nome_arquivo_simulado(payload):
    documento = payload.get("documento") or {}
    numero_nf = str(documento.get("numero_nf") or "").strip()
    chave_acesso = str(documento.get("chave_acesso") or "").strip()

    if numero_nf:
        identificador = f"nf_{numero_nf}"
    elif chave_acesso:
        identificador = f"chave_{chave_acesso}"
    else:
        identificador = "documento"

    identificador = re.sub(r"[^A-Za-z0-9_-]+", "_", identificador).strip("_").lower()
    return f"{PREFIXO_ARQUIVO}{identificador or 'documento'}.json"


def exportar_json_simulado(payload, destino_dir):
    validar_contrato_documento_fiscal_v1(payload)

    if (payload.get("integracao") or {}).get("modo") != "simulado":
        raise ValueError("conector simulado aceita apenas modo simulado")

    destino = Path(destino_dir)
    destino.mkdir(parents=True, exist_ok=True)

    caminho = destino / gerar_nome_arquivo_simulado(payload)
    caminho.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    return str(caminho)

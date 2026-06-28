import json
import re
from pathlib import Path


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
    if not isinstance(payload, dict):
        raise ValueError("payload deve ser um dicionario")
    if payload.get("origem") != "OCR-LEITOR":
        raise ValueError("origem invalida para o conector simulado")
    if payload.get("versao_contrato") != "ocr_leitor.documento_fiscal.v1":
        raise ValueError("versao_contrato invalida para o conector simulado")
    if (payload.get("revisao") or {}).get("revisado") is not True:
        raise ValueError("documento precisa estar revisado")
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

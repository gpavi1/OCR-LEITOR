"""
OCR-S1 — pipeline seguro para gerar JSON padrão e registrar controle em MySQL.

Este arquivo NÃO envia nada para Monday. Ele preserva o OCR atual e cria a base
para produto/SaaS: cliente_id, JSON padronizado, status e histórico no banco.
"""

import argparse
import json
import os
import shutil
import sys
from pathlib import Path
from typing import Optional

import pytesseract
from PIL import Image

from exporters.json_exporter import salvar_json
from models.documento_extraido import data_br_para_iso, montar_documento_fiscal
from parser_nf import parse_ocr
from utils.file_hash import sha256_file

BASE_DIR = Path(__file__).resolve().parent
CONFIG_PATH = BASE_DIR / "config" / "settings.json"
INPUT_FOLDER = BASE_DIR / "input"
PROCESSED_FOLDER = BASE_DIR / "processed"
ERROR_FOLDER = BASE_DIR / "erro"
OUTPUT_JSON_FOLDER = BASE_DIR / "output" / "json"


def carregar_config() -> dict:
    if not CONFIG_PATH.exists():
        return {}
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def configurar_tesseract(config: dict) -> str:
    tesseract_path = config.get("tesseract_path") or r"C:\Program Files\Tesseract-OCR\tesseract.exe"
    if tesseract_path and os.path.exists(tesseract_path):
        pytesseract.pytesseract.tesseract_cmd = tesseract_path
    idioma = config.get("ocr", {}).get("language", "por+eng")
    return "por+eng" if idioma == "por" else idioma


def extract_text(image_path: str, idioma: str) -> str:
    img = Image.open(image_path)
    return pytesseract.image_to_string(img, lang=idioma)


def move_unique(src: str, folder: Path) -> str:
    folder.mkdir(parents=True, exist_ok=True)
    src_path = Path(src)
    dest = folder / src_path.name
    contador = 1
    while dest.exists():
        dest = folder / f"{src_path.stem}_{contador}{src_path.suffix}"
        contador += 1
    shutil.move(str(src_path), str(dest))
    return str(dest)


def registrar_recebido_mysql(cliente_id: int, arquivo_nome: str, arquivo_origem: str, arquivo_hash: str) -> Optional[int]:
    try:
        from database.documentos_repo import criar_documento_recebido, marcar_processando

        documento_id = criar_documento_recebido(cliente_id, arquivo_nome, arquivo_origem, arquivo_hash)
        marcar_processando(documento_id)
        return documento_id
    except Exception as exc:
        print(f"⚠️ MySQL indisponível ou não configurado. JSON será gerado mesmo assim. Motivo: {exc}")
        return None


def atualizar_mysql_sucesso(documento_id: Optional[int], doc_json: dict, json_path: str, arquivo_destino: Optional[str]) -> None:
    if not documento_id:
        return
    try:
        from database.documentos_repo import atualizar_documento_extraido

        documento = doc_json["documento"]
        status_banco = "pendente_integracao" if doc_json["status"] == "sucesso" else "pendente_revisao"
        atualizar_documento_extraido(
            documento_id=documento_id,
            tipo_documento=documento["tipo"],
            empresa=documento["empresa"]["valor"],
            numero_nf=documento["numero_nf"]["valor"],
            chave_acesso=documento["chave_acesso"]["valor"],
            vencimento_iso=documento["vencimento"]["valor"],
            valor_total=documento["valor_total"]["valor"],
            json_path=json_path,
            status=status_banco,
            arquivo_destino=arquivo_destino,
        )
    except Exception as exc:
        print(f"⚠️ Não foi possível atualizar o MySQL após extração: {exc}")


def marcar_mysql_erro(documento_id: Optional[int], status: str, erro: str) -> None:
    if not documento_id:
        return
    try:
        from database.documentos_repo import marcar_erro

        marcar_erro(documento_id, status, erro)
    except Exception as exc:
        print(f"⚠️ Não foi possível registrar erro no MySQL: {exc}")


def processar_arquivo(caminho: str, cliente_id: int, mover: bool = True) -> bool:
    config = carregar_config()
    idioma = configurar_tesseract(config)

    path = Path(caminho)
    if not path.exists():
        print(f"❌ Arquivo não encontrado: {path}")
        return False

    arquivo_hash = sha256_file(str(path))
    documento_id = registrar_recebido_mysql(cliente_id, path.name, str(path), arquivo_hash)

    try:
        print(f"🔍 OCR-S1 processando: {path.name}")
        texto = extract_text(str(path), idioma)
        parsed = parse_ocr(texto)

        arquivo_destino = None
        doc = montar_documento_fiscal(
            cliente_id=cliente_id,
            parsed=parsed,
            texto_extraido=texto,
            arquivo_nome=path.name,
            arquivo_origem=str(path),
            arquivo_hash=arquivo_hash,
            arquivo_destino=arquivo_destino,
            idiomas=idioma.split("+"),
        )
        doc_json = doc.to_dict()
        json_path = salvar_json(doc_json, str(OUTPUT_JSON_FOLDER), path.name)

        if mover:
            destino = PROCESSED_FOLDER if doc_json["status"] == "sucesso" else ERROR_FOLDER
            arquivo_destino = move_unique(str(path), destino)
            doc_json["arquivo"]["destino"] = arquivo_destino
            json_path = salvar_json(doc_json, str(OUTPUT_JSON_FOLDER), path.name)

        atualizar_mysql_sucesso(documento_id, doc_json, json_path, arquivo_destino)

        print(f"✅ JSON gerado: {json_path}")
        print(f"📌 Status OCR: {doc_json['status']}")
        return doc_json["status"] == "sucesso"

    except Exception as exc:
        marcar_mysql_erro(documento_id, "erro_ocr", str(exc))
        if mover and path.exists():
            move_unique(str(path), ERROR_FOLDER)
        print(f"❌ Erro no processamento: {exc}")
        return False


def processar_input(cliente_id: int, mover: bool = True) -> None:
    INPUT_FOLDER.mkdir(exist_ok=True)
    arquivos = [
        p for p in INPUT_FOLDER.iterdir()
        if p.suffix.lower() in (".png", ".jpg", ".jpeg")
    ]
    print(f"📦 Arquivos encontrados: {len(arquivos)}")
    for arquivo in arquivos:
        processar_arquivo(str(arquivo), cliente_id=cliente_id, mover=mover)


def main() -> int:
    parser = argparse.ArgumentParser(description="OCR-S1: JSON padrão + MySQL de controle")
    parser.add_argument("--cliente-id", type=int, default=1, help="ID do cliente no MySQL")
    parser.add_argument("--arquivo", type=str, default=None, help="Processar apenas um arquivo")
    parser.add_argument("--no-move", action="store_true", help="Não mover arquivos para processed/erro")
    args = parser.parse_args()

    if args.arquivo:
        ok = processar_arquivo(args.arquivo, cliente_id=args.cliente_id, mover=not args.no_move)
        return 0 if ok else 1

    processar_input(cliente_id=args.cliente_id, mover=not args.no_move)
    return 0


if __name__ == "__main__":
    sys.exit(main())

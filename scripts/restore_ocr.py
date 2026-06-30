import argparse
import json
import shutil
import zipfile
from datetime import datetime
from pathlib import Path


TIPO_MANIFEST = "ocr_leitor_backup"
CONFIRMACAO_OBRIGATORIA = "RESTAURAR BACKUP"
PASTAS_RESTAURAVEIS = {"input", "output", "processed", "erro", "logs", "exports"}
PREFIXO_ARQUIVOS = "arquivos/"


def agora_nome():
    return datetime.now().strftime("%Y%m%d-%H%M%S")


def caminho_zip_normalizado(nome):
    return nome.replace("\\", "/")


def validar_manifest(zf):
    if "manifest.json" not in zf.namelist():
        raise ValueError("Backup sem manifest.json.")
    manifest = json.loads(zf.read("manifest.json").decode("utf-8"))
    if manifest.get("tipo") != TIPO_MANIFEST:
        raise ValueError("Manifest de backup invalido.")
    return manifest


def entrada_restauravel(nome):
    nome = caminho_zip_normalizado(nome)
    if nome.endswith("/"):
        return False
    if ".." in Path(nome).parts:
        return False
    if nome.startswith(".env") or "/.env" in nome:
        return False
    if ".venv" in Path(nome).parts:
        return False
    if "backups" in Path(nome).parts:
        return False
    if not nome.startswith(PREFIXO_ARQUIVOS):
        return False
    partes = nome.split("/")
    return len(partes) >= 3 and partes[1] in PASTAS_RESTAURAVEIS


def destino_para_entrada(destino, nome):
    rel = caminho_zip_normalizado(nome)[len(PREFIXO_ARQUIVOS):]
    return Path(destino) / Path(rel)


def analisar_backup(backup_path):
    backup_path = Path(backup_path)
    with zipfile.ZipFile(backup_path, "r") as zf:
        manifest = validar_manifest(zf)
        entradas = [nome for nome in zf.namelist() if entrada_restauravel(nome)]
        banco_disponivel = "database/dados.json" in zf.namelist()
    return {
        "manifest": manifest,
        "entradas_restauraveis": entradas,
        "banco_disponivel": banco_disponivel,
    }


def criar_backup_seguranca(destino, entradas):
    destino = Path(destino)
    backup_dir = destino / "backups" / f"restore-seguranca-{agora_nome()}"
    backup_dir.mkdir(parents=True, exist_ok=True)
    manifest = []
    for nome in entradas:
        alvo = destino_para_entrada(destino, nome)
        if not alvo.exists() or not alvo.is_file():
            continue
        rel = alvo.relative_to(destino)
        copia = backup_dir / rel
        copia.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(alvo, copia)
        manifest.append(str(rel).replace("\\", "/"))
    (backup_dir / "manifest_restore_seguranca.json").write_text(
        json.dumps({"arquivos_preservados": manifest}, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    return backup_dir


def restaurar_arquivos(backup_path, destino, entradas):
    destino = Path(destino)
    with zipfile.ZipFile(backup_path, "r") as zf:
        for nome in entradas:
            alvo = destino_para_entrada(destino, nome)
            alvo.parent.mkdir(parents=True, exist_ok=True)
            with zf.open(nome) as origem, alvo.open("wb") as saida:
                shutil.copyfileobj(origem, saida)


def imprimir_analise(analise, destino, restaurar_arquivos_flag, restaurar_banco_flag, dry_run):
    modo = "DRY-RUN" if dry_run else "RESTORE"
    print(f"OCR-LEITOR - {modo} de backup")
    print(f"Destino: {destino}")
    print(f"Entradas restauraveis: {len(analise['entradas_restauraveis'])}")
    for entrada in analise["entradas_restauraveis"]:
        print(f"Arquivo: {entrada}")
    if restaurar_arquivos_flag:
        print("Arquivos operacionais: selecionados")
    else:
        print("Arquivos operacionais: nao selecionados")
    if restaurar_banco_flag:
        print("Banco: solicitado, mas restore real de banco esta bloqueado nesta fase")
    else:
        print("Banco: nao selecionado")


def criar_parser():
    parser = argparse.ArgumentParser(description="Restore operacional seguro do OCR-LEITOR")
    parser.add_argument("--backup", required=True)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--confirmar", action="store_true")
    parser.add_argument("--confirmacao", default="")
    parser.add_argument("--destino")
    parser.add_argument("--restaurar-arquivos", action="store_true")
    parser.add_argument("--restaurar-banco", action="store_true")
    parser.add_argument("--project-root")
    return parser


def main(argv=None):
    args = criar_parser().parse_args(argv)
    backup_path = Path(args.backup).resolve()
    destino = Path(args.destino or args.project_root or Path(__file__).resolve().parents[1]).resolve()

    try:
        analise = analisar_backup(backup_path)
    except Exception as exc:
        print(f"ERRO: {exc}")
        return 1

    dry_run = args.dry_run or not args.confirmar
    imprimir_analise(analise, destino, args.restaurar_arquivos, args.restaurar_banco, dry_run=dry_run)

    if dry_run:
        print("Nenhum arquivo foi restaurado.")
        return 0

    if args.confirmacao != CONFIRMACAO_OBRIGATORIA:
        print(f"ERRO: confirmacao textual obrigatoria: {CONFIRMACAO_OBRIGATORIA}")
        return 1

    if args.restaurar_banco:
        print("ERRO: restore real de banco ainda bloqueado nesta fase. Use dry-run para validar o backup.")
        return 2

    if not args.restaurar_arquivos:
        print("ERRO: selecione --restaurar-arquivos para restaurar pastas operacionais.")
        return 1

    backup_seguranca = criar_backup_seguranca(destino, analise["entradas_restauraveis"])
    restaurar_arquivos(backup_path, destino, analise["entradas_restauraveis"])
    print(f"Backup de seguranca criado em: {backup_seguranca}")
    print("Restore de arquivos operacionais concluido.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

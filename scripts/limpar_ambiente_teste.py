import argparse
import datetime
import shutil
from pathlib import Path


PASTAS_OPERACIONAIS = [
    Path("input"),
    Path("processed"),
    Path("erro"),
    Path("output") / "json",
    Path("exports") / "json",
    Path("exports") / "markdown",
]
BACKUP_DIR = Path("_backup_testes")
ARQUIVOS_VERSIONADOS_PRESERVADOS = {".gitkeep", ".keep"}


def detectar_raiz_projeto():
    return Path(__file__).resolve().parents[1]


def validar_raiz_projeto(base_dir):
    base = Path(base_dir).resolve()
    verificacoes = [
        base.name == "OCR-LEITOR",
        (base / "ocr_pipeline_s1.py").is_file(),
        (base / "scripts").is_dir(),
        (base / "web" / "app.py").is_file(),
    ]
    if not all(verificacoes):
        raise ValueError("Raiz do projeto OCR-LEITOR não validada.")
    return base


def _criar_backup_dir(base_dir, agora=None):
    momento = agora or datetime.datetime.now()
    timestamp = momento.strftime("%Y%m%d_%H%M%S")
    return Path(base_dir) / BACKUP_DIR / f"limpeza_{timestamp}"


def _destino_unico(destino):
    destino = Path(destino)
    if not destino.exists():
        return destino

    contador = 1
    while True:
        candidato = destino.with_name(f"{destino.stem}_{contador}{destino.suffix}")
        if not candidato.exists():
            return candidato
        contador += 1


def _item_movivel(path):
    return path.name not in ARQUIVOS_VERSIONADOS_PRESERVADOS


def limpar_ambiente_teste(base_dir=None, dry_run=False, agora=None, validar_raiz=True):
    base = Path(base_dir) if base_dir is not None else detectar_raiz_projeto()
    base = validar_raiz_projeto(base) if validar_raiz else Path(base).resolve()
    backup_dir = _criar_backup_dir(base, agora=agora)

    resumo = {
        "dry_run": dry_run,
        "base_dir": str(base),
        "backup_dir": str(backup_dir),
        "pastas_verificadas": [],
        "arquivos_movidos": [],
        "arquivos_preservados": [],
        "avisos": [
            "Banco MySQL não foi alterado.",
            "OCR/parser/core não foram executados nem alterados.",
        ],
    }

    for pasta_relativa in PASTAS_OPERACIONAIS:
        pasta = base / pasta_relativa
        resumo["pastas_verificadas"].append(str(pasta_relativa).replace("\\", "/"))

        if not dry_run:
            pasta.mkdir(parents=True, exist_ok=True)

        if not pasta.exists():
            continue

        for item in sorted(pasta.iterdir(), key=lambda p: p.name.lower()):
            if not _item_movivel(item):
                resumo["arquivos_preservados"].append(str(item.relative_to(base)).replace("\\", "/"))
                continue

            destino_base = backup_dir / pasta_relativa
            destino = _destino_unico(destino_base / item.name)

            if not dry_run:
                destino.parent.mkdir(parents=True, exist_ok=True)
                shutil.move(str(item), str(destino))

            resumo["arquivos_movidos"].append({
                "origem": str(item.relative_to(base)).replace("\\", "/"),
                "destino": str(destino.relative_to(base)).replace("\\", "/"),
            })

    return resumo


def imprimir_resumo(resumo):
    modo = "DRY-RUN" if resumo["dry_run"] else "LIMPEZA REAL"
    print("OCR-LEITOR - Limpeza segura do ambiente de testes")
    print("=" * 52)
    print(f"Modo: {modo}")
    print(f"Backup: {resumo['backup_dir']}")
    print(f"Pastas verificadas: {len(resumo['pastas_verificadas'])}")
    for pasta in resumo["pastas_verificadas"]:
        print(f"- {pasta}")
    print(f"Arquivos movidos: {len(resumo['arquivos_movidos'])}")
    for item in resumo["arquivos_movidos"]:
        acao = "moveria" if resumo["dry_run"] else "movido"
        print(f"- {acao}: {item['origem']} -> {item['destino']}")
    for aviso in resumo["avisos"]:
        print(f"AVISO: {aviso}")


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Limpeza segura do ambiente de testes do OCR-LEITOR"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Simula a limpeza sem mover arquivos",
    )
    args = parser.parse_args(argv)

    try:
        resumo = limpar_ambiente_teste(dry_run=args.dry_run)
    except ValueError as exc:
        print(f"ERRO: {exc}")
        return 1

    imprimir_resumo(resumo)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

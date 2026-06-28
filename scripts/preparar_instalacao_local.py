import argparse
from pathlib import Path


PASTAS_OPERACIONAIS = ["input", "output", "processed", "erro", "logs", "config"]


def detectar_base_dir():
    return Path(__file__).resolve().parents[1]


def resultado(acao, alvo, detalhe=""):
    return {
        "acao": acao,
        "alvo": str(alvo),
        "detalhe": detalhe,
    }


def preparar_pastas(base_dir, confirmar=False):
    base = Path(base_dir)
    resultados = []

    for nome_pasta in PASTAS_OPERACIONAIS:
        pasta = base / nome_pasta
        if pasta.is_dir():
            resultados.append(resultado("OK", pasta, "pasta ja existe"))
            continue

        if confirmar:
            pasta.mkdir(parents=True, exist_ok=True)
            resultados.append(resultado("CRIADO", pasta, "pasta criada"))
        else:
            resultados.append(resultado("CRIAR", pasta, "dry-run: pasta seria criada"))

    return resultados


def verificar_arquivos_locais(base_dir):
    base = Path(base_dir)
    resultados = []

    env_path = base / ".env"
    if env_path.is_file():
        resultados.append(resultado("OK", env_path, "arquivo local encontrado"))
    else:
        resultados.append(resultado("AVISO", env_path, "arquivo .env local ausente"))

    settings_path = base / "config" / "settings.json"
    if settings_path.is_file():
        resultados.append(resultado("OK", settings_path, "arquivo local encontrado"))
    else:
        resultados.append(resultado("AVISO", settings_path, "config/settings.json ausente"))

    return resultados


def imprimir_relatorio(resultados):
    print("OCR-LEITOR - Preparacao local")
    print("=" * 31)
    for item in resultados:
        detalhe = f" - {item['detalhe']}" if item.get("detalhe") else ""
        print(f"[{item['acao']}] {item['alvo']}{detalhe}")


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Preparacao local segura do OCR-LEITOR"
    )
    parser.add_argument("--base-dir", default=None, help="Pasta base do OCR-LEITOR")
    parser.add_argument(
        "--confirmar",
        action="store_true",
        help="Cria apenas as pastas operacionais seguras",
    )
    args = parser.parse_args(argv)

    base_dir = Path(args.base_dir) if args.base_dir else detectar_base_dir()
    if not base_dir.exists():
        imprimir_relatorio([
            resultado("ERRO", base_dir, "base-dir nao existe")
        ])
        return 1

    resultados = []
    if not args.confirmar:
        resultados.append(resultado("AVISO", base_dir, "modo dry-run: nada sera alterado"))
    resultados.extend(preparar_pastas(base_dir, confirmar=args.confirmar))
    resultados.extend(verificar_arquivos_locais(base_dir))

    imprimir_relatorio(resultados)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

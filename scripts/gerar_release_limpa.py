import argparse
import subprocess
import sys
from pathlib import Path


NOME_ZIP_PADRAO = "OCR-LEITOR-RELEASE-LIMPA.zip"
DESTINO_DIR_PADRAO = "dist"


def detectar_base_dir():
    return Path(__file__).resolve().parents[1]


def resultado(acao, alvo, detalhe=""):
    return {"acao": acao, "alvo": str(alvo), "detalhe": detalhe}


def validar_nome_zip(nome):
    if not nome.endswith(".zip"):
        return False, "nome do zip deve terminar com .zip"
    for char in ("/", "\\", ":"):
        if char in nome:
            return False, "nome do zip nao pode conter separador de caminho"
    if nome.startswith(".."):
        return False, "nome do zip nao pode conter parent dir"
    return True, ""


def executar_comando_git(args, base_dir):
    return subprocess.run(
        ["git", *args],
        cwd=str(base_dir),
        capture_output=True,
        text=True,
        timeout=30,
    )


def verificar_repositorio_git(base_dir):
    try:
        result = executar_comando_git(["rev-parse", "--git-dir"], base_dir)
        return result.returncode == 0
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return False


def interpretar_worktree_limpo(porcelain_output):
    return porcelain_output.strip() == ""


def verificar_worktree_limpo(base_dir):
    result = executar_comando_git(["status", "--porcelain"], base_dir)
    limpo = interpretar_worktree_limpo(result.stdout)
    return limpo, result.stdout


def gerar_zip_git_archive(base_dir, destino_zip):
    destino_zip = Path(destino_zip)
    destino_zip.parent.mkdir(parents=True, exist_ok=True)
    result = executar_comando_git(
        ["archive", "--format=zip", "-o", str(destino_zip), "HEAD"],
        base_dir,
    )
    if result.returncode != 0:
        raise RuntimeError(
            f"falha ao gerar archive git: {result.stderr.strip()}"
        )
    return destino_zip


def imprimir_relatorio(resultados):
    print("OCR-LEITOR - Release limpa")
    print("=" * 24)
    for item in resultados:
        detalhe = f" - {item['detalhe']}" if item.get("detalhe") else ""
        print(f"[{item['acao']}] {item['alvo']}{detalhe}")


def main(argv=None):
    parser = argparse.ArgumentParser(
        description="Gera release limpa do OCR-LEITOR via git archive"
    )
    parser.add_argument(
        "--confirmar",
        action="store_true",
        help="Gera o ZIP release",
    )
    parser.add_argument(
        "--base-dir",
        default=None,
        help="Pasta raiz do OCR-LEITOR",
    )
    parser.add_argument(
        "--destino-dir",
        default=DESTINO_DIR_PADRAO,
        help=f"Pasta de destino (padrao: {DESTINO_DIR_PADRAO})",
    )
    parser.add_argument(
        "--nome",
        default=NOME_ZIP_PADRAO,
        help=f"Nome do ZIP (padrao: {NOME_ZIP_PADRAO})",
    )
    args = parser.parse_args(argv)

    base_dir = Path(args.base_dir) if args.base_dir else detectar_base_dir()
    if not base_dir.is_dir():
        imprimir_relatorio([resultado("ERRO", base_dir, "base-dir nao encontrado")])
        return 1

    if not verificar_repositorio_git(base_dir):
        imprimir_relatorio([resultado("ERRO", base_dir, "diretorio nao e repositorio git")])
        return 1

    valido, erro_validacao = validar_nome_zip(args.nome)
    if not valido:
        imprimir_relatorio([resultado("ERRO", args.nome, erro_validacao)])
        return 1

    destino_dir = Path(args.destino_dir)
    destino_zip = destino_dir / args.nome
    resultados = []

    if not args.confirmar:
        resultados.append(resultado("AVISO", base_dir, "modo dry-run: nada sera alterado"))
        resultados.append(resultado("OK", base_dir, "repositorio git valido"))
        limpo, _ = verificar_worktree_limpo(base_dir)
        if limpo:
            resultados.append(resultado("OK", base_dir, "working tree limpo"))
        else:
            resultados.append(resultado("AVISO", base_dir, "working tree sujo (bloquearia geracao)"))
        resultados.append(resultado("CRIAR", destino_zip, "dry-run: ZIP seria gerado"))
        resultados.append(resultado("OK", base_dir, "release limpa via git archive"))

        imprimir_relatorio(resultados)
        return 0

    limpo, _ = verificar_worktree_limpo(base_dir)
    if not limpo:
        resultados.append(
            resultado("ERRO", base_dir, "working tree sujo: gere ou descarte alteracoes antes")
        )
        imprimir_relatorio(resultados)
        return 1

    try:
        destino_zip_real = gerar_zip_git_archive(base_dir, destino_zip)
        resultados.append(resultado("CRIADO", destino_zip_real, "release limpa gerada"))
        resultados.append(resultado("OK", base_dir, "release limpa via git archive"))
        imprimir_relatorio(resultados)
        return 0
    except RuntimeError as e:
        imprimir_relatorio([resultado("ERRO", destino_zip, str(e))])
        return 1


if __name__ == "__main__":
    raise SystemExit(main())

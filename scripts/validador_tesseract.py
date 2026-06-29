import shutil
import subprocess
import sys


ERRO_FINAL = 0


def _ok(nome, detalhe=""):
    return {"nome": nome, "status": "OK", "detalhe": detalhe}


def _erro(nome, detalhe=""):
    return {"nome": nome, "status": "ERRO", "detalhe": detalhe}


def _aviso(nome, detalhe=""):
    return {"nome": nome, "status": "AVISO", "detalhe": detalhe}


def verificar_tesseract():
    resultados = []
    caminho = shutil.which("tesseract")
    if not caminho:
        resultados.append(_erro("Tesseract", "comando tesseract nao encontrado no PATH"))
        return resultados

    resultados.append(_ok("Tesseract", f"encontrado em {caminho}"))

    try:
        versao = subprocess.run(
            ["tesseract", "--version"],
            capture_output=True, text=True, timeout=15
        )
        primeira_linha = versao.stdout.splitlines()[0] if versao.stdout else "?"
        linha_stderr = versao.stderr.splitlines()[0] if versao.stderr else ""
        resultados.append(_ok("Tesseract --version", primeira_linha or linha_stderr))
    except Exception as exc:
        resultados.append(_erro("Tesseract --version", str(exc)))
        return resultados

    try:
        langs = subprocess.run(
            ["tesseract", "--list-langs"],
            capture_output=True, text=True, timeout=15
        )
        saida = (langs.stderr or "") + (langs.stdout or "")
        linhas = [l.strip() for l in saida.splitlines() if l.strip()]
        idiomas = [l for l in linhas if not l.startswith("List")]
        resultados.append(_ok("Idiomas instalados", ", ".join(idiomas) if idiomas else "nenhum"))

        tem_por = any(lang.lower() in ("por", "pt") for lang in idiomas)
        tem_eng = any(lang.lower() == "eng" for lang in idiomas)

        if tem_por:
            resultados.append(_ok("Idioma por (portugues)", "disponivel"))
        else:
            resultados.append(_erro("Idioma por (portugues)", "ausente. Instale: tesseract --list-langs | findstr por"))

        if tem_eng:
            resultados.append(_ok("Idioma eng (ingles)", "disponivel"))
        else:
            resultados.append(_aviso("Idioma eng (ingles)", "ausente. Opcional, mas recomendado para OCR misto"))

    except Exception as exc:
        resultados.append(_erro("Tesseract --list-langs", str(exc)))

    return resultados


def imprimir_relatorio(resultados):
    print("OCR-LEITOR - Validador Tesseract")
    print("=" * 35)
    for item in resultados:
        detalhe = f" - {item['detalhe']}" if item.get("detalhe") else ""
        print(f"[{item['status']}] {item['nome']}{detalhe}")


def main():
    resultados = verificar_tesseract()
    imprimir_relatorio(resultados)
    global ERRO_FINAL
    ERRO_FINAL = 1 if any(item["status"] == "ERRO" for item in resultados) else 0
    return ERRO_FINAL


if __name__ == "__main__":
    sys.exit(main())

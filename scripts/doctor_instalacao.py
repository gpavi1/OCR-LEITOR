import importlib.util
import shutil
import sys
from pathlib import Path

try:
    from scripts.caminhos_instalacao import classificar_caminho_instalacao
except ModuleNotFoundError:
    from caminhos_instalacao import classificar_caminho_instalacao


STATUS_OK = "OK"
STATUS_AVISO = "AVISO"
STATUS_ERRO = "ERRO"


def resultado(nome, status, detalhe=""):
    return {
        "nome": nome,
        "status": status,
        "detalhe": detalhe,
    }


def verificar_arquivo(caminho, obrigatorio=True):
    path = Path(caminho)
    if path.is_file():
        return resultado(str(path), STATUS_OK, "arquivo encontrado")

    status = STATUS_ERRO if obrigatorio else STATUS_AVISO
    detalhe = "arquivo obrigatorio ausente" if obrigatorio else "arquivo opcional ausente"
    return resultado(str(path), status, detalhe)


def verificar_pasta(caminho, obrigatorio=True):
    path = Path(caminho)
    if path.is_dir():
        return resultado(str(path), STATUS_OK, "pasta encontrada")

    status = STATUS_ERRO if obrigatorio else STATUS_AVISO
    detalhe = "pasta obrigatoria ausente" if obrigatorio else "pasta opcional ausente"
    return resultado(str(path), status, detalhe)


def verificar_modulo(nome_modulo, nome_exibicao=None, obrigatorio=True):
    nome = nome_exibicao or nome_modulo
    try:
        spec = importlib.util.find_spec(nome_modulo)
    except (ImportError, ModuleNotFoundError, ValueError):
        spec = None

    if spec is not None:
        return resultado(nome, STATUS_OK, "modulo disponivel")

    status = STATUS_ERRO if obrigatorio else STATUS_AVISO
    detalhe = "modulo obrigatorio ausente" if obrigatorio else "modulo opcional ausente"
    return resultado(nome, status, detalhe)


def _verificar_python():
    return resultado("Python em execucao", STATUS_OK, sys.version.split()[0])


def _verificar_venv():
    em_venv = sys.prefix != getattr(sys, "base_prefix", sys.prefix) or hasattr(sys, "real_prefix")
    if em_venv:
        return resultado("Ambiente virtual", STATUS_OK, f"sys.prefix={sys.prefix}")
    return resultado("Ambiente virtual", STATUS_AVISO, "processo atual nao parece estar em .venv")


def _verificar_tesseract_path():
    caminho = shutil.which("tesseract")
    if caminho:
        return resultado("Tesseract no PATH", STATUS_OK, caminho)
    return resultado("Tesseract no PATH", STATUS_AVISO, "comando tesseract nao encontrado no PATH")


def _verificar_caminho_instalacao(base_dir):
    classificacao = classificar_caminho_instalacao(base_dir, modo="desenvolvimento")
    detalhes = classificacao["avisos"] + classificacao["bloqueios"]
    detalhes.append("Para cliente, use C:\\OCR-LEITOR. Para demo, use C:\\OCR-LEITOR-DEMO.")
    status = STATUS_AVISO if classificacao["avisos"] or classificacao["bloqueios"] else STATUS_OK
    return resultado("Caminho de instalacao", status, " ".join(detalhes))


def coletar_diagnostico(base_dir):
    base = Path(base_dir)
    resultados = [
        _verificar_python(),
        _verificar_venv(),
        _verificar_caminho_instalacao(base),
        verificar_arquivo(base / "requirements.txt"),
        verificar_arquivo(base / "requirements.add.txt"),
        verificar_arquivo(base / ".env.example"),
        verificar_arquivo(base / ".env", obrigatorio=False),
        verificar_arquivo(base / "config" / "settings.json", obrigatorio=False),
        verificar_arquivo(base / "database" / "schema.sql"),
        verificar_arquivo(base / "web" / "app.py"),
    ]

    for pasta in ["input", "output", "processed", "erro", "logs", "config"]:
        resultados.append(verificar_pasta(base / pasta))

    for nome_modulo, nome_exibicao in [
        ("flask", "flask"),
        ("waitress", "waitress"),
        ("mysql.connector", "mysql.connector"),
        ("dotenv", "dotenv"),
        ("pytesseract", "pytesseract"),
        ("PIL", "PIL"),
        ("cv2", "cv2"),
    ]:
        resultados.append(verificar_modulo(nome_modulo, nome_exibicao))

    resultados.append(_verificar_tesseract_path())
    return resultados


def imprimir_relatorio(resultados):
    print("OCR-LEITOR - Doctor de instalacao")
    print("=" * 36)
    for item in resultados:
        detalhe = f" - {item['detalhe']}" if item.get("detalhe") else ""
        print(f"[{item['status']}] {item['nome']}{detalhe}")


def main():
    base_dir = Path(__file__).resolve().parents[1]
    resultados = coletar_diagnostico(base_dir)
    imprimir_relatorio(resultados)
    return 1 if any(item["status"] == STATUS_ERRO for item in resultados) else 0


if __name__ == "__main__":
    raise SystemExit(main())

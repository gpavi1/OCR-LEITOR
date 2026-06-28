from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[1]
REQ = BASE_DIR / "requirements.txt"


def test_requirements_txt_existe():
    assert REQ.is_file()


def test_contem_pytesseract():
    conteudo = REQ.read_text(encoding="utf-8")
    assert "pytesseract" in conteudo


def test_contem_pdf2image():
    conteudo = REQ.read_text(encoding="utf-8")
    assert "pdf2image" in conteudo


def test_contem_pillow():
    conteudo = REQ.read_text(encoding="utf-8")
    assert "Pillow" in conteudo


def test_contem_opencv():
    conteudo = REQ.read_text(encoding="utf-8")
    assert "opencv-python" in conteudo


def test_nao_contem_pillow_10_1_0():
    conteudo = REQ.read_text(encoding="utf-8")
    assert "Pillow==10.1.0" not in conteudo


def test_nao_contem_opencv_4_8_1_78():
    conteudo = REQ.read_text(encoding="utf-8")
    assert "opencv-python==4.8.1.78" not in conteudo


def test_pillow_usar_faixa_compativel():
    conteudo = REQ.read_text(encoding="utf-8")
    for line in conteudo.splitlines():
        if "Pillow" in line:
            assert ">=" in line or "==" in line
            assert "11" in line
            break


def test_opencv_usar_faixa_compativel():
    conteudo = REQ.read_text(encoding="utf-8")
    for line in conteudo.splitlines():
        if "opencv-python" in line:
            assert ">=" in line or "==" in line
            assert "4.12" in line
            break


def test_nao_contem_env():
    conteudo = REQ.read_text(encoding="utf-8")
    assert ".env" not in conteudo


def test_nao_contem_settings_json():
    conteudo = REQ.read_text(encoding="utf-8")
    assert "settings.json" not in conteudo


def test_nao_contem_caminho_local():
    conteudo = REQ.read_text(encoding="utf-8")
    assert "C:" not in conteudo and "Users" not in conteudo


def test_nao_contem_url_externa():
    conteudo = REQ.read_text(encoding="utf-8")
    assert "http://" not in conteudo
    assert "https://" not in conteudo


def test_nao_contem_git_plus():
    conteudo = REQ.read_text(encoding="utf-8")
    assert "git+" not in conteudo


def test_nao_contem_senha_token_secret():
    conteudo = REQ.read_text(encoding="utf-8")
    lines = conteudo.splitlines()
    for line in lines:
        line_stripped = line.strip()
        if line_stripped.startswith("#"):
            lower = line_stripped.lower()
            assert "senha" not in lower
            assert "token" not in lower
            assert "secret" not in lower

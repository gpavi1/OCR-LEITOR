from pathlib import Path
import sys

BASE_DIR = Path(__file__).resolve().parents[1]
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from web.app import extensao_permitida_upload, gerar_nome_upload_seguro

APP_PATH = BASE_DIR / "web" / "app.py"
UPLOAD_HTML = BASE_DIR / "web" / "templates" / "upload_documento.html"
BASE_HTML = BASE_DIR / "web" / "templates" / "base.html"
CSS_PATH = BASE_DIR / "web" / "static" / "style.css"


def test_app_existe():
    assert APP_PATH.is_file()


def test_upload_html_existe():
    assert UPLOAD_HTML.is_file()


def test_base_html_existe():
    assert BASE_HTML.is_file()


def test_css_existe():
    assert CSS_PATH.is_file()


def test_app_contem_rota_upload():
    conteudo = APP_PATH.read_text(encoding="utf-8")
    assert '"/upload"' in conteudo or '"/upload",' in conteudo or "'/upload'" in conteudo


def test_app_contem_extensao_jpg():
    conteudo = APP_PATH.read_text(encoding="utf-8")
    assert '".jpg"' in conteudo or "'.jpg'" in conteudo


def test_app_contem_extensao_jpeg():
    conteudo = APP_PATH.read_text(encoding="utf-8")
    assert '".jpeg"' in conteudo or "'.jpeg'" in conteudo


def test_app_contem_extensao_png():
    conteudo = APP_PATH.read_text(encoding="utf-8")
    assert '".png"' in conteudo or "'.png'" in conteudo


def test_app_contem_extensao_pdf():
    conteudo = APP_PATH.read_text(encoding="utf-8")
    assert '".pdf"' in conteudo or "'.pdf'" in conteudo


def test_app_contem_limite_10mb():
    conteudo = APP_PATH.read_text(encoding="utf-8")
    assert "10 * 1024 * 1024" in conteudo


def test_app_contem_pasta_input():
    conteudo = APP_PATH.read_text(encoding="utf-8")
    assert "input" in conteudo


def test_app_nao_contem_pytesseract_no_upload():
    conteudo = APP_PATH.read_text(encoding="utf-8")
    assert "pytesseract" not in conteudo


def test_app_nao_contem_monday_api_url():
    conteudo = APP_PATH.read_text(encoding="utf-8")
    assert "api.monday.com" not in conteudo


def test_app_nao_contem_fechames():
    conteudo = APP_PATH.read_text(encoding="utf-8")
    assert "FechaMes" not in conteudo and "fechames" not in conteudo


def test_upload_html_contem_multipart():
    conteudo = UPLOAD_HTML.read_text(encoding="utf-8")
    assert "multipart/form-data" in conteudo


def test_upload_html_contem_name_documento():
    conteudo = UPLOAD_HTML.read_text(encoding="utf-8")
    assert 'name="documento"' in conteudo


def test_upload_html_contem_accept():
    conteudo = UPLOAD_HTML.read_text(encoding="utf-8")
    assert '.jpg,.jpeg,.png,.pdf' in conteudo


def test_upload_html_contem_titulo():
    conteudo = UPLOAD_HTML.read_text(encoding="utf-8")
    assert "Enviar documento" in conteudo


def test_base_contem_link_upload():
    conteudo = BASE_HTML.read_text(encoding="utf-8")
    assert 'href="/upload"' in conteudo


def test_css_contem_marcador_upload():
    conteudo = CSS_PATH.read_text(encoding="utf-8")
    assert "UPLOAD-OCR-01 — Upload seguro pelo painel" in conteudo


def test_css_nao_contem_cdn():
    conteudo = CSS_PATH.read_text(encoding="utf-8").lower()
    assert "cdn" not in conteudo


def test_nao_contem_import_url():
    for path in (UPLOAD_HTML, BASE_HTML, CSS_PATH):
        conteudo = path.read_text(encoding="utf-8")
        assert "@import url(" not in conteudo


def test_nao_contem_url_externa():
    for path in (UPLOAD_HTML, BASE_HTML, CSS_PATH):
        conteudo = path.read_text(encoding="utf-8").lower()
        assert 'src="http' not in conteudo
        assert 'url(http' not in conteudo


def test_nao_contem_0_0_0_0():
    for path in (UPLOAD_HTML, BASE_HTML, CSS_PATH, APP_PATH):
        conteudo = path.read_text(encoding="utf-8")
        assert "0.0.0.0" not in conteudo


def test_extensao_permitida_valida_jpg():
    assert extensao_permitida_upload("foto.jpg") is True
    assert extensao_permitida_upload("foto.jpeg") is True
    assert extensao_permitida_upload("foto.png") is True
    assert extensao_permitida_upload("foto.pdf") is True
    assert extensao_permitida_upload("foto.JPG") is True


def test_extensao_permitida_valida_pdf():
    assert extensao_permitida_upload("documento.pdf") is True


def test_extensao_permitida_invalida_exe():
    assert extensao_permitida_upload("virus.exe") is False
    assert extensao_permitida_upload("script.bat") is False
    assert extensao_permitida_upload("arquivo") is False


def test_extensao_permitida_invalida_txt():
    assert extensao_permitida_upload("nota.txt") is False
    assert extensao_permitida_upload("dados.xml") is False
    assert extensao_permitida_upload("doc.html") is False


def test_gerar_nome_seguro_sem_caminho():
    nome = gerar_nome_upload_seguro("foto.jpg")
    assert "/" not in nome
    assert "\\" not in nome
    assert ".." not in nome


def test_gerar_nome_seguro_preserva_extensao():
    nome = gerar_nome_upload_seguro("foto.jpg")
    assert nome.endswith(".jpg")
    nome = gerar_nome_upload_seguro("documento.pdf")
    assert nome.endswith(".pdf")

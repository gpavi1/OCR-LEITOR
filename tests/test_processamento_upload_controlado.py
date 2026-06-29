from pathlib import Path
import sys

BASE_DIR = Path(__file__).resolve().parents[1]
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from web.app import app

APP_PATH = BASE_DIR / "web" / "app.py"
UPLOAD_HTML = BASE_DIR / "web" / "templates" / "upload_documento.html"
CSS_PATH = BASE_DIR / "web" / "static" / "style.css"


def test_app_existe():
    assert APP_PATH.is_file()


def test_upload_html_existe():
    assert UPLOAD_HTML.is_file()


def test_css_existe():
    assert CSS_PATH.is_file()


def test_app_contem_rota_processar():
    conteudo = APP_PATH.read_text(encoding="utf-8")
    assert '"/upload/processar"' in conteudo


def test_rota_usa_post():
    conteudo = APP_PATH.read_text(encoding="utf-8")
    assert 'methods=["POST"]' in conteudo or 'methods = ["POST"]' in conteudo


def test_app_nao_contem_shell_true():
    conteudo = APP_PATH.read_text(encoding="utf-8")
    assert "shell=True" not in conteudo


def test_app_nao_contem_0_0_0_0():
    conteudo = APP_PATH.read_text(encoding="utf-8")
    assert "0.0.0.0" not in conteudo


def test_app_nao_contem_monday_api_url():
    conteudo = APP_PATH.read_text(encoding="utf-8")
    assert "api.monday.com" not in conteudo


def test_app_nao_contem_fechames():
    conteudo = APP_PATH.read_text(encoding="utf-8")
    assert "FechaMes" not in conteudo and "fechames" not in conteudo


def test_upload_html_contem_rota_processar():
    conteudo = UPLOAD_HTML.read_text(encoding="utf-8")
    assert "/upload/processar" in conteudo


def test_upload_html_contem_post():
    conteudo = UPLOAD_HTML.read_text(encoding="utf-8")
    assert 'method="post"' in conteudo


def test_upload_html_mantem_name_documento():
    conteudo = UPLOAD_HTML.read_text(encoding="utf-8")
    assert 'name="documento"' in conteudo


def test_upload_html_mantem_multipart():
    conteudo = UPLOAD_HTML.read_text(encoding="utf-8")
    assert "multipart/form-data" in conteudo


def test_upload_html_mantem_accept():
    conteudo = UPLOAD_HTML.read_text(encoding="utf-8")
    assert ".jpg,.jpeg,.png,.pdf" in conteudo


def test_upload_html_explica_separacao():
    conteudo = UPLOAD_HTML.read_text(encoding="utf-8")
    assert "etapas separadas" in conteudo
    assert "processamento controlado" in conteudo.lower()


def test_css_marcador_upload_ocr_02():
    conteudo = CSS_PATH.read_text(encoding="utf-8")
    assert "UPLOAD-OCR-02 — Processamento controlado" in conteudo


def test_rota_processar_importa_pipeline_existente():
    conteudo = APP_PATH.read_text(encoding="utf-8")
    assert "ocr_pipeline_s1" in conteudo


def test_rota_processar_usa_input_folder():
    conteudo = APP_PATH.read_text(encoding="utf-8")
    assert "INPUT_FOLDER" in conteudo


def test_rota_processar_verifica_arquivos():
    conteudo = APP_PATH.read_text(encoding="utf-8")
    assert "iterdir" in conteudo or "listdir" in conteudo


def test_rota_processar_wrapped_try_except():
    conteudo = APP_PATH.read_text(encoding="utf-8")
    assert "try" in conteudo and "except" in conteudo


def test_nao_aceita_caminho_arbitrario():
    conteudo = APP_PATH.read_text(encoding="utf-8")
    idx = conteudo.index("/upload/processar")
    secao = conteudo[idx:idx+1000]
    # Ensure no input() or request.form for file path
    assert "request.form" not in secao or "caminho" not in secao.lower()[:100]


def test_rota_processar_post_retorna_redirect():
    with app.test_client() as client:
        with client.session_transaction() as sess:
            sess["autenticado"] = True
        resp = client.post("/upload/processar")
        assert resp.status_code == 302


def test_rota_processar_get_rejeitado():
    with app.test_client() as client:
        with client.session_transaction() as sess:
            sess["autenticado"] = True
        resp = client.get("/upload/processar")
        assert resp.status_code == 405

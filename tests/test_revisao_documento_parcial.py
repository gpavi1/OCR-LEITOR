from pathlib import Path
import sys

BASE_DIR = Path(__file__).resolve().parents[1]
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from web.app import status_label, STATUS_LABEL, STATUS_PRECISA_REVISAO

APP_PATH = BASE_DIR / "web" / "app.py"
DOCS_HTML = BASE_DIR / "web" / "templates" / "documentos.html"
DETALHE_HTML = BASE_DIR / "web" / "templates" / "documento_detalhe.html"
CSS_PATH = BASE_DIR / "web" / "static" / "style.css"


def test_app_existe():
    assert APP_PATH.is_file()


def test_documentos_html_existe():
    assert DOCS_HTML.is_file()


def test_detalhe_html_existe():
    assert DETALHE_HTML.is_file()


def test_css_existe():
    assert CSS_PATH.is_file()


def test_documentos_contem_precisa_revisao():
    conteudo = DOCS_HTML.read_text(encoding="utf-8")
    assert "Precisa revisão" in conteudo or "needs-review" in conteudo


def test_detalhe_contem_alerta_revisao():
    conteudo = DETALHE_HTML.read_text(encoding="utf-8")
    assert "precisa de revisão" in conteudo


def test_css_contem_marcador_revisao():
    conteudo = CSS_PATH.read_text(encoding="utf-8")
    assert "REVISAO-OCR-01 — Documento parcial revisável" in conteudo


def test_css_contem_regra_needs_review():
    conteudo = CSS_PATH.read_text(encoding="utf-8")
    assert ".needs-review" in conteudo


def test_css_contem_regra_review_alert():
    conteudo = CSS_PATH.read_text(encoding="utf-8")
    assert ".review-alert" in conteudo


def test_app_nao_contem_monday():
    conteudo = APP_PATH.read_text(encoding="utf-8")
    assert "Monday" not in conteudo and "monday" not in conteudo


def test_app_nao_contem_fechames():
    conteudo = APP_PATH.read_text(encoding="utf-8")
    assert "FechaMes" not in conteudo and "fechames" not in conteudo


def test_app_nao_contem_alter_table():
    conteudo = APP_PATH.read_text(encoding="utf-8")
    assert "ALTER TABLE" not in conteudo


def test_app_nao_contem_drop_table():
    conteudo = APP_PATH.read_text(encoding="utf-8")
    assert "DROP TABLE" not in conteudo


def test_app_nao_contem_novo_pytesseract():
    conteudo = APP_PATH.read_text(encoding="utf-8")
    assert "pytesseract" not in conteudo


def test_nao_contem_cdn():
    for path in (DOCS_HTML, DETALHE_HTML, CSS_PATH):
        conteudo = path.read_text(encoding="utf-8").lower()
        assert "cdn" not in conteudo


def test_nao_contem_import_url():
    for path in (DOCS_HTML, DETALHE_HTML, CSS_PATH):
        conteudo = path.read_text(encoding="utf-8")
        assert "@import url(" not in conteudo


def test_nao_contem_url_externa():
    for path in (DOCS_HTML, DETALHE_HTML, CSS_PATH):
        conteudo = path.read_text(encoding="utf-8").lower()
        assert 'src="http' not in conteudo
        assert 'url(http' not in conteudo


def test_detalhe_mantem_form_editar():
    conteudo = DETALHE_HTML.read_text(encoding="utf-8")
    assert '/documentos/' in conteudo and '/editar' in conteudo


def test_detalhe_mantem_form_revisar():
    conteudo = DETALHE_HTML.read_text(encoding="utf-8")
    assert '/revisar' in conteudo or 'marcar como revisado' in conteudo


def test_detalhe_mantem_json_panel():
    conteudo = DETALHE_HTML.read_text(encoding="utf-8")
    assert "json_path" in conteudo or "JSON padrão" in conteudo


def test_documentos_mantem_loop():
    conteudo = DOCS_HTML.read_text(encoding="utf-8")
    assert "{% for doc in documentos %}" in conteudo


def test_documentos_mantem_link_abrir():
    conteudo = DOCS_HTML.read_text(encoding="utf-8")
    assert "/documentos/" in conteudo and "abrir" in conteudo


def test_status_label_parcial():
    assert status_label("pendente_revisao") == "Precisa revisão"


def test_status_label_erro_ocr():
    assert status_label("erro_ocr") == "Erro OCR — revisar"


def test_status_label_pendente_revisao():
    assert status_label("pendente_revisao") == "Precisa revisão"
    assert "pendente_revisao" in STATUS_PRECISA_REVISAO
    assert "erro_ocr" in STATUS_PRECISA_REVISAO

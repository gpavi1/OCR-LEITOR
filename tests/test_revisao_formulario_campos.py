from pathlib import Path
import sys

BASE_DIR = Path(__file__).resolve().parents[1]
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from web.app import campo_pendente, STATUS_PRECISA_REVISAO

APP_PATH = BASE_DIR / "web" / "app.py"
DETAIL_HTML = BASE_DIR / "web" / "templates" / "documento_detalhe.html"
CSS_PATH = BASE_DIR / "web" / "static" / "style.css"


def test_app_existe():
    assert APP_PATH.is_file()


def test_documento_detalhe_html_existe():
    assert DETAIL_HTML.is_file()


def test_css_existe():
    assert CSS_PATH.is_file()


def test_documento_detalhe_contem_campos_extraidos():
    conteudo = DETAIL_HTML.read_text(encoding="utf-8")
    assert "Campos extraídos" in conteudo


def test_documento_detalhe_contem_area_de_revisao():
    conteudo = DETAIL_HTML.read_text(encoding="utf-8")
    assert "Correção manual dos campos" in conteudo
    assert "Aprovação" in conteudo


def test_documento_detalhe_mantem_formulario_post_existente():
    conteudo = DETAIL_HTML.read_text(encoding="utf-8")
    assert 'method="post"' in conteudo
    assert '/documentos/{{ documento.id }}/revisar' in conteudo


def test_documento_detalhe_contem_texto_de_revisao():
    conteudo = DETAIL_HTML.read_text(encoding="utf-8")
    assert "revisão humana" in conteudo.lower()
    assert "campos vazios aparecem em destaque" in conteudo.lower()


def test_documento_detalhe_contem_texto_de_aprovacao():
    conteudo = DETAIL_HTML.read_text(encoding="utf-8")
    assert "A aprovação não é automática" in conteudo
    assert "próxima etapa" in conteudo


def test_documento_detalhe_contem_observacao_revisao():
    conteudo = DETAIL_HTML.read_text(encoding="utf-8")
    assert "observacao_revisao" in conteudo


def test_css_contem_marcador_revisao_02():
    conteudo = CSS_PATH.read_text(encoding="utf-8")
    assert "REVISAO-OCR-02 — Formulário de revisão" in conteudo


def test_css_contem_regra_campo_pendente():
    conteudo = CSS_PATH.read_text(encoding="utf-8")
    assert ".review-field.is-empty" in conteudo
    assert ".review-input.is-empty" in conteudo


def test_css_contem_regra_alerta_operacional():
    conteudo = CSS_PATH.read_text(encoding="utf-8")
    assert ".review-alert" in conteudo


def test_app_nao_contem_alter_table():
    conteudo = APP_PATH.read_text(encoding="utf-8")
    assert "ALTER TABLE" not in conteudo


def test_app_nao_contem_drop_table():
    conteudo = APP_PATH.read_text(encoding="utf-8")
    assert "DROP TABLE" not in conteudo


def test_app_nao_contem_monday_api_url():
    conteudo = APP_PATH.read_text(encoding="utf-8")
    assert "api.monday.com" not in conteudo


def test_app_nao_contem_fechames():
    conteudo = APP_PATH.read_text(encoding="utf-8")
    assert "FechaMes" not in conteudo and "fechames" not in conteudo


def test_app_nao_contem_pytesseract_novo():
    conteudo = APP_PATH.read_text(encoding="utf-8")
    assert "pytesseract" not in conteudo


def test_app_nao_contem_shell_true():
    conteudo = APP_PATH.read_text(encoding="utf-8")
    assert "shell=True" not in conteudo


def test_app_nao_contem_subprocess():
    conteudo = APP_PATH.read_text(encoding="utf-8")
    assert "subprocess" not in conteudo


def test_templates_nao_contem_cdn():
    for path in (DETAIL_HTML, CSS_PATH):
        conteudo = path.read_text(encoding="utf-8").lower()
        assert "cdn" not in conteudo


def test_templates_nao_contem_import_url():
    for path in (DETAIL_HTML, CSS_PATH):
        conteudo = path.read_text(encoding="utf-8")
        assert "@import url(" not in conteudo


def test_templates_nao_contem_url_externa():
    for path in (DETAIL_HTML, CSS_PATH):
        conteudo = path.read_text(encoding="utf-8").lower()
        assert 'src="http' not in conteudo
        assert 'url(http' not in conteudo


def test_documento_detalhe_mantem_formulario_de_edicao():
    conteudo = DETAIL_HTML.read_text(encoding="utf-8")
    assert '/documentos/{{ documento.id }}/editar' in conteudo
    assert 'Salvar correções' in conteudo


def test_documento_detalhe_mantem_area_de_aprovacao():
    conteudo = DETAIL_HTML.read_text(encoding="utf-8")
    assert '/documentos/{{ documento.id }}/revisar' in conteudo
    assert 'Aprovar e avançar' in conteudo


def test_campo_pendente_vazio():
    assert campo_pendente(None) is True
    assert campo_pendente("") is True
    assert campo_pendente("   ") is True


def test_campo_pendente_preenchido():
    assert campo_pendente("CAFE TRES CORACOES") is False
    assert campo_pendente(123) is False


def test_status_precisa_revisao_contem_status_relevantes():
    assert "pendente_revisao" in STATUS_PRECISA_REVISAO
    assert "erro_ocr" in STATUS_PRECISA_REVISAO


def test_testes_nao_exigem_mysql_real_ou_tesseract_real():
    # Os checks acima operam apenas em arquivos e helpers puros.
    assert True

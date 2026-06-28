from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[1]
HTML_BASE = BASE_DIR / "web" / "templates" / "base.html"
HTML_DOCS = BASE_DIR / "web" / "templates" / "documentos.html"
CSS_PATH = BASE_DIR / "web" / "static" / "style.css"


def test_base_html_existe():
    assert HTML_BASE.is_file()


def test_documentos_html_existe():
    assert HTML_DOCS.is_file()


def test_css_existe():
    assert CSS_PATH.is_file()


def test_base_contem_sidebar_nav():
    conteudo = HTML_BASE.read_text(encoding="utf-8")
    assert "sidebar-nav" in conteudo


def test_base_contem_nav_section():
    conteudo = HTML_BASE.read_text(encoding="utf-8")
    assert "nav-section" in conteudo


def test_base_contem_nav_link():
    conteudo = HTML_BASE.read_text(encoding="utf-8")
    assert "nav-link" in conteudo


def test_base_contem_topbar():
    conteudo = HTML_BASE.read_text(encoding="utf-8")
    assert "workspace-topbar" in conteudo or "topbar" in conteudo


def test_base_mantem_block_content():
    conteudo = HTML_BASE.read_text(encoding="utf-8")
    assert "{% block content %}" in conteudo


def test_base_mantem_flash_messages():
    conteudo = HTML_BASE.read_text(encoding="utf-8")
    assert "get_flashed_messages" in conteudo


def test_base_mantem_links_principais():
    conteudo = HTML_BASE.read_text(encoding="utf-8")
    assert 'href="/"' in conteudo
    assert 'href="/integracoes"' in conteudo or "href='/integracoes'" in conteudo
    assert 'href="/integracoes/dashboard"' in conteudo
    assert 'href="/exportar/documentos.csv"' in conteudo
    assert 'href="/health"' in conteudo
    assert 'href="/logout"' in conteudo


def test_documentos_mantem_resumo_total():
    conteudo = HTML_DOCS.read_text(encoding="utf-8")
    assert "{{ resumo.total" in conteudo


def test_documentos_mantem_resumo_pendente_integracao():
    conteudo = HTML_DOCS.read_text(encoding="utf-8")
    assert "{{ resumo.pendente_integracao" in conteudo


def test_documentos_mantem_resumo_pendente_revisao():
    conteudo = HTML_DOCS.read_text(encoding="utf-8")
    assert "{{ resumo.pendente_revisao" in conteudo


def test_documentos_mantem_resumo_erros():
    conteudo = HTML_DOCS.read_text(encoding="utf-8")
    assert "{{ resumo.erros" in conteudo


def test_documentos_mantem_resumo_revisados():
    conteudo = HTML_DOCS.read_text(encoding="utf-8")
    assert "{{ resumo.revisados" in conteudo


def test_documentos_mantem_loop_documentos():
    conteudo = HTML_DOCS.read_text(encoding="utf-8")
    assert "{% for doc in documentos %}" in conteudo


def test_documentos_mantem_link_abrir():
    conteudo = HTML_DOCS.read_text(encoding="utf-8")
    assert "/documentos/{{ doc.id }}" in conteudo


def test_documentos_contem_action_cards():
    conteudo = HTML_DOCS.read_text(encoding="utf-8")
    assert "action-card" in conteudo or "quick-actions" in conteudo


def test_css_marcador_ui_ocr_04():
    conteudo = CSS_PATH.read_text(encoding="utf-8")
    assert "UI-OCR-04 — Layout principal estilo observabilidade" in conteudo


def test_css_contem_sidebar_nav_ou_nav_link():
    conteudo = CSS_PATH.read_text(encoding="utf-8")
    assert "sidebar-nav" in conteudo or "nav-link" in conteudo


def test_css_contem_topbar():
    conteudo = CSS_PATH.read_text(encoding="utf-8")
    assert "workspace-topbar" in conteudo or "topbar-title" in conteudo


def test_css_contem_action_card_ou_quick_actions():
    conteudo = CSS_PATH.read_text(encoding="utf-8")
    assert "action-card" in conteudo or "quick-actions" in conteudo


def test_css_contem_media_query():
    conteudo = CSS_PATH.read_text(encoding="utf-8")
    assert "@media" in conteudo


def test_nao_contem_langsmith():
    for path in (HTML_BASE, HTML_DOCS, CSS_PATH):
        conteudo = path.read_text(encoding="utf-8").lower()
        assert "langsmith" not in conteudo


def test_nao_contem_power_bi():
    for path in (HTML_BASE, HTML_DOCS, CSS_PATH):
        conteudo = path.read_text(encoding="utf-8").lower()
        assert "power bi" not in conteudo


def test_nao_contem_import_url():
    for path in (HTML_BASE, HTML_DOCS, CSS_PATH):
        conteudo = path.read_text(encoding="utf-8")
        assert "@import url(" not in conteudo


def test_nao_contem_cdn():
    for path in (HTML_BASE, HTML_DOCS, CSS_PATH):
        conteudo = path.read_text(encoding="utf-8").lower()
        assert "cdn" not in conteudo


def test_nao_contem_0_0_0_0():
    for path in (HTML_BASE, HTML_DOCS, CSS_PATH):
        conteudo = path.read_text(encoding="utf-8")
        assert "0.0.0.0" not in conteudo


def test_nao_contem_comandos_proibidos():
    for path in (HTML_BASE, HTML_DOCS, CSS_PATH):
        conteudo = path.read_text(encoding="utf-8")
        assert "pip install" not in conteudo
        assert "sc create" not in conteudo
        assert "schtasks" not in conteudo

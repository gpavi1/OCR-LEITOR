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


def test_documentos_titulo_curto():
    conteudo = HTML_DOCS.read_text(encoding="utf-8")
    assert "Visão geral" in conteudo
    assert "Fila, revisão e status" in conteudo


def test_base_contem_sidebar_nav():
    conteudo = HTML_BASE.read_text(encoding="utf-8")
    assert "sidebar-nav" in conteudo


def test_base_contem_workspace_topbar():
    conteudo = HTML_BASE.read_text(encoding="utf-8")
    assert "workspace-topbar" in conteudo


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


def test_documentos_mantem_action_cards():
    conteudo = HTML_DOCS.read_text(encoding="utf-8")
    assert "action-card" in conteudo


def test_documentos_mantem_metric_cards():
    conteudo = HTML_DOCS.read_text(encoding="utf-8")
    assert "metric-cards" in conteudo


def test_documentos_mantem_tabela():
    conteudo = HTML_DOCS.read_text(encoding="utf-8")
    assert "panel" in conteudo and "table" in conteudo


def test_css_marcador_ui_ocr_04b():
    conteudo = CSS_PATH.read_text(encoding="utf-8")
    assert "UI-OCR-04B — Refinamento compacto estilo observabilidade" in conteudo


def test_css_secao_04b_apos_04():
    conteudo = CSS_PATH.read_text(encoding="utf-8")
    assert conteudo.index("UI-OCR-04B") > conteudo.index("UI-OCR-04 —")


def test_css_sidebar_compacta():
    conteudo = CSS_PATH.read_text(encoding="utf-8")
    assert "grid-template-columns: 220px" in conteudo


def test_css_nav_active_discreto():
    conteudo = CSS_PATH.read_text(encoding="utf-8")
    assert "nav-link-active" in conteudo
    assert "rgba(56, 189, 248" in conteudo


def test_css_glow_removido():
    conteudo = CSS_PATH.read_text(encoding="utf-8")
    assert "box-shadow: none" in conteudo
    assert "transform: none" in conteudo


def test_css_btn_sem_sombra():
    conteudo = CSS_PATH.read_text(encoding="utf-8")
    idx = conteudo.index("/* UI-OCR-04B")
    secao_04b = conteudo[idx:]
    assert "box-shadow: none" in secao_04b


def test_css_badge_sem_pseudo():
    conteudo = CSS_PATH.read_text(encoding="utf-8")
    assert "badge::before" in conteudo
    assert "display: none" in conteudo


def test_css_card_sem_pseudo():
    conteudo = CSS_PATH.read_text(encoding="utf-8")
    assert "card::before, .panel::before" in conteudo or ".card::before" in conteudo
    assert "display: none" in conteudo


def test_css_topbar_compacta():
    conteudo = CSS_PATH.read_text(encoding="utf-8")
    assert "padding: 8px 0 10px" in conteudo
    assert "margin-bottom: 14px" in conteudo


def test_css_panel_compacto():
    conteudo = CSS_PATH.read_text(encoding="utf-8")
    assert "padding: 12px 14px" in conteudo


def test_css_tabela_densa():
    conteudo = CSS_PATH.read_text(encoding="utf-8")
    assert "padding: 7px 8px" in conteudo or "padding: 6px 8px" in conteudo


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


def test_nao_contem_url_externa():
    for path in (HTML_BASE, HTML_DOCS, CSS_PATH):
        conteudo = path.read_text(encoding="utf-8").lower()
        assert 'src="http' not in conteudo
        assert 'url(http' not in conteudo

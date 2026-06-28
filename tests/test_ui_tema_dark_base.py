from pathlib import Path

CSS_PATH = Path(__file__).resolve().parents[1] / "web" / "static" / "style.css"


def test_css_existe():
    assert CSS_PATH.is_file()


def test_css_contem_marcador_ui_ocr_03():
    conteudo = CSS_PATH.read_text(encoding="utf-8")
    assert "UI-OCR-03 — Tema dark base" in conteudo


def test_css_contem_root():
    conteudo = CSS_PATH.read_text(encoding="utf-8")
    assert ":root" in conteudo


def test_css_contem_ocr_variaveis():
    conteudo = CSS_PATH.read_text(encoding="utf-8")
    assert "--ocr-" in conteudo


def test_css_contem_ocr_bg():
    conteudo = CSS_PATH.read_text(encoding="utf-8")
    assert "--ocr-bg" in conteudo


def test_css_contem_ocr_panel():
    conteudo = CSS_PATH.read_text(encoding="utf-8")
    assert "--ocr-panel" in conteudo


def test_css_contem_ocr_border():
    conteudo = CSS_PATH.read_text(encoding="utf-8")
    assert "--ocr-border" in conteudo


def test_css_contem_ocr_text():
    conteudo = CSS_PATH.read_text(encoding="utf-8")
    assert "--ocr-text" in conteudo


def test_css_contem_regra_body():
    conteudo = CSS_PATH.read_text(encoding="utf-8")
    assert "body {" in conteudo


def test_css_contem_regra_table():
    conteudo = CSS_PATH.read_text(encoding="utf-8")
    assert "th {" in conteudo or "td {" in conteudo


def test_css_contem_input_ou_textarea():
    conteudo = CSS_PATH.read_text(encoding="utf-8")
    assert "input {" in conteudo or "textarea {" in conteudo


def test_css_contem_button_ou_btn():
    conteudo = CSS_PATH.read_text(encoding="utf-8")
    assert "btn {" in conteudo or "button {" in conteudo or ".btn {" in conteudo


def test_css_nao_contem_langsmith():
    conteudo = CSS_PATH.read_text(encoding="utf-8").lower()
    assert "langsmith" not in conteudo


def test_css_nao_contem_power_bi():
    conteudo = CSS_PATH.read_text(encoding="utf-8").lower()
    assert "power bi" not in conteudo


def test_css_nao_contem_import_url():
    conteudo = CSS_PATH.read_text(encoding="utf-8")
    assert "@import url(" not in conteudo


def test_css_nao_contem_cdn():
    conteudo = CSS_PATH.read_text(encoding="utf-8").lower()
    assert "cdn" not in conteudo


def test_css_nao_contem_0_0_0_0():
    conteudo = CSS_PATH.read_text(encoding="utf-8")
    assert "0.0.0.0" not in conteudo


def test_css_nao_contem_fechames():
    conteudo = CSS_PATH.read_text(encoding="utf-8")
    assert "FechaMes" not in conteudo

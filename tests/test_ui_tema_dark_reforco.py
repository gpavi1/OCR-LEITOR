from pathlib import Path

CSS_PATH = Path(__file__).resolve().parents[1] / "web" / "static" / "style.css"


def test_css_existe():
    assert CSS_PATH.is_file()


def test_css_contem_marcador_ui_ocr_03b():
    conteudo = CSS_PATH.read_text(encoding="utf-8")
    assert "UI-OCR-03B — Reforço visual perceptível" in conteudo


def test_secao_03b_depois_de_03():
    conteudo = CSS_PATH.read_text(encoding="utf-8")
    pos_03 = conteudo.find("UI-OCR-03 — Tema dark base")
    pos_03b = conteudo.find("UI-OCR-03B — Reforço visual perceptível")
    assert pos_03 >= 0
    assert pos_03b > pos_03


def test_contem_sidebar_ou_menu():
    conteudo = CSS_PATH.read_text(encoding="utf-8")
    assert ".sidebar" in conteudo or "nav a" in conteudo


def test_contem_card():
    conteudo = CSS_PATH.read_text(encoding="utf-8")
    assert ".card" in conteudo


def test_contem_table():
    conteudo = CSS_PATH.read_text(encoding="utf-8")
    assert "table" in conteudo or "th " in conteudo or "td " in conteudo


def test_contem_hover_tabela():
    conteudo = CSS_PATH.read_text(encoding="utf-8")
    assert "tr:hover" in conteudo


def test_contem_button_ou_btn():
    conteudo = CSS_PATH.read_text(encoding="utf-8")
    assert ".btn" in conteudo or "button {" in conteudo


def test_contem_input_ou_textarea():
    conteudo = CSS_PATH.read_text(encoding="utf-8")
    assert "input" in conteudo or "textarea" in conteudo


def test_contem_badge_ou_status():
    conteudo = CSS_PATH.read_text(encoding="utf-8")
    assert ".badge" in conteudo or "status-" in conteudo


def test_contem_box_shadow():
    conteudo = CSS_PATH.read_text(encoding="utf-8")
    assert "box-shadow" in conteudo


def test_contem_focus():
    conteudo = CSS_PATH.read_text(encoding="utf-8")
    assert ":focus" in conteudo


def test_nao_contem_import_url():
    conteudo = CSS_PATH.read_text(encoding="utf-8")
    assert "@import url(" not in conteudo


def test_nao_contem_cdn():
    conteudo = CSS_PATH.read_text(encoding="utf-8").lower()
    assert "cdn" not in conteudo


def test_nao_contem_langsmith():
    conteudo = CSS_PATH.read_text(encoding="utf-8").lower()
    assert "langsmith" not in conteudo


def test_nao_contem_power_bi():
    conteudo = CSS_PATH.read_text(encoding="utf-8").lower()
    assert "power bi" not in conteudo


def test_nao_contem_0_0_0_0():
    conteudo = CSS_PATH.read_text(encoding="utf-8")
    assert "0.0.0.0" not in conteudo


def test_nao_contem_comandos_proibidos():
    conteudo = CSS_PATH.read_text(encoding="utf-8")
    assert "pip install" not in conteudo
    assert "sc create" not in conteudo
    assert "schtasks" not in conteudo

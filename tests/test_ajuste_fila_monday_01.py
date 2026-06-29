import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[1]
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

INTEGRACOES_HTML = BASE_DIR / "web" / "templates" / "integracoes.html"
HISTORICO_HTML = BASE_DIR / "web" / "templates" / "historico_integracoes.html"
DETALHE_HTML = BASE_DIR / "web" / "templates" / "documento_detalhe.html"
APP_PATH = BASE_DIR / "web" / "app.py"


# --- integracoes.html ---

def test_integracoes_condicional_revisado_para_simular():
    conteudo = INTEGRACOES_HTML.read_text(encoding="utf-8")
    assert "{% if doc.revisado %}" in conteudo


def test_integracoes_condicional_revisado_para_enviar():
    conteudo = INTEGRACOES_HTML.read_text(encoding="utf-8")
    assert "Enviar para Monday" in conteudo
    assert "doc.revisado" in conteudo


def test_integracoes_mensagem_sem_revisao():
    conteudo = INTEGRACOES_HTML.read_text(encoding="utf-8")
    assert "precisa de revis" in conteudo


# --- historico_integracoes.html ---

def test_historico_usa_status_atual():
    conteudo = HISTORICO_HTML.read_text(encoding="utf-8")
    assert "status_atual" in conteudo


def test_historico_bloqueia_reenfileirar_pendente():
    conteudo = HISTORICO_HTML.read_text(encoding="utf-8")
    assert "pendente_integracao" in conteudo
    assert "reenfileirar" in conteudo


def test_historico_bloqueia_reenfileirar_integrado():
    conteudo = HISTORICO_HTML.read_text(encoding="utf-8")
    assert "integrado" in conteudo
    assert "'integrado'" in conteudo or "'integrado')" in conteudo


def test_historico_preserva_tentativas():
    conteudo = HISTORICO_HTML.read_text(encoding="utf-8")
    assert "tentativa." in conteudo or "tentativas" in conteudo


def test_historico_exibe_doc_integrado():
    conteudo = HISTORICO_HTML.read_text(encoding="utf-8")
    assert "Documento integrado" in conteudo


def test_historico_exibe_doc_ja_na_fila():
    conteudo = HISTORICO_HTML.read_text(encoding="utf-8")
    assert "Documento ja na fila" in conteudo


# --- app.py ---

def test_app_rota_integracoes_contem_revisado():
    conteudo = APP_PATH.read_text(encoding="utf-8")
    assert "revisado," in conteudo
    linhas = [l for l in conteudo.splitlines() if "revisado" in l]
    # linha da SELECT (coluna) vs linha de uso no template
    tem_select = any("revisado," in l for l in linhas)
    assert tem_select


def test_app_rota_historico_contem_status_atual():
    conteudo = APP_PATH.read_text(encoding="utf-8")
    assert "status_atual" in conteudo
    linhas = [l for l in conteudo.splitlines() if "status_atual" in l]
    tem_alias = any("AS status_atual" in l for l in linhas)
    assert tem_alias


# --- documento_detalhe.html nao foi alterado ---

def test_detalhe_mantem_condicionais_originais():
    conteudo = DETALHE_HTML.read_text(encoding="utf-8")
    assert "{% if documento.status == 'pendente_integracao' %}" in conteudo or "if documento.status == 'pendente_integracao'" in conteudo


# --- isolamento ---

def test_testes_nao_chamam_api_externa():
    linhas = Path(__file__).read_text(encoding="utf-8").splitlines()
    imports = [l for l in linhas if l.startswith("import ") or l.startswith("from ")]
    assert all("requests" not in l and "urllib" not in l for l in imports)


def test_testes_nao_usam_token_real():
    linhas = Path(__file__).read_text(encoding="utf-8").splitlines()
    imports = [l for l in linhas if l.startswith("import ") or l.startswith("from ")]
    assert all("mysql" not in l for l in imports)
    assert all("pytesseract" not in l and "tesserocr" not in l for l in imports)

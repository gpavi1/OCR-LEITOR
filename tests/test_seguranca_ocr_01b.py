from pathlib import Path
from io import BytesIO
import sys
import re

BASE_DIR = Path(__file__).resolve().parents[1]
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

USERNAME = "usuario_teste"
PASSWORD = "senha_teste_segura"
SECRET_KEY = "chave-teste-segura-ocr-01b"

from web.app import app, _obter_csrf_token

APP_PATH = BASE_DIR / "web" / "app.py"
TEMPLATES_DIR = BASE_DIR / "web" / "templates"

TEMPLATES_COM_POST = [
    "documento_detalhe.html",
    "login.html",
    "upload_documento.html",
    "integracoes.html",
    "historico_integracoes.html",
]

# ============================================================
# Static analysis — source code checks
# ============================================================

def test_app_contem_obter_csrf_token():
    conteudo = APP_PATH.read_text(encoding="utf-8")
    assert "_obter_csrf_token" in conteudo


def test_app_contem_funcao_csrf_token():
    conteudo = APP_PATH.read_text(encoding="utf-8")
    assert "csrf_token" in conteudo


def test_app_contem_validacao_post_csrf():
    conteudo = APP_PATH.read_text(encoding="utf-8")
    assert "proteger_post_com_csrf" in conteudo


def test_app_usa_hmac_compare_digest_csrf():
    conteudo = APP_PATH.read_text(encoding="utf-8")
    assert "hmac.compare_digest" in conteudo


def test_app_contem_isencao_api_entrada():
    conteudo = APP_PATH.read_text(encoding="utf-8")
    assert "api_entrada_documentos" in conteudo
    linhas = conteudo.splitlines()
    encontrou = False
    for linha in linhas:
        if "api_entrada_documentos" in linha and "exempt" in linha.lower():
            encontrou = True
    if not encontrou:
        for linha in linhas:
            if "api_entrada_documentos" in linha and "CSRF_EXEMPT" in linha.upper():
                encontrou = True
    assert encontrou or "_CSRF_EXEMPT_ENDPOINTS" in conteudo


def test_nenhum_conector_alterado():
    conteudo = APP_PATH.read_text(encoding="utf-8")
    assert "from conectores" in conteudo
    assert "from database" in conteudo


# ============================================================
# Template CSRF presence checks
# ============================================================

def test_todo_template_com_post_tem_csrf_token():
    for nome_template in TEMPLATES_COM_POST:
        caminho = TEMPLATES_DIR / nome_template
        conteudo = caminho.read_text(encoding="utf-8")
        forms = re.findall(r'<form[^>]*method=["\'](?:post|POST)["\']', conteudo)
        csrf_count = conteudo.count('name="csrf_token"')
        msg = f"{nome_template}: {len(forms)} form(s) POST, {csrf_count} csrf_token"
        assert csrf_count >= len(forms), msg


def test_login_contem_csrf_token():
    conteudo = (TEMPLATES_DIR / "login.html").read_text(encoding="utf-8")
    assert 'name="csrf_token"' in conteudo


def test_upload_documento_contem_csrf_token():
    conteudo = (TEMPLATES_DIR / "upload_documento.html").read_text(encoding="utf-8")
    assert 'name="csrf_token"' in conteudo
    assert conteudo.count('name="csrf_token"') >= 2


def test_documento_detalhe_contem_csrf_token():
    conteudo = (TEMPLATES_DIR / "documento_detalhe.html").read_text(encoding="utf-8")
    assert conteudo.count('name="csrf_token"') >= 7


def test_integracoes_contem_csrf_token():
    conteudo = (TEMPLATES_DIR / "integracoes.html").read_text(encoding="utf-8")
    assert conteudo.count('name="csrf_token"') >= 4


def test_historico_integracoes_contem_csrf_token():
    conteudo = (TEMPLATES_DIR / "historico_integracoes.html").read_text(encoding="utf-8")
    assert 'name="csrf_token"' in conteudo


# ============================================================
# Functional tests — Flask test client
# ============================================================

def _login(client):
    resp = client.get("/login")
    token = _extrair_csrf_form(resp.data)
    resp = client.post("/login", data={
        "csrf_token": token,
        "username": USERNAME,
        "password": PASSWORD,
    })
    return resp


def _extrair_csrf_form(html):
    import html as html_mod
    match = re.search(rb'name="csrf_token"\s+value="([^"]+)"', html)
    if match:
        return html_mod.unescape(match.group(1).decode("utf-8"))
    return ""


def test_get_login_retorna_200(monkeypatch):
    monkeypatch.setenv("WEB_USERNAME", USERNAME)
    monkeypatch.setenv("WEB_PASSWORD", PASSWORD)
    monkeypatch.setenv("WEB_SECRET_KEY", SECRET_KEY)
    with app.test_client() as client:
        resp = client.get("/login")
    assert resp.status_code == 200


def test_post_login_sem_csrf_retorna_400(monkeypatch):
    monkeypatch.setenv("WEB_USERNAME", USERNAME)
    monkeypatch.setenv("WEB_PASSWORD", PASSWORD)
    monkeypatch.setenv("WEB_SECRET_KEY", SECRET_KEY)
    with app.test_client() as client:
        resp = client.post("/login", data={
            "username": USERNAME,
            "password": PASSWORD,
        })
    assert resp.status_code == 400


def test_post_login_com_csrf_valido_funciona(monkeypatch):
    monkeypatch.setenv("WEB_USERNAME", USERNAME)
    monkeypatch.setenv("WEB_PASSWORD", PASSWORD)
    monkeypatch.setenv("WEB_SECRET_KEY", SECRET_KEY)
    from web.app import _LOGIN_RATE_LIMIT
    _LOGIN_RATE_LIMIT.clear()
    with app.test_client() as client:
        resp_get = client.get("/login")
        assert resp_get.status_code == 200
        token = _extrair_csrf_form(resp_get.data)
        assert token, "CSRF token nao encontrado no form login"
        resp_post = client.post("/login", data={
            "csrf_token": token,
            "username": USERNAME,
            "password": PASSWORD,
        })
        assert resp_post.status_code == 302


def test_rota_protegida_post_sem_csrf_retorna_400(monkeypatch):
    monkeypatch.setenv("WEB_USERNAME", USERNAME)
    monkeypatch.setenv("WEB_PASSWORD", PASSWORD)
    monkeypatch.setenv("WEB_SECRET_KEY", SECRET_KEY)
    with app.test_client() as client:
        _login(client)
        resp = client.post("/logout")
    assert resp.status_code == 400


def test_api_entrada_bearer_nao_bloqueada_por_csrf(monkeypatch, tmp_path):
    token_api = "token-seguro-teste-csrf"
    monkeypatch.setenv("OCR_API_TOKEN", token_api)
    monkeypatch.setenv("WEB_SECRET_KEY", SECRET_KEY)
    monkeypatch.setattr("web.app.ROOT_DIR", tmp_path)
    with app.test_client() as client:
        resp = client.post(
            "/api/v1/documentos/entrada",
            data={"documento": (BytesIO(b"fake-image"), "teste.jpg")},
            content_type="multipart/form-data",
            headers={"Authorization": f"Bearer {token_api}"},
        )
    assert resp.status_code in (202,)


# ============================================================
# Security: no secrets, no external calls
# ============================================================

def test_app_nao_contem_url_monday():
    conteudo = APP_PATH.read_text(encoding="utf-8")
    assert "api.monday.com" not in conteudo


def test_app_nao_contem_jwt_hardcoded():
    conteudo = APP_PATH.read_text(encoding="utf-8")
    assert "eyJhbGci" not in conteudo


def test_app_nao_contem_requests_http():
    conteudo = APP_PATH.read_text(encoding="utf-8")
    assert "requests.post" not in conteudo
    assert "requests.get" not in conteudo
    assert "urllib.request" not in conteudo
    assert "httpx" not in conteudo

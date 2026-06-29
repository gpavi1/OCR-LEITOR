from pathlib import Path
import sys

BASE_DIR = Path(__file__).resolve().parents[1]
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

USERNAME = "usuario_teste"
PASSWORD = "senha_teste_segura"
SECRET_KEY = "chave-teste-segura-ocr-01a"
BLOQUEIO_SEGUNDOS_TESTE = "1"

from web.app import app

APP_PATH = BASE_DIR / "web" / "app.py"

# ============================================================
# Static analysis — source code checks
# ============================================================

def test_nao_contem_fallback_fixo_inseguro():
    conteudo = APP_PATH.read_text(encoding="utf-8")
    assert "ocr-leitor-local-dev" not in conteudo


def test_contem_carregar_web_secret_key():
    conteudo = APP_PATH.read_text(encoding="utf-8")
    assert "_carregar_web_secret_key" in conteudo


def test_usa_secrets_token_hex():
    conteudo = APP_PATH.read_text(encoding="utf-8")
    assert "secrets.token_hex" in conteudo


def test_configura_permanent_session_lifetime():
    conteudo = APP_PATH.read_text(encoding="utf-8")
    assert "permanent_session_lifetime" in conteudo


def test_configura_session_cookie_httponly():
    conteudo = APP_PATH.read_text(encoding="utf-8")
    assert "SESSION_COOKIE_HTTPONLY" in conteudo


def test_configura_session_cookie_samesite():
    conteudo = APP_PATH.read_text(encoding="utf-8")
    assert "SESSION_COOKIE_SAMESITE" in conteudo


def test_configura_session_cookie_secure_por_env():
    conteudo = APP_PATH.read_text(encoding="utf-8")
    assert "SESSION_COOKIE_SECURE" in conteudo


def test_mantem_hmac_compare_digest():
    conteudo = APP_PATH.read_text(encoding="utf-8")
    assert "hmac.compare_digest" in conteudo


def test_contem_controle_rate_limit():
    conteudo = APP_PATH.read_text(encoding="utf-8")
    assert "_login_rate_limit" in conteudo or "_LOGIN_RATE_LIMIT" in conteudo

# ============================================================
# Functional tests — Flask test client
# ============================================================

def test_get_login_retorna_200(monkeypatch):
    monkeypatch.setenv("WEB_USERNAME", USERNAME)
    monkeypatch.setenv("WEB_PASSWORD", PASSWORD)
    monkeypatch.setenv("WEB_SECRET_KEY", SECRET_KEY)
    with app.test_client() as client:
        resp = client.get("/login")
    assert resp.status_code == 200


def test_rota_protegida_sem_login_redireciona(monkeypatch):
    monkeypatch.setenv("WEB_USERNAME", USERNAME)
    monkeypatch.setenv("WEB_PASSWORD", PASSWORD)
    monkeypatch.setenv("WEB_SECRET_KEY", SECRET_KEY)
    with app.test_client() as client:
        resp = client.get("/")
    assert resp.status_code == 302
    assert "/login" in resp.location


def test_login_credenciais_corretas_autentica(monkeypatch):
    monkeypatch.setenv("WEB_USERNAME", USERNAME)
    monkeypatch.setenv("WEB_PASSWORD", PASSWORD)
    monkeypatch.setenv("WEB_SECRET_KEY", SECRET_KEY)
    with app.test_client() as client:
        resp_login = client.post("/login", data={
            "username": USERNAME,
            "password": PASSWORD,
        })
        assert resp_login.status_code == 302
        resp_index = client.get("/")
    assert resp_index.status_code == 200


def test_logout_limpa_sessao(monkeypatch):
    monkeypatch.setenv("WEB_USERNAME", USERNAME)
    monkeypatch.setenv("WEB_PASSWORD", PASSWORD)
    monkeypatch.setenv("WEB_SECRET_KEY", SECRET_KEY)
    with app.test_client() as client:
        client.post("/login", data={
            "username": USERNAME,
            "password": PASSWORD,
        })
        resp_logout = client.get("/logout")
        assert resp_logout.status_code == 302
        resp_index = client.get("/")
    assert resp_index.status_code == 302


def test_login_invalido_nao_autentica(monkeypatch):
    monkeypatch.setenv("WEB_USERNAME", USERNAME)
    monkeypatch.setenv("WEB_PASSWORD", PASSWORD)
    monkeypatch.setenv("WEB_SECRET_KEY", SECRET_KEY)
    with app.test_client() as client:
        resp = client.post("/login", data={
            "username": USERNAME,
            "password": "senha_errada",
        })
        assert resp.status_code == 200
        resp_index = client.get("/")
    assert resp_index.status_code == 302


def test_muitas_tentativas_invalidas_ativam_bloqueio(monkeypatch):
    monkeypatch.setenv("WEB_USERNAME", USERNAME)
    monkeypatch.setenv("WEB_PASSWORD", PASSWORD)
    monkeypatch.setenv("WEB_SECRET_KEY", SECRET_KEY)
    monkeypatch.setenv("WEB_LOGIN_MAX_TENTATIVAS", "3")
    monkeypatch.setenv("WEB_LOGIN_BLOQUEIO_SEGUNDOS", BLOQUEIO_SEGUNDOS_TESTE)

    from web.app import _LOGIN_RATE_LIMIT
    _LOGIN_RATE_LIMIT.clear()

    with app.test_client() as client:
        for _ in range(3):
            client.post("/login", data={
                "username": "invalido",
                "password": "invalido",
            })
        resp = client.post("/login", data={
            "username": "invalido",
            "password": "invalido",
        })
    assert b"Muitas tentativas" in resp.data or "Muitas tentativas" in resp.get_data(as_text=True)

# ============================================================
# Security: app.py não contém tokens ou chamadas externas
# ============================================================

def test_app_nao_contem_url_monday():
    conteudo = APP_PATH.read_text(encoding="utf-8")
    assert "api.monday.com" not in conteudo


def test_app_nao_contem_requests_http():
    conteudo = APP_PATH.read_text(encoding="utf-8")
    assert "requests.post" not in conteudo
    assert "requests.get" not in conteudo
    assert "urllib.request" not in conteudo
    assert "httpx" not in conteudo

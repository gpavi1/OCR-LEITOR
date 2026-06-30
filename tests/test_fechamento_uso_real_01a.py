import pytest
import os
import re
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parents[1]

os.environ["WEB_USERNAME"] = "usuario_teste"
os.environ["WEB_PASSWORD"] = "senha_teste_segura"
os.environ["WEB_SECRET_KEY"] = "teste_secret_key_fixada_para_testes"
os.environ["MONDAY_API_TOKEN"] = ""
os.environ["MONDAY_BOARD_ID"] = ""

from web.app import app, status_label, _LOGIN_RATE_LIMIT


# ---------------------------------------------------------------------------
# PARTE 1 — Testes unitários de status_label
# ---------------------------------------------------------------------------

class TestStatusLabel:
    def test_pendente_integracao(self):
        assert status_label("pendente_integracao") == "Pendente integração"

    def test_pendente_revisao(self):
        assert status_label("pendente_revisao") == "Pendente revisão"

    def test_dry_run_apto(self):
        assert status_label("dry_run_apto") == "Simulação apta"

    def test_monday_envio_sucesso(self):
        assert status_label("monday_envio_sucesso") == "Enviado ao Monday"

    def test_erro_ocr(self):
        assert status_label("erro_ocr") == "Erro na leitura"

    def test_recebido(self):
        assert status_label("recebido") == "Recebido"

    def test_processando(self):
        assert status_label("processando") == "Processando"

    def test_integrado(self):
        assert status_label("integrado") == "Integrado"

    def test_falha_integracao(self):
        assert status_label("falha_integracao") == "Falha na integração"

    def test_dry_run_bloqueado(self):
        assert status_label("dry_run_bloqueado") == "Simulação bloqueada"

    def test_dry_run_erro(self):
        assert status_label("dry_run_erro") == "Simulação com erro"

    def test_monday_envio_falha(self):
        assert status_label("monday_envio_falha") == "Falha no Monday"

    def test_monday_envio_bloqueado(self):
        assert status_label("monday_envio_bloqueado") == "Envio bloqueado"

    def test_status_desconhecido_fallback(self):
        result = status_label("status_desconhecido")
        assert "_" not in result
        assert result == "Status Desconhecido"


# ---------------------------------------------------------------------------
# PARTE 2 — Testes de templates (render com app.test_client autenticado)
# ---------------------------------------------------------------------------

def _login(client):
    _LOGIN_RATE_LIMIT.clear()
    resp_get = client.get("/login")
    import re, html as html_mod
    match = re.search(rb'name="csrf_token"\s+value="([^"]+)"', resp_get.data)
    ct = html_mod.unescape(match.group(1).decode("utf-8")) if match else ""
    client.post("/login", data={
        "csrf_token": ct,
        "username": "usuario_teste",
        "password": "senha_teste_segura",
    })

class TestTemplatesStatusLabel:
    def test_integracoes_nao_contem_status_cru(self):
        with app.test_client() as client:
            _login(client)
            resp = client.get("/integracoes")
        html = resp.get_data(as_text=True)
        assert "Status: pendente_integracao" not in html

    def test_integracoes_usa_status_label(self):
        with app.test_client() as client:
            _login(client)
            resp = client.get("/integracoes")
        html = resp.get_data(as_text=True)
        assert "status_label" not in html

    def test_historico_integracoes_usa_status_label(self):
        with app.test_client() as client:
            _login(client)
            resp = client.get("/integracoes/historico")
        html = resp.get_data(as_text=True)
        assert "status_label" not in html
        assert "badge status-" in html

    def test_dashboard_integracoes_usa_status_label(self):
        with app.test_client() as client:
            _login(client)
            resp = client.get("/integracoes/dashboard")
        html = resp.get_data(as_text=True)
        assert "status_label" not in html
        assert "badge status-" in html

    def test_integracoes_badge_tem_classe_status(self):
        with app.test_client() as client:
            _login(client)
            resp = client.get("/integracoes")
        html = resp.get_data(as_text=True)
        assert 'class="badge status-' in html

    def test_config_integracoes_contem_guia(self):
        with app.test_client() as client:
            _login(client)
            resp = client.get("/integracoes/configuracao")
        html = resp.get_data(as_text=True)
        assert "Como conectar o OCR-LEITOR ao Monday" in html

    def test_config_integracoes_contem_aviso_seguranca(self):
        with app.test_client() as client:
            _login(client)
            resp = client.get("/integracoes/configuracao")
        html = resp.get_data(as_text=True)
        assert "Nunca cole tokens" in html


# ---------------------------------------------------------------------------
# PARTE 3 — Testes de CSS
# ---------------------------------------------------------------------------

class TestCssClasses:
    CSS_PATH = BASE_DIR / "web" / "static" / "style.css"

    @pytest.fixture
    def css_text(self):
        return self.CSS_PATH.read_text(encoding="utf-8")

    def _test_class_exists(self, css_text, class_name):
        assert f".{class_name}" in css_text

    def test_css_recebido(self, css_text):
        self._test_class_exists(css_text, "status-recebido")

    def test_css_integrado(self, css_text):
        self._test_class_exists(css_text, "status-integrado")

    def test_css_dry_run_apto(self, css_text):
        self._test_class_exists(css_text, "status-dry_run_apto")

    def test_css_monday_envio_sucesso(self, css_text):
        self._test_class_exists(css_text, "status-monday_envio_sucesso")

    def test_css_processando(self, css_text):
        self._test_class_exists(css_text, "status-processando")

    def test_css_falha_integracao(self, css_text):
        self._test_class_exists(css_text, "status-falha_integracao")

    def test_css_dry_run_bloqueado(self, css_text):
        self._test_class_exists(css_text, "status-dry_run_bloqueado")

    def test_css_dry_run_erro(self, css_text):
        self._test_class_exists(css_text, "status-dry_run_erro")

    def test_css_monday_envio_falha(self, css_text):
        self._test_class_exists(css_text, "status-monday_envio_falha")

    def test_css_monday_envio_bloqueado(self, css_text):
        self._test_class_exists(css_text, "status-monday_envio_bloqueado")

    def test_css_btn_simular_monday(self, css_text):
        self._test_class_exists(css_text, "btn-simular-monday")

    def test_css_btn_enviar_monday(self, css_text):
        self._test_class_exists(css_text, "btn-enviar-monday")


# ---------------------------------------------------------------------------
# PARTE 4 — Testes do guia de integração
# ---------------------------------------------------------------------------

class TestGuiaIntegracao:
    GUIA_PATH = BASE_DIR / "docs" / "operacao" / "GUIA_INTEGRACAO_OCR_MONDAY.md"

    def test_guia_existe(self):
        assert self.GUIA_PATH.is_file()

    def test_guia_contem_monday_board_id(self):
        texto = self.GUIA_PATH.read_text(encoding="utf-8")
        assert "MONDAY_BOARD_ID" in texto

    def test_guia_contem_monday_column_empresa(self):
        texto = self.GUIA_PATH.read_text(encoding="utf-8")
        assert "MONDAY_COLUMN_EMPRESA" in texto

    def test_guia_nao_contem_token_real(self):
        texto = self.GUIA_PATH.read_text(encoding="utf-8")
        assert "eyJhbGci" not in texto
        assert "Authorization:" not in texto
        assert "Bearer " not in texto
        assert "OcrAppLocal" not in texto

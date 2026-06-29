import os
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]
APP_PATH = PROJECT_ROOT / "web" / "app.py"
TEMPLATE_PATH = PROJECT_ROOT / "web" / "templates" / "config_integracoes.html"
BASE_TEMPLATE_PATH = PROJECT_ROOT / "web" / "templates" / "base.html"
TEST_FILE_PATH = Path(__file__).resolve()


def _ler_app():
    return APP_PATH.read_text(encoding="utf-8")


def _ler_template():
    return TEMPLATE_PATH.read_text(encoding="utf-8")


def _ler_base():
    return BASE_TEMPLATE_PATH.read_text(encoding="utf-8")


def _ler_teste():
    return TEST_FILE_PATH.read_text(encoding="utf-8")


class TestRotaConfig:
    def test_1_app_contem_rota_configuracao(self):
        conteudo = _ler_app()
        assert '"/integracoes/configuracao"' in conteudo

    def test_2_app_contem_plataformas_integracao(self):
        conteudo = _ler_app()
        assert "PLATAFORMAS_INTEGRACAO" in conteudo

    def test_3_app_contem_monday(self):
        conteudo = _ler_app()
        assert "Monday.com" in conteudo

    def test_4_app_contem_google_sheets(self):
        conteudo = _ler_app()
        assert "Google Sheets" in conteudo

    def test_5_app_contem_erp_api(self):
        conteudo = _ler_app()
        assert "ERP / API" in conteudo and "API pr" in conteudo

    def test_6_app_contem_classificar_variavel_config(self):
        conteudo = _ler_app()
        assert "_classificar_variavel_config" in conteudo

    def test_7_app_contem_status_variaveis_plataforma(self):
        conteudo = _ler_app()
        assert "_status_variaveis_plataforma" in conteudo

    def test_8_app_contem_montar_status_plataformas_integracao(self):
        conteudo = _ler_app()
        assert "_montar_status_plataformas_integracao" in conteudo

    def test_9_template_config_integracoes_existe(self):
        assert TEMPLATE_PATH.exists()

    def test_10_template_contem_titulo(self):
        conteudo = _ler_template()
        assert "Configura" in conteudo and "Integra" in conteudo

    def test_11_template_contem_aviso_somente_leitura(self):
        conteudo = _ler_template()
        assert "somente leitura" in conteudo

    def test_12_template_nao_contem_input(self):
        conteudo = _ler_template()
        assert "<input" not in conteudo

    def test_13_template_nao_contem_textarea(self):
        conteudo = _ler_template()
        assert "<textarea" not in conteudo

    def test_14_template_nao_contem_method_post(self):
        conteudo = _ler_template()
        assert 'method="post"' not in conteudo

    def test_15_template_nao_contem_salvar(self):
        conteudo = _ler_template()
        assert "Salvar" not in conteudo

    def test_16_template_nao_contem_enviar(self):
        conteudo = _ler_template()
        assert "Enviar" not in conteudo

    def test_17_template_nao_contem_testar(self):
        conteudo = _ler_template()
        assert "Testar" not in conteudo

    def test_18_template_nao_contem_var_valor(self):
        conteudo = _ler_template()
        assert "var.valor" not in conteudo

    def test_19_base_contem_link_configuracao(self):
        conteudo = _ler_base()
        assert "/integracoes/configuracao" in conteudo

    def test_20_base_contem_texto_config(self):
        conteudo = _ler_base()
        assert "Config" in conteudo


class TestClassificador:
    def test_21_none_retorna_ausente(self):
        from web.app import _classificar_variavel_config
        assert _classificar_variavel_config(None) == "AUSENTE"

    def test_22_vazio_retorna_ausente(self):
        from web.app import _classificar_variavel_config
        assert _classificar_variavel_config("") == "AUSENTE"

    def test_23_espacos_retorna_ausente(self):
        from web.app import _classificar_variavel_config
        assert _classificar_variavel_config("   ") == "AUSENTE"

    def test_24_cole_seu_token_retorna_placeholder(self):
        from web.app import _classificar_variavel_config
        assert _classificar_variavel_config("cole_seu_token_aqui") == "PLACEHOLDER"

    def test_25_exemplo_token_retorna_placeholder(self):
        from web.app import _classificar_variavel_config
        assert _classificar_variavel_config("EXEMPLO_TOKEN") == "PLACEHOLDER"

    def test_26_valor_real_retorna_configurado(self):
        from web.app import _classificar_variavel_config
        assert _classificar_variavel_config("token_autentico_123") == "CONFIGURADO"


class TestSeguranca:
    def test_27_status_variaveis_nao_retorna_valor_real(self, monkeypatch):
        monkeypatch.setenv("MONDAY_API_TOKEN", "token_super_secreto_123")
        from web.app import _status_variaveis_plataforma
        plataforma = {
            "variaveis": [
                {"chave": "MONDAY_API_TOKEN", "rotulo": "Token", "sensivel": True}
            ]
        }
        resultado = _status_variaveis_plataforma(plataforma)
        for var in resultado:
            assert "valor" not in var
            assert var.get("token_super_secreto_123") is None

    def test_28_montagem_nao_retorna_token_real(self, monkeypatch):
        monkeypatch.setenv("MONDAY_API_TOKEN", "outro_token_secreto_456")
        from web.app import _montar_status_plataformas_integracao
        resultado = _montar_status_plataformas_integracao()
        for plataforma in resultado:
            for var in plataforma["variaveis"]:
                assert "valor" not in var

    def test_29_nenhum_jwt_real_no_teste(self):
        conteudo = _ler_teste()
        linhas = conteudo.splitlines()
        alvo = "eyJ"
        ocorrencias = [l for l in linhas if alvo in l]
        for linha in ocorrencias:
            assert "assert" not in linha

    def test_30_nenhum_authorization_no_teste(self):
        conteudo = _ler_teste()
        linhas = conteudo.splitlines()
        alvo = "Authorization:"
        ocorrencias = [l for l in linhas if alvo in l]
        for linha in ocorrencias:
            assert "assert" not in linha
            assert not linha.strip().startswith("#")

    def test_31_nenhum_bearer_no_teste(self):
        conteudo = _ler_teste()
        linhas = conteudo.splitlines()
        alvo = "Bearer"
        ocorrencias = [l for l in linhas if alvo in l]
        for linha in ocorrencias:
            assert "assert" not in linha
            assert not linha.strip().startswith("#")

    def test_32_nenhum_request_ou_urllib_no_teste(self):
        conteudo = _ler_teste()
        linhas = conteudo.splitlines()
        ocorrencias = [l for l in linhas
                       if "import" in l.lower() and "requests" in l.lower()]
        for linha in ocorrencias:
            assert "assert" not in linha
            assert not linha.strip().startswith("#")

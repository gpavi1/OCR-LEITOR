import builtins
import sys
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parents[1]
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

SCRIPT_PATH = BASE_DIR / "scripts" / "configurar_ambiente.py"
ENV_EXAMPLE = BASE_DIR / ".env.example"
MENU_PATH = BASE_DIR / "scripts" / "menu_operacao.py"
REAL_ENV = BASE_DIR / ".env"


from scripts import configurar_ambiente as cfg


def _config_completa():
    return {
        "WEB_SECRET_KEY": "secret_ficticio_com_tamanho_seguro",
        "WEB_USERNAME": "admin",
        "WEB_PASSWORD": "senha_ficticia",
        "DB_HOST": "localhost",
        "DB_PORT": "3306",
        "DB_NAME": "ocr_leitor",
        "DB_USER": "ocr_app",
        "DB_PASSWORD": "senha_db_ficticia",
        "MONDAY_API_TOKEN": "token_ficticio_seguro",
        "MONDAY_BOARD_ID": "123456789",
        "MONDAY_COLUMN_EMPRESA": "col_empresa",
        "MONDAY_COLUMN_NUMERO_NF": "col_numero_nf",
        "MONDAY_COLUMN_CHAVE_ACESSO": "col_chave_acesso",
        "MONDAY_COLUMN_VENCIMENTO": "col_vencimento",
        "MONDAY_COLUMN_VALOR_TOTAL": "col_valor_total",
        "MONDAY_COLUMN_OBSERVACAO": "col_observacao",
    }


def test_1_script_configurar_ambiente_existe():
    assert SCRIPT_PATH.is_file()


def test_2_carregar_env_le_arquivo(tmp_path):
    env_path = tmp_path / ".env"
    env_path.write_text("DB_HOST=localhost\nDB_PORT=3306\n", encoding="utf-8")
    assert cfg.carregar_env(env_path) == {"DB_HOST": "localhost", "DB_PORT": "3306"}


def test_3_salvar_env_grava_pares_chave_valor(tmp_path):
    env_path = tmp_path / ".env"
    dados = _config_completa()
    cfg.salvar_env(env_path, dados)
    conteudo = env_path.read_text(encoding="utf-8")
    assert "DB_HOST=localhost" in conteudo
    assert "MONDAY_API_TOKEN=token_ficticio_seguro" in conteudo


def test_4_criar_env_do_zero_em_tmp_path(tmp_path):
    env_path = tmp_path / ".env"
    cfg.salvar_env(env_path, _config_completa())
    assert env_path.is_file()


def test_5_preserva_valor_existente_valido():
    existentes = _config_completa()
    resultado = cfg.montar_configuracao_interativa(
        existentes,
        input_func=lambda _prompt: "",
        getpass_func=lambda _prompt: "",
    )
    assert resultado["MONDAY_BOARD_ID"] == existentes["MONDAY_BOARD_ID"]
    assert resultado["DB_PASSWORD"] == existentes["DB_PASSWORD"]


def test_6_cria_backup_antes_de_alterar_env_existente(tmp_path):
    env_path = tmp_path / ".env"
    env_path.write_text("DB_HOST=localhost\n", encoding="utf-8")
    backup = cfg.criar_backup_env(env_path)
    assert backup is not None
    assert backup.is_file()
    assert backup.name.startswith(".env.backup_")
    assert backup.read_text(encoding="utf-8") == "DB_HOST=localhost\n"


def test_7_dry_run_nao_grava_arquivo(tmp_path):
    env_path = tmp_path / ".env"
    retorno = cfg.main(["--env-path", str(env_path), "--dry-run"])
    assert retorno == 0
    assert not env_path.exists()


def test_8_web_secret_key_gerado_quando_ausente():
    resultado = cfg.montar_configuracao_interativa({}, interativo=False)
    assert resultado["WEB_SECRET_KEY"]
    assert not cfg.eh_placeholder(resultado["WEB_SECRET_KEY"])


def test_9_monday_api_token_e_sensivel():
    assert "MONDAY_API_TOKEN" in cfg.CHAVES_SENSIVEIS


def test_10_resumo_mascara_monday_api_token():
    resumo = cfg.gerar_resumo_configuracao(_config_completa())
    assert "MONDAY_API_TOKEN=***guro" in resumo
    assert "MONDAY_API_TOKEN=token_ficticio_seguro" not in resumo


def test_11_resumo_mascara_db_password():
    resumo = cfg.gerar_resumo_configuracao(_config_completa())
    assert "DB_PASSWORD=********" in resumo
    assert "senha_db_ficticia" not in resumo


def test_12_placeholder_detectado():
    assert cfg.eh_placeholder("")
    assert cfg.eh_placeholder("placeholder")
    assert cfg.eh_placeholder("trocar_depois")
    assert cfg.eh_placeholder("coloque_aqui")
    assert cfg.eh_placeholder("seu_token")
    assert cfg.eh_placeholder("sua_senha")
    assert cfg.eh_placeholder("changeme")
    assert cfg.eh_placeholder("example_value")
    assert cfg.eh_placeholder("exemplo_valor")
    assert not cfg.eh_placeholder("valor_configurado")


def test_13_monday_api_key_nao_aparece_env_example():
    old_key = "MONDAY_" + "API_KEY"
    assert old_key not in ENV_EXAMPLE.read_text(encoding="utf-8")


def test_14_monday_api_token_aparece_env_example():
    assert "MONDAY_API_TOKEN=" in ENV_EXAMPLE.read_text(encoding="utf-8")


def test_15_todas_colunas_monday_aparecem_env_example():
    conteudo = ENV_EXAMPLE.read_text(encoding="utf-8")
    for chave in [
        "MONDAY_COLUMN_EMPRESA",
        "MONDAY_COLUMN_NUMERO_NF",
        "MONDAY_COLUMN_CHAVE_ACESSO",
        "MONDAY_COLUMN_VENCIMENTO",
        "MONDAY_COLUMN_VALOR_TOTAL",
        "MONDAY_COLUMN_OBSERVACAO",
    ]:
        assert f"{chave}=" in conteudo


def test_16_variaveis_web_aparecem_env_example():
    conteudo = ENV_EXAMPLE.read_text(encoding="utf-8")
    assert "WEB_SECRET_KEY=" in conteudo
    assert "WEB_USERNAME=admin" in conteudo
    assert "WEB_PASSWORD=" in conteudo


def test_17_variaveis_mysql_aparecem_env_example():
    conteudo = ENV_EXAMPLE.read_text(encoding="utf-8")
    assert "DB_HOST=localhost" in conteudo
    assert "DB_PORT=3306" in conteudo
    assert "DB_NAME=ocr_leitor" in conteudo
    assert "DB_USER=ocr_app" in conteudo
    assert "DB_PASSWORD=" in conteudo


def test_18_script_nao_contem_requests():
    source = SCRIPT_PATH.read_text(encoding="utf-8")
    assert "requests" not in source.lower()


def test_19_script_nao_contem_urllib():
    source = SCRIPT_PATH.read_text(encoding="utf-8")
    assert "urllib" not in source.lower()


def test_20_script_nao_contem_token_real():
    source = SCRIPT_PATH.read_text(encoding="utf-8")
    assert "token_ficticio_seguro" not in source
    assert "senha_db_ficticia" not in source


def test_21_menu_operacional_contem_nova_opcao():
    conteudo = MENU_PATH.read_text(encoding="utf-8")
    assert "Configurar ambiente (Monday + Web + MySQL)" in conteudo


def test_22_menu_operacional_chama_configurar_ambiente():
    conteudo = MENU_PATH.read_text(encoding="utf-8")
    assert "configurar_ambiente.py" in conteudo


def test_23_validacao_acusa_ausencia_monday_board_id():
    dados = _config_completa()
    dados["MONDAY_BOARD_ID"] = ""
    bloqueios = cfg.validar_configuracao(dados)
    assert "MONDAY_BOARD_ID ausente ou placeholder." in bloqueios


def test_24_validacao_acusa_ausencia_coluna_obrigatoria():
    dados = _config_completa()
    dados["MONDAY_COLUMN_EMPRESA"] = ""
    bloqueios = cfg.validar_configuracao(dados)
    assert "MONDAY_COLUMN_EMPRESA ausente ou placeholder." in bloqueios


def test_25_validacao_aceita_configuracao_completa_ficticia():
    assert cfg.validar_configuracao(_config_completa()) == []


def test_26_nenhum_teste_altera_env_real(tmp_path):
    env_path = tmp_path / ".env"
    cfg.salvar_env(env_path, _config_completa())
    assert env_path != REAL_ENV
    assert str(tmp_path) in str(env_path)


def test_27_main_confirmar_cria_env_e_nao_toca_env_real(tmp_path):
    env_path = tmp_path / ".env"
    respostas = iter([
        "senha_web_ficticia",
        "senha_db_ficticia",
        "token_ficticio_seguro",
        "123456789",
        "col_empresa",
        "col_numero_nf",
        "col_chave_acesso",
        "col_vencimento",
        "col_valor_total",
        "col_observacao",
    ])

    def input_func(prompt):
        if "WEB_USERNAME" in prompt:
            return ""
        if "DB_HOST" in prompt:
            return ""
        if "DB_PORT" in prompt:
            return ""
        if "DB_NAME" in prompt:
            return ""
        if "DB_USER" in prompt:
            return ""
        return next(respostas)

    original_input = builtins.input
    original_getpass = cfg.getpass.getpass
    try:
        builtins.input = input_func
        cfg.getpass.getpass = lambda prompt: next(respostas)
        retorno = cfg.main(["--env-path", str(env_path), "--confirmar"])
    finally:
        builtins.input = original_input
        cfg.getpass.getpass = original_getpass

    assert retorno == 0
    assert env_path.is_file()
    assert env_path != REAL_ENV


def test_28_sem_confirmar_nao_grava_env(tmp_path):
    env_path = tmp_path / ".env"
    retorno = cfg.main(["--env-path", str(env_path), "--dry-run"])
    assert retorno == 0
    assert not env_path.exists()

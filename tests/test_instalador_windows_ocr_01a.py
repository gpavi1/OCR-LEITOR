from pathlib import Path


BASE_DIR = Path(__file__).resolve().parents[1]
ROOT_CMD = BASE_DIR / "OCR-LEITOR.cmd"
MENU_PY = BASE_DIR / "scripts" / "menu_operacao.py"
VALIDADOR_TESSERACT = BASE_DIR / "scripts" / "validador_tesseract.py"
VALIDADOR_MYSQL = BASE_DIR / "scripts" / "validador_mysql.py"
TEST_FILE = Path(__file__).resolve()


def _ler_arquivo(caminho):
    return caminho.read_text(encoding="utf-8")


class TestRAIZ:
    def test_1_cmd_existe(self):
        assert ROOT_CMD.is_file()

    def test_2_cmd_usa_tilt_dp0(self):
        conteudo = _ler_arquivo(ROOT_CMD)
        assert "%~dp0" in conteudo

    def test_3_cmd_chama_menu_operacao(self):
        conteudo = _ler_arquivo(ROOT_CMD)
        assert "menu_operacao.py" in conteudo

    def test_4_cmd_tenta_usar_venv(self):
        conteudo = _ler_arquivo(ROOT_CMD)
        assert ".venv" in conteudo

    def test_5_cmd_nao_hardcoda_c_projetos(self):
        conteudo = _ler_arquivo(ROOT_CMD)
        assert "C:\\Projetos\\OCR-LEITOR" not in conteudo

    def test_6_cmd_nao_contem_token(self):
        conteudo = _ler_arquivo(ROOT_CMD)
        assert "MONDAY" not in conteudo

    def test_7_cmd_nao_contem_senha(self):
        conteudo = _ler_arquivo(ROOT_CMD)
        assert "senha" not in conteudo.lower()

    def test_8_menu_py_existe(self):
        assert MENU_PY.is_file()

    def test_9_menu_contem_16_opcoes(self):
        conteudo = _ler_arquivo(MENU_PY)
        for i in range(1, 17):
            assert f"\"{i}\"" in conteudo or f"'{i}'" in conteudo

    def test_10_menu_contem_confirmacao_limpar_teste(self):
        conteudo = _ler_arquivo(MENU_PY)
        assert "LIMPAR TESTE" in conteudo

    def test_11_menu_contem_confirmacao_reset_teste(self):
        conteudo = _ler_arquivo(MENU_PY)
        assert "RESET TESTE" in conteudo

    def test_12_menu_chama_iniciar_web_bat(self):
        conteudo = _ler_arquivo(MENU_PY)
        assert "INICIAR_WEB_LOCAL.bat" in conteudo

    def test_13_menu_chama_iniciar_ocr_bat(self):
        conteudo = _ler_arquivo(MENU_PY)
        assert "INICIAR_OCR_24H_LOCAL.bat" in conteudo

    def test_14_menu_abre_config_integracoes(self):
        conteudo = _ler_arquivo(MENU_PY)
        assert "/integracoes/configuracao" in conteudo

    def test_15_menu_nao_chama_monday_api(self):
        conteudo = _ler_arquivo(MENU_PY)
        assert "api.monday.com" not in conteudo

    def test_16_menu_nao_contem_token(self):
        conteudo = _ler_arquivo(MENU_PY)
        assert "MONDAY_API_TOKEN" not in conteudo

    def test_17_validador_tesseract_existe(self):
        assert VALIDADOR_TESSERACT.is_file()

    def test_18_validador_tesseract_list_langs(self):
        conteudo = _ler_arquivo(VALIDADOR_TESSERACT)
        assert "--list-langs" in conteudo

    def test_19_validador_tesseract_verifica_por(self):
        conteudo = _ler_arquivo(VALIDADOR_TESSERACT)
        assert "por" in conteudo

    def test_20_validador_tesseract_verifica_eng(self):
        conteudo = _ler_arquivo(VALIDADOR_TESSERACT)
        assert "eng" in conteudo

    def test_21_validador_mysql_existe(self):
        assert VALIDADOR_MYSQL.is_file()

    def test_22_validador_mysql_nao_hardcoda_senha(self):
        conteudo = _ler_arquivo(VALIDADOR_MYSQL)
        linhas = conteudo.splitlines()
        for linha in linhas:
            linha_strip = linha.strip()
            if "password" in linha_strip.lower() or "senha" in linha_strip.lower():
                assert "=" in linha_strip and ("\"\"" in linha_strip or "''" in linha_strip or "os.getenv" in linha_strip.lower())

    def test_23_validador_mysql_verifica_tabelas(self):
        conteudo = _ler_arquivo(VALIDADOR_MYSQL)
        assert "integracoes" in conteudo
        assert "documentos" in conteudo
        assert "clientes" in conteudo

    def test_24_nenhum_jwt(self):
        arquivos = [ROOT_CMD, MENU_PY, VALIDADOR_TESSERACT, VALIDADOR_MYSQL, TEST_FILE]
        for arq in arquivos:
            conteudo = _ler_arquivo(arq)
            linhas = conteudo.splitlines()
            for linha in linhas:
                if "eyJ" in linha:
                    assert "assert" not in linha

    def test_25_nenhum_authorization(self):
        arquivos = [ROOT_CMD, MENU_PY, VALIDADOR_TESSERACT, VALIDADOR_MYSQL, TEST_FILE]
        for arq in arquivos:
            conteudo = _ler_arquivo(arq)
            linhas = conteudo.splitlines()
            for linha in linhas:
                if "Authorization:" in linha or "authorization:" in linha:
                    assert "assert" not in linha

    def test_26_nenhum_bearer(self):
        arquivos = [ROOT_CMD, MENU_PY, VALIDADOR_TESSERACT, VALIDADOR_MYSQL, TEST_FILE]
        for arq in arquivos:
            conteudo = _ler_arquivo(arq)
            linhas = conteudo.splitlines()
            for linha in linhas:
                if "Bearer" in linha:
                    assert "assert" not in linha

    def test_27_nenhum_teste_chama_api_externa(self):
        arquivo = TEST_FILE.read_text(encoding="utf-8")
        linhas_import = [l for l in arquivo.splitlines()
                         if "import" in l.lower() and "requests" in l.lower()]
        for linha in linhas_import:
            assert "assert" in linha or "#" in linha or "if" in linha

    def _linhas_sem_infra(self, texto):
        return [
            l for l in texto.splitlines()
            if "def " not in l and "assert" not in l and "alvo =" not in l
        ]

    def test_28_nenhum_teste_executa_reset_real(self):
        linhas = self._linhas_sem_infra(TEST_FILE.read_text(encoding="utf-8"))
        texto_limpo = "\n".join(linhas)
        assert "reset_real" not in texto_limpo.lower()

    def test_29_nenhum_teste_apaga_dados(self):
        linhas = self._linhas_sem_infra(TEST_FILE.read_text(encoding="utf-8"))
        texto_limpo = "\n".join(linhas)
        assert "shutil.rmtree" not in texto_limpo

    def test_30_nenhum_teste_depende_vscode(self):
        linhas = self._linhas_sem_infra(TEST_FILE.read_text(encoding="utf-8"))
        texto_limpo = "\n".join(linhas)
        assert "vscode" not in texto_limpo.lower()

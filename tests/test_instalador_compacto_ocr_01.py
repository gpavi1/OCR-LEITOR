from pathlib import Path

from scripts import instalar_ocr
from scripts.caminhos_instalacao import CAMINHO_PADRAO_CLIENTE, CAMINHO_PADRAO_DEMO


BASE_DIR = Path(__file__).resolve().parents[1]
CMD = BASE_DIR / "INSTALAR-OCR-LEITOR.cmd"
SCRIPT = BASE_DIR / "scripts" / "instalar_ocr.py"
MENU = BASE_DIR / "scripts" / "menu_operacao.py"
DOC = BASE_DIR / "docs" / "operacao" / "INSTALADOR_COMPACTO_OCR.md"
LEIA = BASE_DIR / "LEIA_PRIMEIRO.txt"


def _ler(path):
    return path.read_text(encoding="utf-8")


def test_cmd_instalador_existe():
    assert CMD.is_file()


def test_cmd_chama_scripts_instalar_ocr_py():
    assert r"scripts\instalar_ocr.py" in _ler(CMD)


def test_cmd_nao_contem_caminho_fixo_do_desenvolvedor():
    conteudo = _ler(CMD)

    assert "C:\\Users\\Gabriel" not in conteudo
    assert "OneDrive\\Desktop\\Prod-OCR" not in conteudo


def test_script_instalador_existe():
    assert SCRIPT.is_file()


def test_script_possui_subcomando_demo():
    assert '"demo"' in _ler(SCRIPT)


def test_script_possui_subcomando_cliente():
    assert '"cliente"' in _ler(SCRIPT)


def test_script_possui_subcomando_update():
    assert '"update"' in _ler(SCRIPT)


def test_script_possui_subcomando_verificar():
    assert '"verificar"' in _ler(SCRIPT)


def test_modo_demo_usa_caminho_padrao_demo():
    acoes = instalar_ocr.montar_acoes_demo()

    assert CAMINHO_PADRAO_DEMO == r"C:\OCR-LEITOR-DEMO"
    assert any(acao.get("destino") == CAMINHO_PADRAO_DEMO for acao in acoes)


def test_modo_cliente_usa_caminho_padrao_cliente():
    acoes = instalar_ocr.montar_acoes_cliente()

    assert CAMINHO_PADRAO_CLIENTE == r"C:\OCR-LEITOR"
    assert any(acao.get("destino") == CAMINHO_PADRAO_CLIENTE for acao in acoes)


def test_modo_update_exige_instalacao_existente(tmp_path):
    acoes = instalar_ocr.montar_acoes_update(tmp_path)

    erros = [acao["descricao"] for acao in acoes if acao["tipo"] == "erro"]

    assert "Update exige instalação existente." in erros


def test_modo_update_exige_backup(tmp_path):
    acoes = instalar_ocr.montar_acoes_update(tmp_path)

    assert any(acao["tipo"] == "backup" for acao in acoes)


def test_modo_update_preserva_env(tmp_path):
    acoes = instalar_ocr.montar_acoes_update(tmp_path)

    assert any(acao.get("alvo") == ".env" for acao in acoes)


def test_modo_update_preserva_pastas_operacionais(tmp_path):
    acoes = instalar_ocr.montar_acoes_update(tmp_path)
    preservados = {acao.get("alvo") for acao in acoes if acao["tipo"] == "preservar"}

    for pasta in ["input", "output", "processed", "erro", "logs", "exports", "backups"]:
        assert pasta in preservados


def test_modo_demo_cria_env_ficticio_com_confirmar_em_tmp_path(tmp_path):
    destino = tmp_path / "demo"

    retorno = instalar_ocr.main(["demo", "--destino", str(destino), "--confirmar"])

    assert retorno == 0
    env = destino / ".env"
    assert env.is_file()
    conteudo = env.read_text(encoding="utf-8")
    assert "DB_NAME=ocr_leitor_demo" in conteudo
    assert "MONDAY_API_TOKEN=" in conteudo


def test_dry_run_nao_altera_arquivos(tmp_path):
    destino = tmp_path / "demo"

    retorno = instalar_ocr.main(["demo", "--destino", str(destino), "--dry-run"])

    assert retorno == 0
    assert not destino.exists()


def test_sem_confirmar_nao_executa_alteracoes_reais(tmp_path):
    destino = tmp_path / "demo"

    retorno = instalar_ocr.main(["demo", "--destino", str(destino)])

    assert retorno == 0
    assert not destino.exists()


def test_script_nao_contem_requests():
    assert "requests" not in _ler(SCRIPT)


def test_script_nao_contem_urllib():
    assert "urllib" not in _ler(SCRIPT)


def test_script_nao_contem_token_real():
    conteudo = _ler(SCRIPT)

    assert "eyJ" + "hbGci" not in conteudo
    assert "Author" + "ization:" not in conteudo
    assert "Bearer" + " " not in conteudo


def test_menu_operacional_cita_instalador_compacto():
    assert "Instalador compacto / modos demo, cliente e update" in _ler(MENU)


def test_documentacao_instalador_existe():
    assert DOC.is_file()


def test_documentacao_cita_demo():
    assert "demo" in _ler(DOC).lower()


def test_documentacao_cita_cliente():
    assert "cliente" in _ler(DOC).lower()


def test_documentacao_cita_update():
    assert "update" in _ler(DOC).lower()


def test_leia_primeiro_cita_instalar_ocr_leitor_cmd():
    assert "INSTALAR-OCR-LEITOR.cmd" in _ler(LEIA)


def test_leia_primeiro_cita_ocr_leitor_cmd():
    assert "OCR-LEITOR.cmd" in _ler(LEIA)


def test_instalador_nao_altera_conectores():
    assert "conectores/" not in _ler(SCRIPT)
    assert "conectores\\" not in _ler(SCRIPT)


def test_instalador_nao_altera_banco_schema():
    assert "database/schema.sql" not in _ler(SCRIPT)
    assert "database\\schema.sql" not in _ler(SCRIPT)


def test_instalador_nao_altera_web():
    assert "web/app.py" not in _ler(SCRIPT)
    assert "web\\app.py" not in _ler(SCRIPT)


def test_modo_verificar_monta_validacoes_existentes():
    acoes = instalar_ocr.montar_acoes_verificar(BASE_DIR)
    scripts = {acao["script"] for acao in acoes}

    assert "doctor_instalacao.py" in scripts
    assert "validador_tesseract.py" in scripts
    assert "validador_mysql.py" in scripts


def test_update_bloqueia_pasta_demo():
    acoes = instalar_ocr.montar_acoes_update(CAMINHO_PADRAO_DEMO)

    assert any("pasta demo" in acao["descricao"] for acao in acoes if acao["tipo"] == "erro")

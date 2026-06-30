from pathlib import Path

from scripts import caminhos_instalacao
from scripts.caminhos_instalacao import (
    CAMINHO_PADRAO_CLIENTE,
    CAMINHO_PADRAO_DEMO,
    classificar_caminho_instalacao,
    detectar_instalacao_existente,
    esta_em_desktop,
    esta_em_downloads,
    esta_em_onedrive,
    esta_em_temp,
    obter_estrutura_pastas_recomendada,
)
from scripts.doctor_instalacao import STATUS_AVISO, _verificar_caminho_instalacao


BASE_DIR = Path(__file__).resolve().parents[1]
MODULO = BASE_DIR / "scripts" / "caminhos_instalacao.py"
DOCTOR = BASE_DIR / "scripts" / "doctor_instalacao.py"
DOCUMENTACAO = BASE_DIR / "docs" / "operacao" / "CAMINHOS_INSTALACAO_OCR.md"


def _ler(path):
    return path.read_text(encoding="utf-8")


def test_modulo_caminhos_instalacao_existe():
    assert MODULO.is_file()
    assert caminhos_instalacao.__file__


def test_caminho_padrao_cliente():
    assert CAMINHO_PADRAO_CLIENTE == r"C:\OCR-LEITOR"


def test_caminho_padrao_demo():
    assert CAMINHO_PADRAO_DEMO == r"C:\OCR-LEITOR-DEMO"


def test_esta_em_onedrive_detecta_onedrive():
    assert esta_em_onedrive(r"C:\Users\Cliente\OneDrive\OCR-LEITOR")


def test_esta_em_desktop_detecta_desktop():
    assert esta_em_desktop(r"C:\Users\Cliente\Desktop\OCR-LEITOR")


def test_esta_em_desktop_detecta_area_de_trabalho():
    assert esta_em_desktop(r"C:\Users\Cliente\Area de Trabalho\OCR-LEITOR")
    assert esta_em_desktop(r"C:\Users\Cliente\Área de Trabalho\OCR-LEITOR")


def test_esta_em_downloads_detecta_downloads():
    assert esta_em_downloads(r"C:\Users\Cliente\Downloads\OCR-LEITOR")


def test_esta_em_temp_detecta_temp():
    assert esta_em_temp(r"C:\Temp\OCR-LEITOR")


def test_classificar_cliente_recomenda_caminho_cliente(tmp_path):
    resultado = classificar_caminho_instalacao(tmp_path, modo="cliente")

    assert CAMINHO_PADRAO_CLIENTE in resultado["recomendacao"]


def test_classificar_cliente_marca_onedrive_como_inseguro(tmp_path):
    caminho = tmp_path / "OneDrive" / "OCR-LEITOR"
    resultado = classificar_caminho_instalacao(caminho, modo="cliente")

    assert resultado["seguro"] is False
    assert any("OneDrive" in item for item in resultado["bloqueios"])


def test_classificar_cliente_marca_desktop_como_inseguro(tmp_path):
    caminho = tmp_path / "Desktop" / "OCR-LEITOR"
    resultado = classificar_caminho_instalacao(caminho, modo="cliente")

    assert resultado["seguro"] is False
    assert any("Desktop" in item for item in resultado["bloqueios"])


def test_classificar_demo_recomenda_caminho_demo(tmp_path):
    resultado = classificar_caminho_instalacao(tmp_path, modo="demo")

    assert CAMINHO_PADRAO_DEMO in resultado["recomendacao"]


def test_classificar_demo_alerta_se_usar_caminho_cliente():
    resultado = classificar_caminho_instalacao(CAMINHO_PADRAO_CLIENTE, modo="demo")

    assert any("cliente real" in item for item in resultado["avisos"])


def test_classificar_update_bloqueia_sem_instalacao_existente(tmp_path):
    resultado = classificar_caminho_instalacao(tmp_path, modo="update")


    assert resultado["seguro"] is False
    assert "Update exige instalação existente." in resultado["bloqueios"]


def test_detectar_instalacao_existente_retorna_falso_em_pasta_vazia(tmp_path):
    resultado = detectar_instalacao_existente(tmp_path)

    assert resultado == {
        "existe": False,
        "sinais": [],
        "marcador_encontrado": False,
    }


def test_detectar_instalacao_existente_retorna_verdadeiro_com_env_e_app(tmp_path):
    (tmp_path / ".env").write_text("", encoding="utf-8")
    (tmp_path / "web").mkdir()
    (tmp_path / "web" / "app.py").write_text("", encoding="utf-8")

    resultado = detectar_instalacao_existente(tmp_path)

    assert resultado["existe"] is True
    assert ".env" in resultado["sinais"]
    assert str(Path("web") / "app.py") in resultado["sinais"]


def test_estrutura_recomendada_inclui_input():
    assert "input" in obter_estrutura_pastas_recomendada()


def test_estrutura_recomendada_inclui_processed():
    assert "processed" in obter_estrutura_pastas_recomendada()


def test_estrutura_recomendada_inclui_backups():
    assert "backups" in obter_estrutura_pastas_recomendada()


def test_doctor_usa_validacao_de_caminhos():
    conteudo = _ler(DOCTOR)

    assert "classificar_caminho_instalacao" in conteudo
    assert "Caminho de instalacao" in conteudo


def test_doctor_nao_torna_caminho_inseguro_como_erro_fatal(tmp_path):
    item = _verificar_caminho_instalacao(tmp_path / "OneDrive" / "Desktop" / "OCR-LEITOR")

    assert item["status"] == STATUS_AVISO


def test_documentacao_caminhos_instalacao_existe():
    assert DOCUMENTACAO.is_file()


def test_documentacao_cita_caminho_cliente():
    assert r"C:\OCR-LEITOR" in _ler(DOCUMENTACAO)


def test_documentacao_cita_caminho_demo():
    assert r"C:\OCR-LEITOR-DEMO" in _ler(DOCUMENTACAO)


def test_documentacao_cita_update_depende_de_backup_restore():
    conteudo = _ler(DOCUMENTACAO)

    assert "BACKUP-RESTORE-OCR-01" in conteudo


def test_modulo_nao_importa_requests():
    assert "requests" not in _ler(MODULO)


def test_modulo_nao_importa_urllib():
    assert "urllib" not in _ler(MODULO)


def test_modulo_nao_contem_token_real():
    conteudo = _ler(MODULO)

    assert "eyJ" + "hbGci" not in conteudo
    assert "Author" + "ization:" not in conteudo
    assert "Bearer" + " " not in conteudo

from pathlib import Path

import pytest


@pytest.fixture
def conteudo_bat():
    path = Path(__file__).resolve().parents[1] / "INICIAR_OCR_24H_LOCAL.bat"
    return path.read_text(encoding="utf-8")


def test_bat_existe():
    path = Path(__file__).resolve().parents[1] / "INICIAR_OCR_24H_LOCAL.bat"
    assert path.is_file()


def test_bat_contem_python_da_venv(conteudo_bat):
    assert r"\.venv\Scripts\python.exe" in conteudo_bat


def test_bat_contem_waitress(conteudo_bat):
    assert "waitress" in conteudo_bat


def test_bat_contem_listen_127_0_0_1(conteudo_bat):
    assert "--listen=127.0.0.1:5000" in conteudo_bat


def test_bat_contem_web_app_app(conteudo_bat):
    assert "web.app:app" in conteudo_bat


def test_bat_nao_contem_0_0_0_0(conteudo_bat):
    assert "0.0.0.0" not in conteudo_bat


def test_bat_nao_contem_pip_install(conteudo_bat):
    assert "pip install" not in conteudo_bat


def test_bat_nao_contem_sc_create(conteudo_bat):
    assert "sc create" not in conteudo_bat


def test_bat_nao_contem_schtasks(conteudo_bat):
    assert "schtasks" not in conteudo_bat


def test_bat_nao_contem_fechames_comando(conteudo_bat):
    for line in conteudo_bat.splitlines():
        assert "FechaMes" not in line

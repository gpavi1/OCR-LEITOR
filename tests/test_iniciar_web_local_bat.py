from pathlib import Path


def test_iniciar_web_local_usa_waitress_da_venv_local():
    bat_path = Path(__file__).resolve().parents[1] / "INICIAR_WEB_LOCAL.bat"
    conteudo = bat_path.read_text(encoding="utf-8")

    assert (
        r".\.venv\Scripts\python.exe -m waitress --listen=127.0.0.1:5000 web.app:app"
        in conteudo
    )
    assert (
        "waitress-serve --host=127.0.0.1 --port=5000 web.app:app"
        not in conteudo
    )

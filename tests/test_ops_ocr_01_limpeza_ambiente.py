from datetime import datetime
from pathlib import Path
import sys

BASE_DIR = Path(__file__).resolve().parents[1]
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from scripts.limpar_ambiente_teste import (
    PASTAS_OPERACIONAIS,
    limpar_ambiente_teste,
    main,
)

SCRIPT_PATH = BASE_DIR / "scripts" / "limpar_ambiente_teste.py"
BAT_PATH = BASE_DIR / "8_LIMPAR_AMBIENTE_TESTE.bat"
DOC_PATH = BASE_DIR / "docs" / "operacao" / "OPS-OCR-01_LIMPEZA_AMBIENTE_TESTE.md"


def criar_ambiente_teste(base):
    for pasta in PASTAS_OPERACIONAIS:
        destino = base / pasta
        destino.mkdir(parents=True, exist_ok=True)
        (destino / f"arquivo_{str(pasta).replace('/', '_').replace('\\', '_')}.txt").write_text(
            "conteudo de teste",
            encoding="utf-8",
        )


def test_script_existe():
    assert SCRIPT_PATH.is_file()


def test_bat_existe():
    assert BAT_PATH.is_file()


def test_documentacao_existe():
    assert DOC_PATH.is_file()


def test_dry_run_nao_move_arquivos(tmp_path):
    criar_ambiente_teste(tmp_path)

    resumo = limpar_ambiente_teste(
        tmp_path,
        dry_run=True,
        agora=datetime(2026, 6, 28, 10, 0, 0),
        validar_raiz=False,
    )

    assert resumo["dry_run"] is True
    assert resumo["arquivos_movidos"]
    assert not (tmp_path / "_backup_testes").exists()
    for pasta in PASTAS_OPERACIONAIS:
        assert any((tmp_path / pasta).iterdir())


def test_limpeza_move_arquivos_para_backup_testes(tmp_path):
    criar_ambiente_teste(tmp_path)

    resumo = limpar_ambiente_teste(
        tmp_path,
        dry_run=False,
        agora=datetime(2026, 6, 28, 10, 0, 0),
        validar_raiz=False,
    )

    backup = tmp_path / "_backup_testes" / "limpeza_20260628_100000"
    assert Path(resumo["backup_dir"]) == backup
    assert backup.is_dir()
    assert len(resumo["arquivos_movidos"]) == len(PASTAS_OPERACIONAIS)
    assert any(backup.rglob("*.txt"))


def test_pastas_operacionais_continuam_existindo_apos_limpeza(tmp_path):
    criar_ambiente_teste(tmp_path)
    limpar_ambiente_teste(tmp_path, validar_raiz=False)

    for pasta in PASTAS_OPERACIONAIS:
        assert (tmp_path / pasta).is_dir()


def test_pastas_operacionais_ficam_vazias_apos_limpeza(tmp_path):
    criar_ambiente_teste(tmp_path)
    limpar_ambiente_teste(tmp_path, validar_raiz=False)

    for pasta in PASTAS_OPERACIONAIS:
        assert list((tmp_path / pasta).iterdir()) == []


def test_script_nao_aceita_caminho_arbitrario_externo():
    try:
        main(["C:/fora/do/projeto"])
    except SystemExit as exc:
        assert exc.code != 0
        return

    assert False, "argumento posicional de caminho externo deveria ser rejeitado"


def test_script_nao_usa_delete_permanente_em_pastas_operacionais():
    conteudo = SCRIPT_PATH.read_text(encoding="utf-8")
    assert "shutil.rmtree" not in conteudo
    assert ".unlink(" not in conteudo
    assert ".remove(" not in conteudo
    assert "os.remove" not in conteudo


def test_script_nao_altera_banco():
    conteudo = SCRIPT_PATH.read_text(encoding="utf-8")
    assert "import mysql" not in conteudo.lower()
    assert "from database" not in conteudo.lower()
    assert "database.mysql_db" not in conteudo.lower()
    assert "ALTER TABLE" not in conteudo
    assert "DROP TABLE" not in conteudo
    assert "execute(" not in conteudo


def test_script_nao_chama_ocr_parser_pipeline():
    conteudo = SCRIPT_PATH.read_text(encoding="utf-8")
    assert "from ocr_pipeline_s1" not in conteudo
    assert "import ocr_pipeline_s1" not in conteudo
    assert "processar_input" not in conteudo
    assert "from parser_nf" not in conteudo
    assert "import parser_nf" not in conteudo
    assert "pytesseract" not in conteudo


def test_script_nao_altera_exports_de_codigo():
    conteudo = SCRIPT_PATH.read_text(encoding="utf-8")
    assert "exportacao" not in conteudo
    assert "json_validado" not in conteudo
    assert "markdown_relatorio" not in conteudo


def test_script_preserva_arquivos_versionados(tmp_path):
    pasta = tmp_path / "input"
    pasta.mkdir(parents=True)
    (pasta / ".gitkeep").write_text("", encoding="utf-8")
    (pasta / "documento.jpg").write_text("img", encoding="utf-8")

    limpar_ambiente_teste(tmp_path, validar_raiz=False)

    assert (pasta / ".gitkeep").is_file()
    assert not (pasta / "documento.jpg").exists()


def test_script_so_atua_nas_pastas_permitidas():
    assert [str(p).replace("\\", "/") for p in PASTAS_OPERACIONAIS] == [
        "input",
        "processed",
        "erro",
        "output/json",
        "exports/json",
        "exports/markdown",
    ]


def test_script_tem_mensagens_claras_de_seguranca():
    conteudo = SCRIPT_PATH.read_text(encoding="utf-8")
    assert "Banco MySQL não foi alterado." in conteudo
    assert "OCR/parser/core não foram executados nem alterados." in conteudo
    assert "dry-run" in conteudo

import json
import zipfile
from pathlib import Path

from scripts import restore_ocr


BASE_DIR = Path(__file__).resolve().parents[1]
SCRIPT = BASE_DIR / "scripts" / "restore_ocr.py"
DOC = BASE_DIR / "docs" / "operacao" / "BACKUP_RESTORE_OCR.md"
MENU = BASE_DIR / "scripts" / "menu_operacao.py"


def _ler(path):
    return path.read_text(encoding="utf-8")


def _manifest(tipo="ocr_leitor_backup"):
    return {
        "tipo": tipo,
        "versao_manifest": "1.0",
        "criado_em": "2026-01-01T00:00:00",
        "project_root": "fake",
        "incluiu_env_mascarado": False,
        "incluiu_banco": False,
        "banco_status": "ignorado",
        "pastas_incluidas": [],
        "arquivos_incluidos": [],
        "avisos": [],
        "nunca_incluir": [],
    }


def _criar_zip(tmp_path, manifest=None, entradas=None):
    zip_path = tmp_path / "backup.zip"
    with zipfile.ZipFile(zip_path, "w") as zf:
        if manifest is not None:
            zf.writestr("manifest.json", json.dumps(manifest))
        for nome, conteudo in (entradas or {}).items():
            zf.writestr(nome, conteudo)
    return zip_path


def test_script_restore_existe():
    assert SCRIPT.is_file()


def test_restore_dry_run_abre_zip_valido(tmp_path):
    zip_path = _criar_zip(tmp_path, _manifest(), {"arquivos/input/doc.txt": "backup"})

    retorno = restore_ocr.main(["--backup", str(zip_path), "--dry-run", "--restaurar-arquivos", "--destino", str(tmp_path / "dest")])

    assert retorno == 0


def test_restore_dry_run_nao_altera_arquivos(tmp_path):
    zip_path = _criar_zip(tmp_path, _manifest(), {"arquivos/input/doc.txt": "backup"})
    destino = tmp_path / "dest"

    retorno = restore_ocr.main(["--backup", str(zip_path), "--dry-run", "--restaurar-arquivos", "--destino", str(destino)])

    assert retorno == 0
    assert not (destino / "input" / "doc.txt").exists()


def test_restore_rejeita_zip_sem_manifest(tmp_path):
    zip_path = _criar_zip(tmp_path, None, {"arquivos/input/doc.txt": "backup"})

    assert restore_ocr.main(["--backup", str(zip_path), "--dry-run"]) == 1


def test_restore_rejeita_manifest_com_tipo_incorreto(tmp_path):
    zip_path = _criar_zip(tmp_path, _manifest(tipo="outro"), {"arquivos/input/doc.txt": "backup"})

    assert restore_ocr.main(["--backup", str(zip_path), "--dry-run"]) == 1


def test_restore_real_sem_confirmar_nao_roda(tmp_path):
    zip_path = _criar_zip(tmp_path, _manifest(), {"arquivos/input/doc.txt": "backup"})
    destino = tmp_path / "dest"

    retorno = restore_ocr.main(["--backup", str(zip_path), "--restaurar-arquivos", "--destino", str(destino)])

    assert retorno == 0
    assert not (destino / "input" / "doc.txt").exists()


def test_restore_real_sem_confirmacao_textual_nao_roda(tmp_path):
    zip_path = _criar_zip(tmp_path, _manifest(), {"arquivos/input/doc.txt": "backup"})
    destino = tmp_path / "dest"

    retorno = restore_ocr.main(["--backup", str(zip_path), "--confirmar", "--restaurar-arquivos", "--destino", str(destino)])

    assert retorno == 1
    assert not (destino / "input" / "doc.txt").exists()


def test_restore_real_exige_frase_restaurar_backup(tmp_path):
    zip_path = _criar_zip(tmp_path, _manifest(), {"arquivos/input/doc.txt": "backup"})
    destino = tmp_path / "dest"

    retorno = restore_ocr.main([
        "--backup", str(zip_path),
        "--confirmar",
        "--confirmacao", "OUTRA FRASE",
        "--restaurar-arquivos",
        "--destino", str(destino),
    ])

    assert retorno == 1
    assert not (destino / "input" / "doc.txt").exists()


def test_restore_nao_restaura_env(tmp_path):
    zip_path = _criar_zip(tmp_path, _manifest(), {".env": "remoto", "arquivos/input/doc.txt": "backup"})
    destino = tmp_path / "dest"
    destino.mkdir()
    (destino / ".env").write_text("local", encoding="utf-8")

    retorno = restore_ocr.main([
        "--backup", str(zip_path),
        "--confirmar",
        "--confirmacao", "RESTAURAR BACKUP",
        "--restaurar-arquivos",
        "--destino", str(destino),
    ])

    assert retorno == 0
    assert (destino / ".env").read_text(encoding="utf-8") == "local"


def test_restore_nao_restaura_venv(tmp_path):
    zip_path = _criar_zip(tmp_path, _manifest(), {"arquivos/.venv/secret.txt": "x"})
    destino = tmp_path / "dest"

    restore_ocr.main([
        "--backup", str(zip_path),
        "--confirmar",
        "--confirmacao", "RESTAURAR BACKUP",
        "--restaurar-arquivos",
        "--destino", str(destino),
    ])

    assert not (destino / ".venv" / "secret.txt").exists()


def test_restore_nao_restaura_backups(tmp_path):
    zip_path = _criar_zip(tmp_path, _manifest(), {"arquivos/backups/old.zip": "x"})
    destino = tmp_path / "dest"

    restore_ocr.main([
        "--backup", str(zip_path),
        "--confirmar",
        "--confirmacao", "RESTAURAR BACKUP",
        "--restaurar-arquivos",
        "--destino", str(destino),
    ])

    assert not (destino / "backups" / "old.zip").exists()


def test_restore_com_restaurar_arquivos_restaura_arquivo_fake_permitido(tmp_path):
    zip_path = _criar_zip(tmp_path, _manifest(), {"arquivos/input/doc.txt": "backup"})
    destino = tmp_path / "dest"

    retorno = restore_ocr.main([
        "--backup", str(zip_path),
        "--confirmar",
        "--confirmacao", "RESTAURAR BACKUP",
        "--restaurar-arquivos",
        "--destino", str(destino),
    ])

    assert retorno == 0
    assert (destino / "input" / "doc.txt").read_text(encoding="utf-8") == "backup"


def test_restore_cria_backup_de_seguranca_antes_do_restore_real(tmp_path):
    zip_path = _criar_zip(tmp_path, _manifest(), {"arquivos/input/doc.txt": "novo"})
    destino = tmp_path / "dest"
    (destino / "input").mkdir(parents=True)
    (destino / "input" / "doc.txt").write_text("antigo", encoding="utf-8")

    retorno = restore_ocr.main([
        "--backup", str(zip_path),
        "--confirmar",
        "--confirmacao", "RESTAURAR BACKUP",
        "--restaurar-arquivos",
        "--destino", str(destino),
    ])

    assert retorno == 0
    backups = list((destino / "backups").glob("restore-seguranca-*"))
    assert backups
    assert (backups[0] / "input" / "doc.txt").read_text(encoding="utf-8") == "antigo"


def test_restore_banco_sem_flag_nao_tenta_banco(tmp_path):
    zip_path = _criar_zip(tmp_path, _manifest(), {"database/dados.json": "{}", "arquivos/input/doc.txt": "backup"})
    destino = tmp_path / "dest"

    retorno = restore_ocr.main([
        "--backup", str(zip_path),
        "--confirmar",
        "--confirmacao", "RESTAURAR BACKUP",
        "--restaurar-arquivos",
        "--destino", str(destino),
    ])

    assert retorno == 0
    assert (destino / "input" / "doc.txt").exists()


def test_restore_banco_com_flag_retorna_mensagem_controlada(tmp_path):
    zip_path = _criar_zip(tmp_path, _manifest(), {"database/dados.json": "{}"})

    retorno = restore_ocr.main([
        "--backup", str(zip_path),
        "--confirmar",
        "--confirmacao", "RESTAURAR BACKUP",
        "--restaurar-banco",
        "--destino", str(tmp_path / "dest"),
    ])

    assert retorno == 2


def test_script_nao_contem_requests():
    assert "requests" not in _ler(SCRIPT)


def test_script_nao_contem_urllib():
    assert "urllib" not in _ler(SCRIPT)


def test_script_nao_contem_token_real():
    conteudo = _ler(SCRIPT)

    assert "eyJ" + "hbGci" not in conteudo
    assert "Author" + "ization:" not in conteudo
    assert "Bearer" + " " not in conteudo


def test_documentacao_backup_restore_existe():
    assert DOC.is_file()


def test_menu_contem_opcoes_de_backup_e_restore_dry_run():
    conteudo = _ler(MENU)

    assert "Gerar backup operacional" in conteudo
    assert "Validar backup / restore dry-run" in conteudo

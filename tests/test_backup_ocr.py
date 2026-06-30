import json
import zipfile
from pathlib import Path

from scripts import backup_ocr


BASE_DIR = Path(__file__).resolve().parents[1]
SCRIPT = BASE_DIR / "scripts" / "backup_ocr.py"


def _ler(path):
    return path.read_text(encoding="utf-8")


def _criar_projeto_fake(tmp_path):
    root = tmp_path / "projeto"
    root.mkdir()
    for pasta in ["input", "output", "processed", "erro", "logs", "exports"]:
        alvo = root / pasta
        alvo.mkdir()
        (alvo / f"{pasta}.txt").write_text(f"arquivo {pasta}", encoding="utf-8")
    (root / "database").mkdir()
    (root / "database" / "schema.sql").write_text("CREATE TABLE exemplo (id INT);", encoding="utf-8")
    (root / "config").mkdir()
    (root / "config" / "settings.json").write_text('{"ok": true}', encoding="utf-8")
    (root / ".env").write_text(
        "DB_PASSWORD=senha-real\nMONDAY_API_TOKEN=token-real\nWEB_SECRET_KEY=segredo-real\nDEBUG=false\n",
        encoding="utf-8",
    )
    (root / ".venv").mkdir()
    (root / ".venv" / "secret.txt").write_text("nao incluir", encoding="utf-8")
    (root / "__pycache__").mkdir()
    (root / "__pycache__" / "x.pyc").write_text("nao incluir", encoding="utf-8")
    (root / "backups").mkdir()
    (root / "backups" / "antigo.zip").write_text("nao incluir", encoding="utf-8")
    return root


def _criar_backup(root, destino, *args):
    retorno = backup_ocr.main(["--project-root", str(root), "--destino", str(destino), "--confirmar", "--sem-banco", *args])
    assert retorno == 0
    zips = list(destino.glob("OCR-LEITOR-BACKUP-*.zip"))
    assert len(zips) == 1
    return zips[0]


def _nomes_zip(zip_path):
    with zipfile.ZipFile(zip_path) as zf:
        return set(zf.namelist())


def test_script_backup_existe():
    assert SCRIPT.is_file()


def test_dry_run_nao_cria_zip(tmp_path):
    root = _criar_projeto_fake(tmp_path)
    destino = tmp_path / "destino"

    retorno = backup_ocr.main(["--project-root", str(root), "--destino", str(destino), "--dry-run", "--sem-banco"])

    assert retorno == 0
    assert not list(destino.glob("*.zip"))


def test_confirmar_cria_zip_em_destino_temporario(tmp_path):
    root = _criar_projeto_fake(tmp_path)
    destino = tmp_path / "destino"

    zip_path = _criar_backup(root, destino)

    assert zip_path.is_file()


def test_zip_contem_manifest_json(tmp_path):
    zip_path = _criar_backup(_criar_projeto_fake(tmp_path), tmp_path / "destino")

    assert "manifest.json" in _nomes_zip(zip_path)


def test_zip_contem_diagnostico_suporte(tmp_path):
    zip_path = _criar_backup(_criar_projeto_fake(tmp_path), tmp_path / "destino")

    assert "suporte/diagnostico.txt" in _nomes_zip(zip_path)


def test_zip_contem_schema_quando_existir(tmp_path):
    zip_path = _criar_backup(_criar_projeto_fake(tmp_path), tmp_path / "destino")

    assert "database/schema.sql" in _nomes_zip(zip_path)


def test_zip_inclui_pastas_operacionais_fake(tmp_path):
    zip_path = _criar_backup(_criar_projeto_fake(tmp_path), tmp_path / "destino")
    nomes = _nomes_zip(zip_path)

    assert "arquivos/input/input.txt" in nomes
    assert "arquivos/processed/processed.txt" in nomes
    assert "arquivos/exports/exports.txt" in nomes


def test_zip_nao_inclui_env_por_padrao(tmp_path):
    zip_path = _criar_backup(_criar_projeto_fake(tmp_path), tmp_path / "destino")

    assert ".env" not in _nomes_zip(zip_path)
    assert "config/env_mascarado.txt" not in _nomes_zip(zip_path)


def test_zip_inclui_env_mascarado_somente_com_flag(tmp_path):
    zip_path = _criar_backup(_criar_projeto_fake(tmp_path), tmp_path / "destino", "--incluir-env-mascarado")

    assert "config/env_mascarado.txt" in _nomes_zip(zip_path)


def test_env_mascarado_nao_contem_senha_token_em_claro(tmp_path):
    zip_path = _criar_backup(_criar_projeto_fake(tmp_path), tmp_path / "destino", "--incluir-env-mascarado")

    with zipfile.ZipFile(zip_path) as zf:
        texto = zf.read("config/env_mascarado.txt").decode("utf-8")

    assert "senha-real" not in texto
    assert "token-real" not in texto
    assert "segredo-real" not in texto
    assert "DB_PASSWORD=***" in texto


def test_zip_nao_inclui_venv(tmp_path):
    zip_path = _criar_backup(_criar_projeto_fake(tmp_path), tmp_path / "destino")

    assert not any(".venv" in nome for nome in _nomes_zip(zip_path))


def test_zip_nao_inclui_pycache(tmp_path):
    zip_path = _criar_backup(_criar_projeto_fake(tmp_path), tmp_path / "destino")

    assert not any("__pycache__" in nome for nome in _nomes_zip(zip_path))


def test_zip_nao_inclui_backups(tmp_path):
    zip_path = _criar_backup(_criar_projeto_fake(tmp_path), tmp_path / "destino")

    assert not any(nome.startswith("backups/") for nome in _nomes_zip(zip_path))
    assert not any(nome.startswith("arquivos/backups/") for nome in _nomes_zip(zip_path))


def test_manifest_contem_tipo_backup(tmp_path):
    zip_path = _criar_backup(_criar_projeto_fake(tmp_path), tmp_path / "destino")
    with zipfile.ZipFile(zip_path) as zf:
        manifest = json.loads(zf.read("manifest.json").decode("utf-8"))

    assert manifest["tipo"] == "ocr_leitor_backup"


def test_manifest_contem_avisos(tmp_path):
    zip_path = _criar_backup(_criar_projeto_fake(tmp_path), tmp_path / "destino")
    with zipfile.ZipFile(zip_path) as zf:
        manifest = json.loads(zf.read("manifest.json").decode("utf-8"))

    assert isinstance(manifest["avisos"], list)


def test_sem_banco_marca_banco_como_ignorado(tmp_path):
    zip_path = _criar_backup(_criar_projeto_fake(tmp_path), tmp_path / "destino")
    with zipfile.ZipFile(zip_path) as zf:
        manifest = json.loads(zf.read("manifest.json").decode("utf-8"))

    assert manifest["incluiu_banco"] is False
    assert manifest["banco_status"] == "ignorado"


def test_script_nao_contem_requests():
    assert "requests" not in _ler(SCRIPT)


def test_script_nao_contem_urllib():
    assert "urllib" not in _ler(SCRIPT)


def test_script_nao_contem_token_real():
    conteudo = _ler(SCRIPT)

    assert "eyJ" + "hbGci" not in conteudo
    assert "Author" + "ization:" not in conteudo
    assert "Bearer" + " " not in conteudo


def test_backup_nao_chama_monday():
    conteudo = _ler(SCRIPT).lower()

    assert "api.monday.com" not in conteudo

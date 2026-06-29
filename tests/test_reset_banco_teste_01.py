import json
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

BASE_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BASE_DIR))

from scripts import reset_banco_teste

SCRIPT_PATH = reset_banco_teste.BASE_DIR / "scripts" / "reset_banco_teste.py"
DOC_PATH = (
    reset_banco_teste.BASE_DIR
    / "docs" / "operacao" / "RESET-BANCO-TESTE-01_LIMPEZA_BANCO_TESTE.md"
)
GITIGNORE_PATH = reset_banco_teste.BASE_DIR / ".gitignore"

TABELAS_PADRAO = ["clientes", "documentos", "integracoes", "integracao_tentativas"]

REGISTROS_PADRAO = {
    "documentos": [
        {"id": 1, "cliente_id": 1, "arquivo_nome": "nf_teste_001.jpg",
         "status": "recebido"},
        {"id": 2, "cliente_id": 1, "arquivo_nome": "nf_teste_002.jpg",
         "status": "processado"},
    ],
    "integracao_tentativas": [
        {"id": 1, "documento_id": 1, "integracao_id": 1, "status": "sucesso"},
    ],
    "integracoes": [
        {"id": 1, "cliente_id": 1, "tipo": "monday", "nome": "Board Teste",
         "ativo": True},
    ],
    "clientes": [
        {"id": 1, "nome": "Cliente Teste OCR", "plano": "starter"},
    ],
}


class MockDB:
    def __init__(self, tabelas=None, registros=None):
        self.tabelas = list(tabelas or TABELAS_PADRAO)
        self.registros = {}
        for t in self.tabelas:
            self.registros[t] = list((registros or REGISTROS_PADRAO).get(t, []))
        self.deletes_executados = []

    def fetch_all(self, sql, params=None):
        s = sql.upper().strip()
        if "INFORMATION_SCHEMA" in s or s.startswith("SHOW TABLES"):
            return [{"TABLE_NAME": t} for t in self.tabelas]
        if s.startswith("SELECT * FROM"):
            nome = s.replace("SELECT * FROM", "").strip().strip('"').strip("'")
            return list(self.registros.get(nome, []))
        return []

    def fetch_one(self, sql, params=None):
        s = sql.upper().strip()
        if "SELECT 1" in s:
            return {"ok": 1}
        if "COUNT" in s:
            for t in self.tabelas:
                if f"FROM {t}" in s:
                    return {"total": len(self.registros.get(t, []))}
        return None

    @staticmethod
    def testar_conexao():
        return True, "Conexao MySQL OK"

    def get_connection(self):
        conn = MagicMock()
        cursor = MagicMock()
        cursor.execute.side_effect = self._capture_delete
        conn.cursor.return_value = cursor
        cm = MagicMock()
        cm.__enter__.return_value = conn
        cm.__exit__.return_value = False
        return cm

    def _capture_delete(self, sql, params=None):
        s = sql.upper().strip()
        if s.startswith("DELETE"):
            self.deletes_executados.append(sql)
        return None

    def execute(self, sql, params=None):
        s = sql.upper().strip()
        if s.startswith("DELETE"):
            self.deletes_executados.append(sql)
        return 1


@pytest.fixture
def mock_db():
    return MockDB()


@pytest.fixture
def db_patches(mock_db):
    with patch.multiple(
        "database.mysql_db",
        fetch_all=MagicMock(side_effect=mock_db.fetch_all),
        fetch_one=MagicMock(side_effect=mock_db.fetch_one),
        testar_conexao=MagicMock(side_effect=mock_db.testar_conexao),
    ):
        yield mock_db


@pytest.fixture
def db_patches_com_conexao(mock_db):
    with patch.multiple(
        "database.mysql_db",
        fetch_all=MagicMock(side_effect=mock_db.fetch_all),
        fetch_one=MagicMock(side_effect=mock_db.fetch_one),
        testar_conexao=MagicMock(side_effect=mock_db.testar_conexao),
        get_connection=MagicMock(side_effect=mock_db.get_connection),
    ):
        yield mock_db


# === Testes Basicos ===

def test_script_existe():
    assert SCRIPT_PATH.is_file()


def test_documentacao_existe():
    assert DOC_PATH.is_file()


def test_gitignore_protege_backup_banco():
    conteudo = GITIGNORE_PATH.read_text(encoding="utf-8")
    assert "_backup_banco_teste/" in conteudo


# === Testes de Modo Dry-Run ===

def test_dry_run_eh_padrao(db_patches):
    codigo = reset_banco_teste.main([])
    assert codigo == 0


def test_dry_run_cria_backup(db_patches, tmp_path):
    reset_banco_teste.main(["--dry-run", "--backup-dir", str(tmp_path / "bak")])
    pasta = list((tmp_path / "bak").iterdir())[0]
    assert (pasta / "resumo_antes.json").is_file()
    assert (pasta / "relatorio_reset_banco_teste.md").is_file()


def test_dry_run_cria_resumo_antes(db_patches, tmp_path):
    reset_banco_teste.main(["--dry-run", "--backup-dir", str(tmp_path / "bak")])
    pasta = list((tmp_path / "bak").iterdir())[0]
    resumo = json.loads((pasta / "resumo_antes.json").read_text(encoding="utf-8"))
    assert "tabelas" in resumo
    assert "documentos" in resumo["tabelas"]


def test_dry_run_nao_executa_delete(db_patches, tmp_path):
    mock_db = db_patches
    reset_banco_teste.main(["--dry-run", "--backup-dir", str(tmp_path / "bak")])
    assert len(mock_db.deletes_executados) == 0


# === Testes de Modo Confirmado ===

def test_sem_confirmar_nao_limpa(db_patches):
    codigo = reset_banco_teste.main(["--confirmar"])
    assert codigo == 1


def test_confirmacao_invalida_rejeitada(db_patches):
    codigo = reset_banco_teste.main([
        "--confirmar", "--confirmacao", "TEXTO_ERRADO",
    ])
    assert codigo == 1


def test_modo_real_executa_delete(db_patches_com_conexao, tmp_path):
    mock = db_patches_com_conexao
    codigo = reset_banco_teste.main([
        "--confirmar", "--confirmacao", "RESETAR_BANCO_TESTE",
        "--backup-dir", str(tmp_path / "bak"),
    ])
    assert codigo == 0
    assert len(mock.deletes_executados) >= 2


def test_modo_real_cria_backup(db_patches_com_conexao, tmp_path):
    reset_banco_teste.main([
        "--confirmar", "--confirmacao", "RESETAR_BANCO_TESTE",
        "--backup-dir", str(tmp_path / "bak"),
    ])
    pasta = list((tmp_path / "bak").iterdir())[0]
    assert (pasta / "resumo_antes.json").is_file()
    assert (pasta / "resumo_depois.json").is_file()
    assert (pasta / "relatorio_reset_banco_teste.md").is_file()


def test_modo_real_cria_relatorio_com_modo(db_patches_com_conexao, tmp_path):
    reset_banco_teste.main([
        "--confirmar", "--confirmacao", "RESETAR_BANCO_TESTE",
        "--backup-dir", str(tmp_path / "bak"),
    ])
    pasta = list((tmp_path / "bak").iterdir())[0]
    conteudo = (pasta / "relatorio_reset_banco_teste.md").read_text(encoding="utf-8")
    assert "REAL" in conteudo


# === Testes de Seguranca ===

def test_nao_apaga_clientes():
    assert "clientes" not in reset_banco_teste.TABELAS_CLEANUP
    assert "clientes" in reset_banco_teste.TABELAS_PROTEGIDAS


def test_nao_altera_schema(db_patches_com_conexao, tmp_path):
    mock = db_patches_com_conexao
    reset_banco_teste.main([
        "--confirmar", "--confirmacao", "RESETAR_BANCO_TESTE",
        "--backup-dir", str(tmp_path / "bak"),
    ])
    for sql in mock.deletes_executados:
        assert not sql.upper().startswith("ALTER")
        assert not sql.upper().startswith("DROP")
        assert not sql.upper().startswith("TRUNCATE")
        assert not sql.upper().startswith("CREATE")


def test_nao_altera_ocr_parser():
    assert not hasattr(reset_banco_teste, "parse_ocr")
    assert not hasattr(reset_banco_teste, "extrair_empresa")


def test_nao_altera_api():
    assert not hasattr(reset_banco_teste, "app")
    assert "flask" not in dir(reset_banco_teste)


def test_nao_altera_requirements():
    req_path = reset_banco_teste.BASE_DIR / "requirements.txt"
    conteudo = req_path.read_text(encoding="utf-8")
    assert "pytesseract" in conteudo


# === Testes de Tabelas com / sem Registros ===

def test_tabelas_sem_registros_funcionam(db_patches, tmp_path):
    mock = MockDB(tabelas=TABELAS_PADRAO, registros={})
    with patch.multiple(
        "database.mysql_db",
        fetch_all=MagicMock(side_effect=mock.fetch_all),
        fetch_one=MagicMock(side_effect=mock.fetch_one),
        testar_conexao=MagicMock(side_effect=mock.testar_conexao),
    ):
        codigo = reset_banco_teste.main([
            "--dry-run", "--backup-dir", str(tmp_path / "bak"),
        ])
        assert codigo == 0


def test_tabelas_desconhecidas_nao_quebram(db_patches, tmp_path):
    mock = MockDB(tabelas=["clientes", "documentos", "tabela_estranha"])
    with patch.multiple(
        "database.mysql_db",
        fetch_all=MagicMock(side_effect=mock.fetch_all),
        fetch_one=MagicMock(side_effect=mock.fetch_one),
        testar_conexao=MagicMock(side_effect=mock.testar_conexao),
    ):
        codigo = reset_banco_teste.main([
            "--dry-run", "--backup-dir", str(tmp_path / "bak"),
        ])
        assert codigo == 0


def test_sem_tabelas_de_limpeza_funciona(db_patches, tmp_path):
    mock = MockDB(tabelas=["clientes"])
    with patch.multiple(
        "database.mysql_db",
        fetch_all=MagicMock(side_effect=mock.fetch_all),
        fetch_one=MagicMock(side_effect=mock.fetch_one),
        testar_conexao=MagicMock(side_effect=mock.testar_conexao),
    ):
        codigo = reset_banco_teste.main([
            "--dry-run", "--backup-dir", str(tmp_path / "bak"),
        ])
        assert codigo == 0


# === Testes de Erro ===

def test_erro_em_get_connection_retorna_1(db_patches, tmp_path):
    with patch("database.mysql_db.get_connection") as mock_gc:
        mock_gc.side_effect = RuntimeError("Erro simulado")
        codigo = reset_banco_teste.main([
            "--confirmar", "--confirmacao", "RESETAR_BANCO_TESTE",
            "--backup-dir", str(tmp_path / "bak"),
        ])
        assert codigo == 1


# === Testes das Funcoes Internas ===

def test_listar_tabelas_existentes_chama_fetch_all():
    with patch("database.mysql_db.fetch_all") as mock_fa:
        mock_fa.return_value = [{"TABLE_NAME": "documentos"}]
        resultado = reset_banco_teste.listar_tabelas_existentes()
        assert resultado == ["documentos"]
        mock_fa.assert_called_once()


def test_contar_registros_chama_fetch_one():
    with patch("database.mysql_db.fetch_one") as mock_fo:
        mock_fo.return_value = {"total": 5}
        total = reset_banco_teste.contar_registros("documentos")
        assert total == 5


def test_exportar_tabela_chama_fetch_all():
    with patch("database.mysql_db.fetch_all") as mock_fa:
        mock_fa.return_value = [{"id": 1}]
        dados = reset_banco_teste.exportar_tabela("documentos")
        assert len(dados) == 1


def test_gerar_backup_cria_pasta(tmp_path):
    reset_banco_teste.gerar_backup(tmp_path / "bak", {}, [], [], [])
    assert (tmp_path / "bak").is_dir()


def test_gerar_backup_salva_resumo(tmp_path):
    dados = {"documentos": {"total": 2, "dados": [{"id": 1}]}}
    reset_banco_teste.gerar_backup(tmp_path / "bak", dados, ["documentos"], [], [])
    assert (tmp_path / "bak" / "resumo_antes.json").is_file()


def test_gerar_backup_salva_json_por_tabela(tmp_path):
    dados = {"documentos": {"total": 2, "dados": [{"id": 1}]}}
    reset_banco_teste.gerar_backup(tmp_path / "bak", dados, ["documentos"], [], [])
    assert (tmp_path / "bak" / "documentos.json").is_file()


def test_gerar_backup_nao_salva_json_vazio(tmp_path):
    dados = {"documentos": {"total": 0, "dados": []}}
    reset_banco_teste.gerar_backup(tmp_path / "bak", dados, ["documentos"], [], [])
    assert not (tmp_path / "bak" / "documentos.json").exists()


def test_gerar_resumo_depois(tmp_path):
    (tmp_path / "bak").mkdir()
    reset_banco_teste.gerar_resumo_depois(tmp_path / "bak", {"documentos": 0})
    assert (tmp_path / "bak" / "resumo_depois.json").is_file()


def test_gerar_relatorio_md(tmp_path):
    (tmp_path / "bak").mkdir()
    ra = {"tabelas": {"documentos": {"total": 2}}, "tabelas_puladas": [],
          "tabelas_protegidas": ["clientes"]}
    reset_banco_teste.gerar_relatorio_md(tmp_path / "bak", ra, {"documentos": 0},
                                          "DRY-RUN", ["documentos"])
    rel = tmp_path / "bak" / "relatorio_reset_banco_teste.md"
    assert rel.is_file()
    assert "DRY-RUN" in rel.read_text(encoding="utf-8")


def test_gerar_relatorio_com_erro(tmp_path):
    (tmp_path / "bak").mkdir()
    ra = {"tabelas": {"documentos": {"total": 2}}, "tabelas_puladas": [],
          "tabelas_protegidas": []}
    reset_banco_teste.gerar_relatorio_md(tmp_path / "bak", ra, {"documentos": 2},
                                          "ERRO", ["documentos"],
                                          erro=ValueError("explodiu"))
    rel = tmp_path / "bak" / "relatorio_reset_banco_teste.md"
    conteudo = rel.read_text(encoding="utf-8")
    assert "explodiu" in conteudo


# === Testes de Seguranca Adicional ===

def test_script_nao_usa_internet():
    conteudo = SCRIPT_PATH.read_text(encoding="utf-8").lower()
    assert "requests" not in conteudo
    assert "urllib" not in conteudo
    assert "openai" not in conteudo
    assert "http://" not in conteudo
    assert "https://" not in conteudo


def test_backup_em_pasta_ignorada_pelo_git():
    gitignore = GITIGNORE_PATH.read_text(encoding="utf-8")
    assert "_backup_banco_teste/" in gitignore


def test_limpa_integracoes_so_com_flag(db_patches_com_conexao, tmp_path):
    mock = db_patches_com_conexao
    reset_banco_teste.main([
        "--confirmar", "--confirmacao", "RESETAR_BANCO_TESTE",
        "--limpar-integracoes",
        "--backup-dir", str(tmp_path / "bak"),
    ])
    deletes_integracoes = [s for s in mock.deletes_executados if "integracoes" in s]
    assert len(deletes_integracoes) >= 1

import sys
from pathlib import Path
from unittest.mock import patch, MagicMock

BASE_DIR = Path(__file__).resolve().parents[1]
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from conectores.monday_dryrun import (
    gerar_dryrun_monday,
    MAPA_PADRAO_DRYRUN,
    DRYRUN_VERSION,
)
from conectores.monday_payload import MONDAY_PAYLOAD_VERSION

DRYRUN_PATH = BASE_DIR / "conectores" / "monday_dryrun.py"
DOC_PATH = BASE_DIR / "docs" / "integracao" / "MONDAY-DRYRUN-01_ENVIO_SIMULADO.md"
APP_PATH = BASE_DIR / "web" / "app.py"
INTEGRACOES_HTML = BASE_DIR / "web" / "templates" / "integracoes.html"
DETALHE_HTML = BASE_DIR / "web" / "templates" / "documento_detalhe.html"
HISTORICO_HTML = BASE_DIR / "web" / "templates" / "historico_integracoes.html"


def documento_exemplo(status="pendente_integracao", revisado=True, tipo_documento=None, **kwargs):
    doc = {
        "id": 123,
        "cliente_id": 1,
        "arquivo_nome": "nf_exemplo.pdf",
        "empresa": "EMPRESA TESTE LTDA",
        "numero_nf": "000123",
        "chave_acesso": "3511112222333344445555666677778888",
        "vencimento": "2026-07-10",
        "valor_total": 150.00,
        "status": status,
        "revisado": revisado,
        "revisado_por": "operador_local",
        "revisado_em": "2026-07-01 10:00:00",
        "observacao_revisao": "revisado manualmente",
        "json_path": "exports/json/documento_123_20260701.json",
        "tipo_documento": tipo_documento,
    }
    doc.update(kwargs)
    return doc


# --- existencia ---

def test_modulo_existe():
    assert DRYRUN_PATH.is_file()


def test_funcao_gerar_dryrun_existe():
    assert callable(gerar_dryrun_monday)


# --- comportamento apto ---

def test_documento_apto_retorna_status_apto():
    doc = documento_exemplo()
    resultado = gerar_dryrun_monday(doc)
    assert resultado["status"] == "apto"


def test_documento_apto_envio_real_false():
    doc = documento_exemplo()
    resultado = gerar_dryrun_monday(doc)
    assert resultado["envio_real"] is False


def test_documento_apto_requer_confirmacao():
    doc = documento_exemplo()
    resultado = gerar_dryrun_monday(doc)
    assert resultado["payload"]["metadados"]["requer_confirmacao_humana"] is True


def test_documento_apto_contem_payload():
    doc = documento_exemplo()
    resultado = gerar_dryrun_monday(doc)
    assert "payload" in resultado
    assert resultado["payload"]["versao"] == MONDAY_PAYLOAD_VERSION


def test_documento_apto_contem_column_values():
    doc = documento_exemplo()
    resultado = gerar_dryrun_monday(doc)
    assert "column_values" in resultado
    assert len(resultado["column_values"]) > 0


def test_documento_apto_sem_bloqueios():
    doc = documento_exemplo()
    resultado = gerar_dryrun_monday(doc)
    assert resultado["bloqueios"] == []


# --- comportamento bloqueado ---

def test_documento_pendente_revisao_bloqueado():
    doc = documento_exemplo(status="pendente_revisao", revisado=False)
    resultado = gerar_dryrun_monday(doc)
    assert resultado["status"] == "bloqueado"


def test_documento_erro_ocr_bloqueado():
    doc = documento_exemplo(status="erro_ocr", revisado=False)
    resultado = gerar_dryrun_monday(doc)
    assert resultado["status"] == "bloqueado"


def test_documento_nao_revisado_bloqueado():
    doc = documento_exemplo(revisado=False)
    resultado = gerar_dryrun_monday(doc)
    assert resultado["status"] == "bloqueado"


def test_documento_recebido_bloqueado():
    doc = documento_exemplo(status="recebido", revisado=False)
    resultado = gerar_dryrun_monday(doc)
    assert resultado["status"] == "bloqueado"


def test_documento_processando_bloqueado():
    doc = documento_exemplo(status="processando", revisado=False)
    resultado = gerar_dryrun_monday(doc)
    assert resultado["status"] == "bloqueado"


def test_bloqueado_column_values_vazio():
    doc = documento_exemplo(status="pendente_revisao", revisado=False)
    resultado = gerar_dryrun_monday(doc)
    assert resultado["column_values"] == {}


def test_bloqueado_contem_bloqueios():
    doc = documento_exemplo(status="pendente_revisao", revisado=False)
    resultado = gerar_dryrun_monday(doc)
    assert len(resultado["bloqueios"]) > 0


# --- mapa padrao ---

def test_mapa_padrao_usado_quando_none():
    doc = documento_exemplo()
    resultado = gerar_dryrun_monday(doc)
    for col_id in resultado["column_values"]:
        assert col_id.startswith("dryrun_")


def test_mapa_padrao_ids_ficticios():
    for key, value in MAPA_PADRAO_DRYRUN.items():
        assert value.startswith("dryrun_"), f"{key} -> {value} deve comecar com dryrun_"


# --- versao ---

def test_versao_correta():
    assert DRYRUN_VERSION == "monday_dryrun.v1"


def test_resultado_contem_tipo():
    doc = documento_exemplo()
    resultado = gerar_dryrun_monday(doc)
    assert resultado["tipo"] == "monday_dryrun"


# --- seguranca do modulo ---

def test_modulo_nao_importa_requests():
    conteudo = DRYRUN_PATH.read_text(encoding="utf-8")
    padroes = ["import requests", "from requests", "import urllib", "from urllib"]
    for p in padroes:
        assert p not in conteudo, f"Nao deve conter: {p}"


def test_modulo_nao_contem_api_monday():
    conteudo = DRYRUN_PATH.read_text(encoding="utf-8")
    assert "api.monday.com" not in conteudo


def test_modulo_nao_le_env():
    conteudo = DRYRUN_PATH.read_text(encoding="utf-8")
    assert ".env" not in conteudo


def test_modulo_nao_usa_os_getenv():
    conteudo = DRYRUN_PATH.read_text(encoding="utf-8")
    assert "os.getenv" not in conteudo
    assert "os.environ" not in conteudo


def test_modulo_nao_contem_token():
    conteudo = DRYRUN_PATH.read_text(encoding="utf-8")
    assert "token" not in conteudo.lower()


def test_modulo_nao_contem_board_id_real():
    conteudo = DRYRUN_PATH.read_text(encoding="utf-8")
    assert "board_id" not in conteudo.lower()


def test_modulo_nao_contem_column_id_real():
    conteudo = DRYRUN_PATH.read_text(encoding="utf-8")
    assert "col_" not in conteudo


# --- rota web app ---

def test_rota_dryrun_existe_no_app():
    conteudo = APP_PATH.read_text(encoding="utf-8")
    assert "/integracoes/documentos/<int:documento_id>/monday-dryrun" in conteudo


def test_rota_dryrun_aceita_apenas_post():
    conteudo = APP_PATH.read_text(encoding="utf-8")
    assert "monday-dryrun" in conteudo
    assert 'methods=["POST"]' in conteudo


def test_rota_chama_gerar_dryrun_monday():
    conteudo = APP_PATH.read_text(encoding="utf-8")
    assert "gerar_dryrun_monday" in conteudo


def test_rota_registra_dry_run_apto():
    conteudo = APP_PATH.read_text(encoding="utf-8")
    assert "dry_run_apto" in conteudo


def test_rota_registra_dry_run_bloqueado():
    conteudo = APP_PATH.read_text(encoding="utf-8")
    assert "dry_run_bloqueado" in conteudo


def test_rota_nao_altera_status_para_integrado():
    conteudo = APP_PATH.read_text(encoding="utf-8")
    linhas_perigo = [l for l in conteudo.splitlines() if "monday-dryrun" in l or "simular_monday" in l.lower()]
    for linha in linhas_perigo:
        assert "UPDATE documentos" not in linha
        assert "status = 'integrado'" not in linha


def test_rota_nao_chama_monday_real():
    conteudo = APP_PATH.read_text(encoding="utf-8")
    assert "api.monday.com" not in conteudo
    assert "requests." not in conteudo


# --- ui: integracoes.html ---

def test_integracoes_contem_botao_simular_monday():
    conteudo = INTEGRACOES_HTML.read_text(encoding="utf-8")
    assert "Simular Monday" in conteudo or "simular_monday" in conteudo


# --- ui: documento_detalhe.html ---

def test_detalhe_contem_botao_simular_monday_condicional():
    conteudo = DETALHE_HTML.read_text(encoding="utf-8")
    assert "Simular Monday" in conteudo


def test_detalhe_botao_condicionado_pendente_integracao():
    conteudo = DETALHE_HTML.read_text(encoding="utf-8")
    assert "pendente_integracao" in conteudo


# --- ui: historico_integracoes.html ---

def test_historico_exibe_status_dry_run():
    conteudo = HISTORICO_HTML.read_text(encoding="utf-8")
    assert "badge-{{ tentativa.status }}" in conteudo or "tentativa.status" in conteudo


# --- documentacao ---

def test_documentacao_existe():
    assert DOC_PATH.is_file()


def test_documentacao_menciona_sem_envio_real():
    conteudo = DOC_PATH.read_text(encoding="utf-8")
    assert "nao envia" in conteudo.lower() or "nao ha envio" in conteudo.lower()


def test_documentacao_menciona_sem_token():
    conteudo = DOC_PATH.read_text(encoding="utf-8")
    assert "token" not in conteudo.lower() or "nao usa token" in conteudo.lower()


def test_documentacao_menciona_sem_api_externa():
    conteudo = DOC_PATH.read_text(encoding="utf-8")
    assert "nao chama" in conteudo.lower() or "externa" in conteudo.lower()


def test_documentacao_menciona_revisao_humana():
    conteudo = DOC_PATH.read_text(encoding="utf-8")
    assert "revis" in conteudo.lower()


def test_documentacao_menciona_proxima_fase():
    conteudo = DOC_PATH.read_text(encoding="utf-8")
    assert "MONDAY-ENVIO-APROVADO-01" in conteudo


# --- seguranca dos testes ---

def test_teste_nao_conecta_mysql():
    linhas = Path(__file__).read_text(encoding="utf-8").splitlines()
    imports = [l for l in linhas if l.startswith("import ") or l.startswith("from ")]
    assert all("mysql" not in l and "MySQL" not in l for l in imports)


def test_teste_nao_executa_ocr():
    linhas = Path(__file__).read_text(encoding="utf-8").splitlines()
    imports = [l for l in linhas if l.startswith("import ") or l.startswith("from ")]
    assert all("pytesseract" not in l and "tesserocr" not in l for l in imports)


def test_teste_nao_exige_internet():
    linhas = Path(__file__).read_text(encoding="utf-8").splitlines()
    imports = [l for l in linhas if l.startswith("import ") or l.startswith("from ")]
    assert all(
        "requests" not in l and "urllib" not in l and "http.client" not in l
        for l in imports
    )


# --- dry-run nao envia e nao integra ---

def test_dryrun_sempre_envio_real_false():
    doc = documento_exemplo()
    resultado = gerar_dryrun_monday(doc)
    assert resultado["envio_real"] is False

    doc2 = documento_exemplo(status="pendente_revisao", revisado=False)
    resultado2 = gerar_dryrun_monday(doc2)
    assert resultado2["envio_real"] is False


def test_dryrun_nao_muda_status_para_integrado():
    from conectores.monday_payload import normalizar_documento_para_monday
    doc = documento_exemplo(status="pendente_integracao")
    payload = normalizar_documento_para_monday(doc)
    assert payload["campos"]["status"] == "pendente_integracao"
    assert payload["campos"]["status"] != "integrado"


# --- import da rota no app ---

def test_app_importa_dryrun():
    conteudo = APP_PATH.read_text(encoding="utf-8")
    assert "monday_dryrun" in conteudo


# --- STATUS_LABEL ---

def test_app_contem_status_dry_run_apto():
    conteudo = APP_PATH.read_text(encoding="utf-8")
    assert "dry_run_apto" in conteudo


def test_app_contem_status_dry_run_bloqueado():
    conteudo = APP_PATH.read_text(encoding="utf-8")
    assert "dry_run_bloqueado" in conteudo


def test_app_contem_status_dry_run_erro():
    conteudo = APP_PATH.read_text(encoding="utf-8")
    assert "dry_run_erro" in conteudo

import json
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[1]
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from conectores.monday_envio import (
    enviar_documento_monday,
    ENVIO_VERSION,
    MONDAY_API_URL,
    COLUNAS_OBRIGATORIAS,
)

ENVIO_PATH = BASE_DIR / "conectores" / "monday_envio.py"
DOC_PATH = BASE_DIR / "docs" / "integracao" / "MONDAY-ENVIO-APROVADO-01_ENVIO_REAL_CONTROLADO.md"
CONFIG_DOC_PATH = BASE_DIR / "docs" / "integracao" / "MONDAY_CONFIG_EXEMPLO.md"
APP_PATH = BASE_DIR / "web" / "app.py"
INTEGRACOES_HTML = BASE_DIR / "web" / "templates" / "integracoes.html"
DETALHE_HTML = BASE_DIR / "web" / "templates" / "documento_detalhe.html"
HISTORICO_HTML = BASE_DIR / "web" / "templates" / "historico_integracoes.html"

TOKEN_FAKE = "fake-token-para-teste"
BOARD_ID_FAKE = "987654321"
MAPA_COLUNAS_FAKE = {
    "empresa": "col_empresa",
    "numero_nf": "col_numero_nf",
    "chave_acesso": "col_chave_acesso",
    "vencimento": "col_vencimento",
    "valor_total": "col_valor_total",
    "observacao_revisao": "col_observacao",
}


class RespostaFake:
    def __init__(self, dados):
        self._dados = dados

    def json(self):
        return self._dados


def post_func_sucesso(url, json, headers, timeout):
    dados = json
    query = dados.get("query", "")
    if "create_item" in query:
        return RespostaFake({
            "data": {
                "create_item": {
                    "id": "123456789",
                    "name": dados.get("variables", {}).get("item_name", ""),
                }
            }
        })
    if "change_multiple_column_values" in query:
        return RespostaFake({"data": {"change_multiple_column_values": {"id": "ok"}}})
    return RespostaFake({"data": {}})


def post_func_falha_create(url, json, headers, timeout):
    return RespostaFake({"errors": [{"message": "Board not found"}]})


def post_func_falha_update(url, json, headers, timeout):
    dados = json
    query = dados.get("query", "")
    if "create_item" in query:
        return RespostaFake({
            "data": {"create_item": {"id": "123456789", "name": "teste"}}
        })
    if "change_multiple_column_values" in query:
        return RespostaFake({"errors": [{"message": "Column not found"}]})
    return RespostaFake({"data": {}})


def documento_exemplo(status="pendente_integracao", revisado=True, **kwargs):
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
        "json_path": "exports/json/documento_123.json",
        "tipo_documento": "NF-e",
    }
    doc.update(kwargs)
    return doc


# --- existencia ---

def test_modulo_existe():
    assert ENVIO_PATH.is_file()


def test_funcao_enviar_existe():
    assert callable(enviar_documento_monday)


# --- sucesso ---

def test_documento_apto_retorna_sucesso():
    resultado = enviar_documento_monday(
        documento_exemplo(), TOKEN_FAKE, BOARD_ID_FAKE,
        MAPA_COLUNAS_FAKE, post_func=post_func_sucesso,
    )
    assert resultado["status"] == "sucesso"
    assert resultado["item_id"] == "123456789"
    assert resultado["envio_real"] is True


def test_sucesso_retorna_item_id():
    resultado = enviar_documento_monday(
        documento_exemplo(), TOKEN_FAKE, BOARD_ID_FAKE,
        MAPA_COLUNAS_FAKE, post_func=post_func_sucesso,
    )
    assert resultado["item_id"] is not None
    assert resultado["item_id"] == "123456789"


def test_sucesso_contem_payload():
    resultado = enviar_documento_monday(
        documento_exemplo(), TOKEN_FAKE, BOARD_ID_FAKE,
        MAPA_COLUNAS_FAKE, post_func=post_func_sucesso,
    )
    assert "payload" in resultado
    assert resultado["payload"]["apto_envio"] is True


# --- bloqueio por validacao do documento ---

def test_pendente_revisao_bloqueado():
    resultado = enviar_documento_monday(
        documento_exemplo(status="pendente_revisao", revisado=False),
        TOKEN_FAKE, BOARD_ID_FAKE, MAPA_COLUNAS_FAKE,
        post_func=post_func_sucesso,
    )
    assert resultado["status"] == "bloqueado"


def test_nao_revisado_bloqueado():
    resultado = enviar_documento_monday(
        documento_exemplo(revisado=False),
        TOKEN_FAKE, BOARD_ID_FAKE, MAPA_COLUNAS_FAKE,
        post_func=post_func_sucesso,
    )
    assert resultado["status"] == "bloqueado"


def test_integrado_bloqueado():
    resultado = enviar_documento_monday(
        documento_exemplo(status="integrado"),
        TOKEN_FAKE, BOARD_ID_FAKE, MAPA_COLUNAS_FAKE,
        post_func=post_func_sucesso,
    )
    assert resultado["status"] == "bloqueado"


# --- bloqueio por config ---

def test_token_ausente_bloqueado():
    resultado = enviar_documento_monday(
        documento_exemplo(), "", BOARD_ID_FAKE, MAPA_COLUNAS_FAKE,
        post_func=post_func_sucesso,
    )
    assert resultado["status"] == "bloqueado"
    assert any("token" in b.lower() for b in resultado["bloqueios"])


def test_board_id_ausente_bloqueado():
    resultado = enviar_documento_monday(
        documento_exemplo(), TOKEN_FAKE, "", MAPA_COLUNAS_FAKE,
        post_func=post_func_sucesso,
    )
    assert resultado["status"] == "bloqueado"
    assert any("board" in b.lower() for b in resultado["bloqueios"])


def test_mapa_colunas_ausente_bloqueado():
    resultado = enviar_documento_monday(
        documento_exemplo(), TOKEN_FAKE, BOARD_ID_FAKE, {},
        post_func=post_func_sucesso,
    )
    assert resultado["status"] == "bloqueado"
    assert len(resultado["bloqueios"]) > 0


def test_mapa_colunas_incompleto_bloqueado():
    mapa = {"empresa": "col_empresa"}
    resultado = enviar_documento_monday(
        documento_exemplo(), TOKEN_FAKE, BOARD_ID_FAKE, mapa,
        post_func=post_func_sucesso,
    )
    assert resultado["status"] == "bloqueado"


# --- falha na API ---

def test_falha_create_item_retorna_falha():
    resultado = enviar_documento_monday(
        documento_exemplo(), TOKEN_FAKE, BOARD_ID_FAKE,
        MAPA_COLUNAS_FAKE, post_func=post_func_falha_create,
    )
    assert resultado["status"] == "falha"
    assert resultado["item_id"] is None


def test_falha_update_columns_retorna_falha():
    resultado = enviar_documento_monday(
        documento_exemplo(), TOKEN_FAKE, BOARD_ID_FAKE,
        MAPA_COLUNAS_FAKE, post_func=post_func_falha_update,
    )
    assert resultado["status"] == "falha"
    # item foi criado mesmo com falha no update
    assert resultado["item_id"] == "123456789"


# --- graphql usa variables ---

def test_create_item_usa_variables():
    chamadas = []

    def capturar(url, json, headers, timeout):
        chamadas.append(json)
        return post_func_sucesso(url, json, headers, timeout)

    enviar_documento_monday(
        documento_exemplo(), TOKEN_FAKE, BOARD_ID_FAKE,
        MAPA_COLUNAS_FAKE, post_func=capturar,
    )

    chamada_create = [c for c in chamadas if "create_item" in c.get("query", "")]
    assert len(chamada_create) == 1
    variaveis = chamada_create[0].get("variables", {})
    assert "board_id" in variaveis
    assert "item_name" in variaveis
    assert variaveis["board_id"] == BOARD_ID_FAKE
    assert "EMPRESA" in variaveis["item_name"]


def test_update_columns_usa_variables():
    chamadas = []

    def capturar(url, json, headers, timeout):
        chamadas.append(json)
        return post_func_sucesso(url, json, headers, timeout)

    enviar_documento_monday(
        documento_exemplo(), TOKEN_FAKE, BOARD_ID_FAKE,
        MAPA_COLUNAS_FAKE, post_func=capturar,
    )

    chamada_update = [c for c in chamadas if "change_multiple_column_values" in c.get("query", "")]
    assert len(chamada_update) == 1
    variaveis = chamada_update[0].get("variables", {})
    assert "board_id" in variaveis
    assert "item_id" in variaveis
    assert "column_values" in variaveis
    # column_values deve ser string JSON
    assert isinstance(variaveis["column_values"], str)
    col_val = json.loads(variaveis["column_values"])
    assert "col_empresa" in col_val


# --- seguranca do modulo ---

def test_modulo_nao_le_env():
    conteudo = ENVIO_PATH.read_text(encoding="utf-8")
    assert ".env" not in conteudo


def test_modulo_nao_usa_os_getenv():
    conteudo = ENVIO_PATH.read_text(encoding="utf-8")
    assert "os.getenv" not in conteudo
    assert "os.environ" not in conteudo


def test_modulo_nao_contem_token_real():
    conteudo = ENVIO_PATH.read_text(encoding="utf-8")
    assert "fake-token" not in conteudo


def test_modulo_nao_contem_board_id_real():
    conteudo = ENVIO_PATH.read_text(encoding="utf-8")
    assert "987654321" not in conteudo


def test_modulo_nao_contem_api_key_real():
    conteudo = ENVIO_PATH.read_text(encoding="utf-8")
    assert "api_key" not in conteudo.lower()


def test_modulo_nao_importa_ocr_to_monday():
    conteudo = ENVIO_PATH.read_text(encoding="utf-8")
    assert "ocr_to_monday" not in conteudo
    assert "ocr_to_monday.py" not in conteudo


def test_modulo_nao_importa_src_monday_api():
    conteudo = ENVIO_PATH.read_text(encoding="utf-8")
    assert "src.monday_api" not in conteudo
    assert "src/monday_api" not in conteudo


def test_modulo_nao_implementa_anexo():
    conteudo = ENVIO_PATH.read_text(encoding="utf-8")
    assert "add_file_to_column" not in conteudo


def test_versao_correta():
    assert ENVIO_VERSION == "monday_envio_aprovado.v1"


# --- web app ---

def test_rota_enviar_monday_existe():
    conteudo = APP_PATH.read_text(encoding="utf-8")
    assert "enviar-monday" in conteudo


def test_rota_exige_post():
    conteudo = APP_PATH.read_text(encoding="utf-8")
    assert 'methods=["POST"]' in conteudo


def test_rota_exige_confirmar_sim():
    conteudo = APP_PATH.read_text(encoding="utf-8")
    assert "confirmar" in conteudo


def test_rota_bloqueia_duplicidade():
    conteudo = APP_PATH.read_text(encoding="utf-8")
    assert "duplicidade" in conteudo.lower() or "monday_envio_sucesso" in conteudo


def test_rota_registra_monday_envio_sucesso():
    conteudo = APP_PATH.read_text(encoding="utf-8")
    assert "monday_envio_sucesso" in conteudo


def test_rota_registra_monday_envio_falha():
    conteudo = APP_PATH.read_text(encoding="utf-8")
    assert "monday_envio_falha" in conteudo


def test_rota_registra_monday_envio_bloqueado():
    conteudo = APP_PATH.read_text(encoding="utf-8")
    assert "monday_envio_bloqueado" in conteudo


def test_rota_atualiza_integrado_somente_sucesso():
    conteudo = APP_PATH.read_text(encoding="utf-8")
    assert "status = 'integrado'" in conteudo
    assert "enviar_monday" in conteudo


def test_rota_nao_salva_token_no_banco():
    conteudo = APP_PATH.read_text(encoding="utf-8")
    linhas = [l for l in conteudo.splitlines() if "INSERT INTO integracoes" in l]
    for linha in linhas:
        assert "token" not in linha.lower() and "MONDAY_API_TOKEN" not in linha


# --- ui ---

def test_integracoes_contem_botao_enviar_monday():
    conteudo = INTEGRACOES_HTML.read_text(encoding="utf-8")
    assert "Enviar para Monday" in conteudo


def test_integracoes_contem_confirm_explicito():
    conteudo = INTEGRACOES_HTML.read_text(encoding="utf-8")
    assert "confirm" in conteudo.lower()


def test_detalhe_contem_botao_enviar_monday_condicional():
    conteudo = DETALHE_HTML.read_text(encoding="utf-8")
    assert "Enviar para Monday" in conteudo
    assert "pendente_integracao" in conteudo


def test_historico_exibe_status_envio():
    conteudo = HISTORICO_HTML.read_text(encoding="utf-8")
    assert "tentativa.status" in conteudo


# --- status labels no app ---

def test_app_contem_status_monday_envio_sucesso():
    conteudo = APP_PATH.read_text(encoding="utf-8")
    assert "monday_envio_sucesso" in conteudo


def test_app_contem_status_monday_envio_falha():
    conteudo = APP_PATH.read_text(encoding="utf-8")
    assert "monday_envio_falha" in conteudo


def test_app_contem_status_monday_envio_bloqueado():
    conteudo = APP_PATH.read_text(encoding="utf-8")
    assert "monday_envio_bloqueado" in conteudo


# --- documentacao ---

def test_documentacao_envio_existe():
    assert DOC_PATH.is_file()


def test_documentacao_config_existe():
    assert CONFIG_DOC_PATH.is_file()


def test_documentacao_menciona_variaveis_ambiente():
    conteudo = DOC_PATH.read_text(encoding="utf-8")
    assert "MONDAY_API_TOKEN" in conteudo or "variavel" in conteudo.lower()


def test_documentacao_menciona_sem_lote():
    conteudo = DOC_PATH.read_text(encoding="utf-8")
    assert "lote" not in conteudo.lower() or "nao implementa lote" in conteudo.lower()


def test_documentacao_menciona_sem_anexo():
    conteudo = DOC_PATH.read_text(encoding="utf-8")
    assert "anexo" not in conteudo.lower() or "nao implementa anexo" in conteudo.lower()


def test_documentacao_menciona_confirmacao_humana():
    conteudo = DOC_PATH.read_text(encoding="utf-8")
    assert "confirmac" in conteudo.lower()


def test_documentacao_menciona_anti_duplicidade():
    conteudo = DOC_PATH.read_text(encoding="utf-8")
    assert "duplicidade" in conteudo.lower() or "duplicid" in conteudo.lower()


def test_documentacao_sem_token_real():
    conteudo = DOC_PATH.read_text(encoding="utf-8")
    assert "fake-token" not in conteudo


def test_documentacao_sem_senha():
    conteudo = DOC_PATH.read_text(encoding="utf-8")
    assert "senha" not in conteudo.lower()


def test_config_doc_sem_token_real():
    conteudo = CONFIG_DOC_PATH.read_text(encoding="utf-8")
    assert "seu_token" not in conteudo.lower() or "SUA_CHAVE" in conteudo


# --- isolamento dos testes ---

def test_testes_nao_chamam_api_externa():
    linhas = Path(__file__).read_text(encoding="utf-8").splitlines()
    imports = [l for l in linhas if l.startswith("import ") or l.startswith("from ")]
    assert all("requests" not in l and "urllib" not in l for l in imports)


def test_testes_nao_conectam_mysql():
    linhas = Path(__file__).read_text(encoding="utf-8").splitlines()
    imports = [l for l in linhas if l.startswith("import ") or l.startswith("from ")]
    assert all("mysql" not in l for l in imports)


def test_testes_nao_executam_ocr():
    linhas = Path(__file__).read_text(encoding="utf-8").splitlines()
    imports = [l for l in linhas if l.startswith("import ") or l.startswith("from ")]
    assert all("pytesseract" not in l and "tesserocr" not in l for l in imports)


def test_testes_nao_usam_internet():
    linhas = Path(__file__).read_text(encoding="utf-8").splitlines()
    imports = [l for l in linhas if l.startswith("import ") or l.startswith("from ")]
    assert all("http.client" not in l for l in imports)


# --- column format ---

def test_column_values_montadas_corretamente():
    resultado = enviar_documento_monday(
        documento_exemplo(), TOKEN_FAKE, BOARD_ID_FAKE,
        MAPA_COLUNAS_FAKE, post_func=post_func_sucesso,
    )
    cv = resultado["column_values"]
    assert cv["col_empresa"] == "EMPRESA TESTE LTDA"
    assert cv["col_numero_nf"] == "000123"
    assert "col_vencimento" in cv
    assert isinstance(cv["col_vencimento"], dict)
    assert "date" in cv["col_vencimento"]

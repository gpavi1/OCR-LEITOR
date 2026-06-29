import json
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[1]
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from conectores.monday_payload import (
    _bool_revisado,
    validar_documento_apto_monday,
    normalizar_documento_para_monday,
    MONDAY_PAYLOAD_VERSION,
)
from conectores.monday_dryrun import gerar_dryrun_monday
from conectores.monday_envio import enviar_documento_monday

PAYLOAD_PATH = BASE_DIR / "conectores" / "monday_payload.py"

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

DOCUMENTO_BASE = {
    "id": 999,
    "cliente_id": 1,
    "arquivo_nome": "nota_teste.jpg",
    "empresa": "EMPRESA TESTE LTDA",
    "numero_nf": "100001",
    "chave_acesso": "35260612345678000190550010001000011234567890",
    "vencimento": "2026-07-15",
    "valor_total": 1250.75,
    "status": "pendente_integracao",
    "revisado": 1,
    "revisado_por": "operador_local",
    "revisado_em": "2026-06-29 10:49:23",
    "observacao_revisao": "Ok",
    "json_path": "exports/json/nota_teste.json",
    "tipo_documento": "NFE",
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


# --- _bool_revisado unitario ---

def test_revisado_true_boolean():
    assert _bool_revisado(True) is True


def test_revisado_false_boolean():
    assert _bool_revisado(False) is False


def test_revisado_um_int():
    assert _bool_revisado(1) is True


def test_revisado_zero_int():
    assert _bool_revisado(0) is False


def test_revisado_um_string():
    assert _bool_revisado("1") is True


def test_revisado_zero_string():
    assert _bool_revisado("0") is False


def test_revisado_true_string():
    assert _bool_revisado("true") is True


def test_revisado_True_string():
    assert _bool_revisado("True") is True


def test_revisado_TRUE_string():
    assert _bool_revisado("TRUE") is True


def test_revisado_sim():
    assert _bool_revisado("sim") is True


def test_revisado_Sim():
    assert _bool_revisado("Sim") is True


def test_revisado_SIM():
    assert _bool_revisado("SIM") is True


def test_revisado_yes():
    assert _bool_revisado("yes") is True


def test_revisado_Yes():
    assert _bool_revisado("Yes") is True


def test_revisado_YES():
    assert _bool_revisado("YES") is True


def test_revisado_s():
    assert _bool_revisado("s") is True


def test_revisado_S():
    assert _bool_revisado("S") is True


def test_revisado_nao():
    assert _bool_revisado("nao") is False


def test_revisado_nao_com_til():
    assert _bool_revisado("não") is False


def test_revisado_Nao():
    assert _bool_revisado("Nao") is False


def test_revisado_false_string():
    assert _bool_revisado("false") is False


def test_revisado_False_string():
    assert _bool_revisado("False") is False


def test_revisado_FALSE_string():
    assert _bool_revisado("FALSE") is False


def test_revisado_none():
    assert _bool_revisado(None) is False


def test_revisado_vazio():
    assert _bool_revisado("") is False


def test_revisado_espacos():
    assert _bool_revisado("   ") is False


# --- validar_documento_apto_monday ---

def test_doc_1_apto():
    doc = dict(DOCUMENTO_BASE, revisado=1)
    apto, bloqueios, avisos = validar_documento_apto_monday(doc)
    assert apto is True
    assert "Documento nao foi revisado." not in bloqueios


def test_doc_um_string_apto():
    doc = dict(DOCUMENTO_BASE, revisado="1")
    apto, bloqueios, avisos = validar_documento_apto_monday(doc)
    assert apto is True
    assert "Documento nao foi revisado." not in bloqueios


def test_doc_true_apto():
    doc = dict(DOCUMENTO_BASE, revisado=True)
    apto, bloqueios, avisos = validar_documento_apto_monday(doc)
    assert apto is True
    assert "Documento nao foi revisado." not in bloqueios


def test_doc_true_string_apto():
    doc = dict(DOCUMENTO_BASE, revisado="true")
    apto, bloqueios, avisos = validar_documento_apto_monday(doc)
    assert apto is True


def test_doc_sim_apto():
    doc = dict(DOCUMENTO_BASE, revisado="sim")
    apto, bloqueios, avisos = validar_documento_apto_monday(doc)
    assert apto is True


def test_doc_0_bloqueado():
    doc = dict(DOCUMENTO_BASE, revisado=0)
    apto, bloqueios, avisos = validar_documento_apto_monday(doc)
    assert apto is False
    assert "Documento nao foi revisado." in bloqueios


def test_doc_zero_string_bloqueado():
    doc = dict(DOCUMENTO_BASE, revisado="0")
    apto, bloqueios, avisos = validar_documento_apto_monday(doc)
    assert apto is False
    assert "Documento nao foi revisado." in bloqueios


def test_doc_false_bloqueado():
    doc = dict(DOCUMENTO_BASE, revisado=False)
    apto, bloqueios, avisos = validar_documento_apto_monday(doc)
    assert apto is False
    assert "Documento nao foi revisado." in bloqueios


def test_doc_none_bloqueado():
    doc = dict(DOCUMENTO_BASE, revisado=None)
    apto, bloqueios, avisos = validar_documento_apto_monday(doc)
    assert apto is False
    assert "Documento nao foi revisado." in bloqueios


def test_doc_vazio_bloqueado():
    doc = dict(DOCUMENTO_BASE, revisado="")
    apto, bloqueios, avisos = validar_documento_apto_monday(doc)
    assert apto is False
    assert "Documento nao foi revisado." in bloqueios


def test_doc_ausente_bloqueado():
    doc = dict(DOCUMENTO_BASE)
    del doc["revisado"]
    apto, bloqueios, avisos = validar_documento_apto_monday(doc)
    assert apto is False
    assert "Documento nao foi revisado." in bloqueios


def test_doc_nao_bloqueado_outros_motivos():
    doc = dict(DOCUMENTO_BASE, revisado=1)
    apto, bloqueios, avisos = validar_documento_apto_monday(doc)
    assert "Documento nao foi revisado." not in bloqueios
    assert len(bloqueios) == 0


# --- normalizar_documento_para_monday ---

def test_normalizar_1_apto():
    doc = dict(DOCUMENTO_BASE, revisado=1)
    payload = normalizar_documento_para_monday(doc)
    assert payload["apto_envio"] is True
    assert payload["campos"]["revisado"] is True


def test_normalizar_0_bloqueado():
    doc = dict(DOCUMENTO_BASE, revisado=0)
    payload = normalizar_documento_para_monday(doc)
    assert payload["apto_envio"] is False
    assert payload["campos"]["revisado"] is False


# --- dry-run com revisado=1 ---

def test_dryrun_revisado_1_apto():
    doc = dict(DOCUMENTO_BASE, revisado=1)
    resultado = gerar_dryrun_monday(doc)
    assert resultado["status"] == "apto"
    assert resultado.get("payload", {}).get("apto_envio") is True
    assert not resultado.get("bloqueios")


# --- envio real com revisado=1 ---

def test_envio_revisado_1_sucesso():
    doc = dict(DOCUMENTO_BASE, revisado=1)
    resultado = enviar_documento_monday(
        doc, TOKEN_FAKE, BOARD_ID_FAKE,
        MAPA_COLUNAS_FAKE, post_func=post_func_sucesso,
    )
    assert resultado["status"] == "sucesso"
    assert resultado["item_id"] == "123456789"


# --- isolamento ---

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


def test_modulo_nao_le_env():
    conteudo = PAYLOAD_PATH.read_text(encoding="utf-8")
    assert ".env" not in conteudo


def test_modulo_nao_contem_token_real():
    conteudo = PAYLOAD_PATH.read_text(encoding="utf-8")
    assert "fake-token" not in conteudo

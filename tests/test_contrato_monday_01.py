import sys
import re
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[1]
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from conectores.monday_payload import (
    MONDAY_PAYLOAD_VERSION,
    normalizar_documento_para_monday,
    montar_column_values_monday,
    validar_documento_apto_monday,
    _texto_ou_none,
    _bool_revisado,
    _normalizar_data_iso,
    _normalizar_decimal,
    _montar_item_name,
)

PAYLOAD_PATH = BASE_DIR / "conectores" / "monday_payload.py"
DOC_PATH = BASE_DIR / "docs" / "integracao" / "CONTRATO-MONDAY-01_PAYLOAD_REVISADO.md"


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


MAPA_COLUNAS_FAKE = {
    "empresa": "col_empresa",
    "numero_nf": "col_nf",
    "chave_acesso": "col_chave",
    "vencimento": "col_vencimento",
    "valor_total": "col_valor",
    "observacao_revisao": "col_obs",
}


# --- Existencia ---

def test_modulo_existe():
    assert PAYLOAD_PATH.is_file()


def test_versao_definida():
    assert MONDAY_PAYLOAD_VERSION == "monday_payload_revisado.v1"


# --- normalizar_documento_para_monday ---

def test_payload_versao_correta():
    doc = documento_exemplo()
    payload = normalizar_documento_para_monday(doc)
    assert payload["versao"] == MONDAY_PAYLOAD_VERSION


def test_payload_documento_apto_true():
    doc = documento_exemplo()
    payload = normalizar_documento_para_monday(doc)
    assert payload["apto_envio"] is True
    assert payload["bloqueios"] == []


def test_payload_documento_pendente_revisao_apto_false():
    doc = documento_exemplo(status="pendente_revisao")
    payload = normalizar_documento_para_monday(doc)
    assert payload["apto_envio"] is False
    assert any("pendente_revisao" in b for b in payload["bloqueios"])


def test_payload_documento_erro_ocr_apto_false():
    doc = documento_exemplo(status="erro_ocr", revisado=False)
    payload = normalizar_documento_para_monday(doc)
    assert payload["apto_envio"] is False
    assert any("erro_ocr" in b for b in payload["bloqueios"])


def test_payload_documento_sem_revisao_apto_false():
    doc = documento_exemplo(revisado=False)
    payload = normalizar_documento_para_monday(doc)
    assert payload["apto_envio"] is False
    assert any("revisado" in b.lower() for b in payload["bloqueios"])


def test_payload_documento_sem_empresa_bloqueia():
    doc = documento_exemplo(empresa=None)
    payload = normalizar_documento_para_monday(doc)
    assert payload["apto_envio"] is False
    assert any("empresa" in b.lower() for b in payload["bloqueios"])


def test_payload_documento_sem_nf_e_sem_chave_bloqueia():
    doc = documento_exemplo(numero_nf=None, chave_acesso=None)
    payload = normalizar_documento_para_monday(doc)
    assert payload["apto_envio"] is False
    assert any("ambos vazios" in b.lower() for b in payload["bloqueios"])


def test_payload_nfse_sem_chave_nao_bloqueia():
    doc = documento_exemplo(tipo_documento="NFS-e", chave_acesso=None, numero_nf="001234")
    payload = normalizar_documento_para_monday(doc)
    assert payload["apto_envio"] is True
    assert any("chave" in a.lower() for a in payload["avisos"])


def test_payload_valor_vazio_aviso_nao_bloqueio():
    doc = documento_exemplo(valor_total=None)
    payload = normalizar_documento_para_monday(doc)
    assert payload["apto_envio"] is True
    assert any("valor total" in a.lower() for a in payload["avisos"])


def test_payload_vencimento_vazio_aviso_nao_bloqueio():
    doc = documento_exemplo(vencimento=None)
    payload = normalizar_documento_para_monday(doc)
    assert payload["apto_envio"] is True
    assert any("vencimento" in a.lower() for a in payload["avisos"])


# --- Formatacao de campos ---

def test_data_br_convertida_iso():
    doc = documento_exemplo(vencimento="10/07/2026")
    payload = normalizar_documento_para_monday(doc)
    assert payload["campos"]["vencimento"] == "2026-07-10"


def test_data_iso_mantida():
    doc = documento_exemplo(vencimento="2026-07-10")
    payload = normalizar_documento_para_monday(doc)
    assert payload["campos"]["vencimento"] == "2026-07-10"


def test_valor_br_convertido_decimal():
    doc = documento_exemplo(valor_total="1.250,75")
    payload = normalizar_documento_para_monday(doc)
    assert payload["campos"]["valor_total"] == "1250.75"


def test_valor_float_convertido_string_decimal():
    doc = documento_exemplo(valor_total=150.00)
    payload = normalizar_documento_para_monday(doc)
    assert payload["campos"]["valor_total"] == "150.00"


def test_valor_decimal_seguro():
    from decimal import Decimal
    doc = documento_exemplo(valor_total=Decimal("1250.75"))
    payload = normalizar_documento_para_monday(doc)
    assert payload["campos"]["valor_total"] == "1250.75"


def test_item_name_com_nf():
    doc = documento_exemplo(empresa="EMPRESA TESTE LTDA", numero_nf="000123")
    payload = normalizar_documento_para_monday(doc)
    assert payload["item_name"] == "EMPRESA TESTE LTDA - NF 000123"


def test_item_name_sem_nf_usando_id():
    doc = documento_exemplo(numero_nf=None)
    payload = normalizar_documento_para_monday(doc)
    assert "ID" in payload["item_name"]
    assert str(doc["id"]) in payload["item_name"]


# --- montar_column_values_monday ---

def test_montar_column_values_usando_mapa_fake():
    doc = documento_exemplo()
    payload = normalizar_documento_para_monday(doc)
    col_values = montar_column_values_monday(payload, MAPA_COLUNAS_FAKE)
    assert col_values["col_empresa"] == "EMPRESA TESTE LTDA"
    assert col_values["col_nf"] == "000123"
    assert col_values["col_chave"] == "3511112222333344445555666677778888"


def test_montar_column_values_nao_usa_ids_reais():
    doc = documento_exemplo()
    payload = normalizar_documento_para_monday(doc)
    col_values = montar_column_values_monday(payload, MAPA_COLUNAS_FAKE)
    for chave in col_values:
        assert not chave.startswith("col_") or chave in MAPA_COLUNAS_FAKE.values()


def test_montar_column_values_data_como_dict_date():
    doc = documento_exemplo(vencimento="2026-07-10")
    payload = normalizar_documento_para_monday(doc)
    col_values = montar_column_values_monday(payload, MAPA_COLUNAS_FAKE)
    assert col_values["col_vencimento"] == {"date": "2026-07-10"}


# --- Seguranca do modulo ---

def test_modulo_nao_importa_requests():
    conteudo = PAYLOAD_PATH.read_text(encoding="utf-8")
    # nao deve importar requests, urllib, http.client, socket
    padroes_proibidos = [
        "import requests",
        "from requests",
        "import urllib",
        "from urllib",
        "import http.client",
        "from http.client",
        "import socket",
        "from socket",
    ]
    for padrao in padroes_proibidos:
        assert padrao not in conteudo, f"Modulo nao deve conter: {padrao}"


def test_modulo_nao_contem_url_monday():
    conteudo = PAYLOAD_PATH.read_text(encoding="utf-8")
    assert "api.monday.com" not in conteudo


def test_modulo_nao_le_env():
    conteudo = PAYLOAD_PATH.read_text(encoding="utf-8")
    assert ".env" not in conteudo


def test_modulo_nao_usa_os_getenv():
    conteudo = PAYLOAD_PATH.read_text(encoding="utf-8")
    assert "os.getenv" not in conteudo
    assert "os.environ" not in conteudo


def test_modulo_nao_contem_token():
    conteudo = PAYLOAD_PATH.read_text(encoding="utf-8")
    assert "token" not in conteudo.lower()


# --- Documentacao ---

def test_documentacao_existe():
    assert DOC_PATH.is_file()


def test_documentacao_menciona_revisao_humana_obrigatoria():
    conteudo = DOC_PATH.read_text(encoding="utf-8")
    assert "revis" in conteudo.lower()
    assert "humana" in conteudo.lower() or "humano" in conteudo.lower()


def test_documentacao_menciona_sem_envio_real():
    conteudo = DOC_PATH.read_text(encoding="utf-8")
    assert "nao envia" in conteudo.lower() or "nao há envio" in conteudo.lower()


def test_documentacao_menciona_dryrun():
    conteudo = DOC_PATH.read_text(encoding="utf-8")
    assert "dry-run" in conteudo.lower() or "dryrun" in conteudo.lower() or "MONDAY-DRYRUN-01" in conteudo


def test_documentacao_sem_senha():
    conteudo = DOC_PATH.read_text(encoding="utf-8")
    assert "senha" not in conteudo.lower()


def test_documentacao_sem_token_real():
    conteudo = DOC_PATH.read_text(encoding="utf-8")
    for linha in conteudo.splitlines():
        if "token" in linha.lower():
            assert "seu_token" not in linha.lower()


# --- Testes de validacao de borda ---

def test_validacao_documento_nulo():
    apto, bloqueios, avisos = validar_documento_apto_monday(None)
    assert apto is False
    assert len(bloqueios) > 0


def test_validacao_documento_sem_id():
    doc = documento_exemplo(id=None)
    apto, bloqueios, avisos = validar_documento_apto_monday(doc)
    assert apto is False
    assert any("id" in b.lower() for b in bloqueios)


def test_validacao_documento_sem_status():
    doc = documento_exemplo(status=None)
    apto, bloqueios, avisos = validar_documento_apto_monday(doc)
    assert apto is False
    assert any("status" in b.lower() for b in bloqueios)


def test_validacao_documento_status_recebido():
    doc = documento_exemplo(status="recebido", revisado=False)
    apto, bloqueios, avisos = validar_documento_apto_monday(doc)
    assert apto is False
    assert any("recebido" in b.lower() for b in bloqueios)


def test_validacao_documento_status_processando():
    doc = documento_exemplo(status="processando", revisado=False)
    apto, bloqueios, avisos = validar_documento_apto_monday(doc)
    assert apto is False
    assert any("processando" in b.lower() for b in bloqueios)


def test_validacao_observacao_vazia_aviso():
    doc = documento_exemplo(observacao_revisao=None)
    apto, bloqueios, avisos = validar_documento_apto_monday(doc)
    assert apto is True
    assert any("observacao" in a.lower() for a in avisos)


def test_validacao_json_path_vazio_aviso():
    doc = documento_exemplo(json_path=None)
    apto, bloqueios, avisos = validar_documento_apto_monday(doc)
    assert apto is True
    assert any("json" in a.lower() for a in avisos)


# --- Normalizacao de campos vazios ---

def test_campos_vazios_viram_none():
    doc = documento_exemplo(
        empresa="",
        numero_nf="",
        chave_acesso="   ",
        vencimento="",
        observacao_revisao=None,
    )
    payload = normalizar_documento_para_monday(doc)
    assert payload["campos"]["empresa"] is None
    assert payload["campos"]["numero_nf"] is None
    assert payload["campos"]["chave_acesso"] is None
    assert payload["campos"]["vencimento"] is None
    assert payload["campos"]["observacao_revisao"] is None


# --- metadados ---

def test_metadados_envio_real_false():
    doc = documento_exemplo()
    payload = normalizar_documento_para_monday(doc)
    assert payload["metadados"]["envio_real"] is False
    assert payload["metadados"]["requer_confirmacao_humana"] is True
    assert payload["metadados"]["integracao"] == "monday"


# --- Seguranca dos testes ---

def test_teste_nao_conecta_mysql():
    linhas = Path(__file__).read_text(encoding="utf-8").splitlines()
    import_ok = all("mysql" not in l and "MySQL" not in l for l in linhas if l.startswith("import") or l.startswith("from"))
    assert import_ok, "Nenhum import deve referenciar mysql"


def test_teste_nao_executa_ocr_real():
    linhas = Path(__file__).read_text(encoding="utf-8").splitlines()
    import_ok = all("pytesseract" not in l and "tesserocr" not in l for l in linhas if l.startswith("import") or l.startswith("from"))
    assert import_ok, "Nenhum import deve referenciar OCR"


def test_teste_nao_exige_internet():
    linhas = Path(__file__).read_text(encoding="utf-8").splitlines()
    import_ok = all(
        "requests" not in l and "urllib" not in l and "http.client" not in l
        for l in linhas if l.startswith("import") or l.startswith("from")
    )
    assert import_ok, "Nenhum import deve referenciar biblioteca de rede"


# --- Modulo nao tem acesso a rede ---

def test_modulo_nao_chama_api():
    conteudo = PAYLOAD_PATH.read_text(encoding="utf-8")
    assert "requests." not in conteudo
    assert "urllib." not in conteudo
    assert "http." not in conteudo


# --- Seguranca extra ---

def test_modulo_nao_abre_arquivo_real():
    conteudo = PAYLOAD_PATH.read_text(encoding="utf-8")
    assert "open(" not in conteudo


def test_modulo_nao_contem_board_id():
    conteudo = PAYLOAD_PATH.read_text(encoding="utf-8")
    assert "board_id" not in conteudo.lower()


def test_modulo_nao_contem_api_key():
    conteudo = PAYLOAD_PATH.read_text(encoding="utf-8")
    assert "api_key" not in conteudo.lower()


def test_montar_column_values_mapa_vazio():
    doc = documento_exemplo()
    payload = normalizar_documento_para_monday(doc)
    col_values = montar_column_values_monday(payload, {})
    assert col_values == {}


def test_montar_column_values_mapa_parcial():
    doc = documento_exemplo()
    payload = normalizar_documento_para_monday(doc)
    col_values = montar_column_values_monday(payload, {"empresa": "col_empresa"})
    assert "col_empresa" in col_values
    assert "col_nf" not in col_values


def test_payload_origem_correta():
    doc = documento_exemplo()
    payload = normalizar_documento_para_monday(doc)
    assert payload["origem"] == "ocr-leitor.documentos"


def test_payload_documento_id_presente():
    doc = documento_exemplo()
    payload = normalizar_documento_para_monday(doc)
    assert payload["documento_id"] == 123
    assert payload["cliente_id"] == 1

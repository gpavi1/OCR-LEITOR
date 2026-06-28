from copy import deepcopy

from contratos.contrato_documento_fiscal_v1 import (
    validar_contrato_documento_fiscal_v1,
)
from contratos.montador_documento_fiscal_v1 import montar_payload_documento_fiscal_v1


def dados_documento_validos():
    return {
        "empresa": "EMPRESA EXEMPLO LTDA",
        "numero_nf": "123456",
        "chave_acesso": "0" * 44,
        "vencimento": "30/08/2026",
        "valor_total": "150.00",
        "revisado": True,
        "revisado_por": "operador_local",
        "revisado_em": "2026-06-28T00:00:00",
        "arquivo_nome": "documento_exemplo.pdf",
        "json_path": "output/json/documento_exemplo.json",
        "gerado_em": "2026-06-28T00:00:00",
    }


def test_montador_documento_fiscal_v1_monta_payload_valido():
    payload = montar_payload_documento_fiscal_v1(dados_documento_validos())

    assert payload["origem"] == "OCR-LEITOR"
    assert payload["versao_contrato"] == "ocr_leitor.documento_fiscal.v1"
    assert payload["documento"]["empresa"] == "EMPRESA EXEMPLO LTDA"
    assert payload["revisao"]["revisado"] is True
    assert payload["integracao"]["destino"] == "fechames_fiscal"
    assert payload["integracao"]["modo"] == "simulado"


def test_montador_documento_fiscal_v1_payload_passa_no_validador():
    payload = montar_payload_documento_fiscal_v1(dados_documento_validos())

    assert validar_contrato_documento_fiscal_v1(payload) is True


def test_montador_documento_fiscal_v1_preenche_confianca_com_none():
    payload = montar_payload_documento_fiscal_v1(dados_documento_validos())

    assert payload["confianca"] == {
        "empresa": None,
        "numero_nf": None,
        "chave_acesso": None,
        "vencimento": None,
        "valor_total": None,
    }


def test_montador_documento_fiscal_v1_rejeita_nao_revisado():
    dados = deepcopy(dados_documento_validos())
    dados["revisado"] = False

    try:
        montar_payload_documento_fiscal_v1(dados)
    except ValueError:
        return

    assert False, "documento nao revisado deveria ser rejeitado"


def test_montador_documento_fiscal_v1_rejeita_empresa_vazia():
    dados = deepcopy(dados_documento_validos())
    dados["empresa"] = ""

    try:
        montar_payload_documento_fiscal_v1(dados)
    except ValueError:
        return

    assert False, "empresa vazia deveria ser rejeitada"


def test_montador_documento_fiscal_v1_rejeita_chave_invalida():
    dados = deepcopy(dados_documento_validos())
    dados["chave_acesso"] = "0" * 43

    try:
        montar_payload_documento_fiscal_v1(dados)
    except ValueError:
        return

    assert False, "chave_acesso invalida deveria ser rejeitada"


def test_montador_documento_fiscal_v1_rejeita_dados_documento_nao_dict():
    try:
        montar_payload_documento_fiscal_v1(None)
    except ValueError:
        return

    assert False, "dados_documento nao dict deveria ser rejeitado"

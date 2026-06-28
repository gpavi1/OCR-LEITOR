from copy import deepcopy

from compatibilidade.validador_fechames_v1 import validar_compatibilidade_fechames_v1
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


def payload_valido():
    return montar_payload_documento_fiscal_v1(dados_documento_validos())


def test_validador_compatibilidade_fechames_v1_aceita_payload_valido():
    resultado = validar_compatibilidade_fechames_v1(payload_valido())

    assert resultado["compativel"] is True
    assert resultado["erros"] == []
    assert resultado["destino"] == "fechames_fiscal"
    assert resultado["modo"] == "simulado"


def test_validador_compatibilidade_fechames_v1_rejeita_destino_invalido():
    payload = deepcopy(payload_valido())
    payload["integracao"]["destino"] = "outro_destino"

    resultado = validar_compatibilidade_fechames_v1(payload)

    assert resultado["compativel"] is False
    assert resultado["erros"]


def test_validador_compatibilidade_fechames_v1_rejeita_modo_nao_simulado():
    payload = deepcopy(payload_valido())
    payload["integracao"]["modo"] = "producao"

    resultado = validar_compatibilidade_fechames_v1(payload)

    assert resultado["compativel"] is False
    assert resultado["erros"]


def test_validador_compatibilidade_fechames_v1_rejeita_empresa_vazia():
    payload = deepcopy(payload_valido())
    payload["documento"]["empresa"] = ""

    resultado = validar_compatibilidade_fechames_v1(payload)
    assert resultado["compativel"] is False
    assert resultado["erros"]


def test_validador_compatibilidade_fechames_v1_rejeita_valor_total_invalido():
    payload = deepcopy(payload_valido())
    payload["documento"]["valor_total"] = "valor-invalido"

    resultado = validar_compatibilidade_fechames_v1(payload)
    assert resultado["compativel"] is False
    assert resultado["erros"]


def test_validador_compatibilidade_fechames_v1_rejeita_sem_numero_nf_e_chave():
    payload = deepcopy(payload_valido())
    payload["documento"]["numero_nf"] = ""
    payload["documento"]["chave_acesso"] = ""

    resultado = validar_compatibilidade_fechames_v1(payload)
    assert resultado["compativel"] is False
    assert resultado["erros"]


def test_validador_compatibilidade_fechames_v1_rejeita_chave_com_tamanho_invalido():
    payload = deepcopy(payload_valido())
    payload["documento"]["chave_acesso"] = "0" * 43

    resultado = validar_compatibilidade_fechames_v1(payload)
    assert resultado["compativel"] is False
    assert resultado["erros"]


def test_validador_compatibilidade_fechames_v1_rejeita_payload_nao_dict():
    resultado = validar_compatibilidade_fechames_v1(None)

    assert resultado["compativel"] is False
    assert resultado["erros"]
    assert resultado["destino"] is None
    assert resultado["modo"] is None

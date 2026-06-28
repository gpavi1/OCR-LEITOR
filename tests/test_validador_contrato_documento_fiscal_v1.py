from copy import deepcopy
import json
from pathlib import Path

from contratos.contrato_documento_fiscal_v1 import (
    validar_contrato_documento_fiscal_v1,
)


def carregar_payload_exemplo():
    caminho = (
        Path(__file__).resolve().parents[1]
        / "docs"
        / "exemplos"
        / "documento_fiscal_v1.exemplo.json"
    )
    return json.loads(caminho.read_text(encoding="utf-8"))


def assert_payload_invalido(payload):
    try:
        validar_contrato_documento_fiscal_v1(payload)
    except ValueError:
        return

    assert False, "payload invalido deveria levantar ValueError"


def test_validador_contrato_documento_fiscal_v1_aceita_exemplo():
    payload = carregar_payload_exemplo()

    assert validar_contrato_documento_fiscal_v1(payload) is True


def test_validador_contrato_documento_fiscal_v1_rejeita_origem_invalida():
    payload = deepcopy(carregar_payload_exemplo())
    payload["origem"] = "OUTRO-SISTEMA"

    assert_payload_invalido(payload)


def test_validador_contrato_documento_fiscal_v1_rejeita_versao_invalida():
    payload = deepcopy(carregar_payload_exemplo())
    payload["versao_contrato"] = "ocr_leitor.documento_fiscal.v2"

    assert_payload_invalido(payload)


def test_validador_contrato_documento_fiscal_v1_rejeita_nao_revisado():
    payload = deepcopy(carregar_payload_exemplo())
    payload["revisao"]["revisado"] = False

    assert_payload_invalido(payload)


def test_validador_contrato_documento_fiscal_v1_rejeita_empresa_vazia():
    payload = deepcopy(carregar_payload_exemplo())
    payload["documento"]["empresa"] = ""

    assert_payload_invalido(payload)


def test_validador_contrato_documento_fiscal_v1_rejeita_sem_numero_nf_e_chave():
    payload = deepcopy(carregar_payload_exemplo())
    payload["documento"]["numero_nf"] = ""
    payload["documento"]["chave_acesso"] = ""

    assert_payload_invalido(payload)


def test_validador_contrato_documento_fiscal_v1_rejeita_chave_com_tamanho_invalido():
    payload = deepcopy(carregar_payload_exemplo())
    payload["documento"]["chave_acesso"] = "0" * 43

    assert_payload_invalido(payload)


def test_validador_contrato_documento_fiscal_v1_rejeita_chave_com_letra():
    payload = deepcopy(carregar_payload_exemplo())
    payload["documento"]["chave_acesso"] = "0" * 43 + "A"

    assert_payload_invalido(payload)


def test_validador_contrato_documento_fiscal_v1_rejeita_valor_total_invalido():
    payload = deepcopy(carregar_payload_exemplo())
    payload["documento"]["valor_total"] = "valor-invalido"

    assert_payload_invalido(payload)

import json
from pathlib import Path

from compatibilidade.validador_fechames_v1 import validar_compatibilidade_fechames_v1
from contratos.contrato_documento_fiscal_v1 import validar_contrato_documento_fiscal_v1


def carregar_payload_sandbox():
    caminho = (
        Path(__file__).resolve().parents[1]
        / "docs"
        / "sandbox"
        / "fechames_documento_fiscal_v1.sandbox.json"
    )
    return json.loads(caminho.read_text(encoding="utf-8"))


def test_fechames_sandbox_payload_v1_valido_e_compativel():
    payload = carregar_payload_sandbox()

    assert validar_contrato_documento_fiscal_v1(payload) is True

    resultado = validar_compatibilidade_fechames_v1(payload)
    assert resultado["compativel"] is True
    assert resultado["destino"] == "fechames_fiscal"
    assert resultado["modo"] == "simulado"

    empresa = payload["documento"]["empresa"]
    assert "SANDBOX" in empresa or "EXEMPLO" in empresa
    assert payload["documento"]["chave_acesso"] == "0" * 44

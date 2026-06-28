from copy import deepcopy
import json
from pathlib import Path

from conectores.fluxo_simulado_documento_fiscal_v1 import (
    exportar_documento_fiscal_v1_simulado,
)


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


def test_fluxo_simulado_documento_fiscal_v1_exporta_json_em_tmp_path(tmp_path):
    resultado = exportar_documento_fiscal_v1_simulado(
        dados_documento_validos(),
        tmp_path,
    )

    caminho = Path(resultado["caminho"])
    assert resultado["status"] == "exportado_simulado"
    assert resultado["modo"] == "simulado"
    assert resultado["destino"] == "fechames_fiscal"
    assert caminho.exists()
    assert caminho.parent.resolve() == tmp_path.resolve()

    payload = json.loads(caminho.read_text(encoding="utf-8"))
    assert payload["origem"] == "OCR-LEITOR"
    assert payload["versao_contrato"] == "ocr_leitor.documento_fiscal.v1"
    assert payload["integracao"]["modo"] == "simulado"
    assert payload["documento"]["empresa"] == "EMPRESA EXEMPLO LTDA"


def test_fluxo_simulado_documento_fiscal_v1_rejeita_nao_revisado(tmp_path):
    dados = deepcopy(dados_documento_validos())
    dados["revisado"] = False

    try:
        exportar_documento_fiscal_v1_simulado(dados, tmp_path)
    except ValueError:
        return

    assert False, "documento nao revisado deveria ser rejeitado"


def test_fluxo_simulado_documento_fiscal_v1_rejeita_chave_invalida(tmp_path):
    dados = deepcopy(dados_documento_validos())
    dados["chave_acesso"] = "0" * 43

    try:
        exportar_documento_fiscal_v1_simulado(dados, tmp_path)
    except ValueError:
        return

    assert False, "chave_acesso invalida deveria ser rejeitada"


def test_fluxo_simulado_documento_fiscal_v1_aceita_destino_customizado(tmp_path):
    resultado = exportar_documento_fiscal_v1_simulado(
        dados_documento_validos(),
        tmp_path,
        destino="sistema_teste",
    )

    assert resultado["destino"] == "sistema_teste"

    payload = json.loads(Path(resultado["caminho"]).read_text(encoding="utf-8"))
    assert payload["integracao"]["destino"] == "sistema_teste"

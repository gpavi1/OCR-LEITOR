from copy import deepcopy
import json
from pathlib import Path

from conectores.conector_simulado import exportar_json_simulado


def carregar_payload_exemplo():
    caminho = (
        Path(__file__).resolve().parents[1]
        / "docs"
        / "exemplos"
        / "documento_fiscal_v1.exemplo.json"
    )
    return json.loads(caminho.read_text(encoding="utf-8"))


def test_conector_simulado_exporta_json_em_tmp_path(tmp_path):
    payload = carregar_payload_exemplo()

    caminho_salvo = Path(exportar_json_simulado(payload, tmp_path))

    assert caminho_salvo.exists()
    assert caminho_salvo.suffix == ".json"
    assert caminho_salvo.parent.resolve() == tmp_path.resolve()

    salvo = json.loads(caminho_salvo.read_text(encoding="utf-8"))
    assert salvo["origem"] == "OCR-LEITOR"
    assert salvo["versao_contrato"] == "ocr_leitor.documento_fiscal.v1"
    assert salvo["integracao"]["modo"] == "simulado"


def test_conector_simulado_rejeita_documento_nao_revisado(tmp_path):
    payload = deepcopy(carregar_payload_exemplo())
    payload["revisao"]["revisado"] = False

    try:
        exportar_json_simulado(payload, tmp_path)
    except ValueError:
        return

    assert False, "documento nao revisado deveria ser rejeitado"


def test_conector_simulado_rejeita_modo_nao_simulado(tmp_path):
    payload = deepcopy(carregar_payload_exemplo())
    payload["integracao"]["modo"] = "producao"

    try:
        exportar_json_simulado(payload, tmp_path)
    except ValueError:
        return

    assert False, "modo diferente de simulado deveria ser rejeitado"

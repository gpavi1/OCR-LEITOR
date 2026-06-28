from decimal import Decimal
import json
from pathlib import Path


def carregar_contrato_exemplo():
    caminho = (
        Path(__file__).resolve().parents[1]
        / "docs"
        / "exemplos"
        / "documento_fiscal_v1.exemplo.json"
    )
    return json.loads(caminho.read_text(encoding="utf-8"))


def test_contrato_json_v1_tem_campos_raiz_obrigatorios():
    dados = carregar_contrato_exemplo()

    for campo in [
        "origem",
        "versao_contrato",
        "documento",
        "revisao",
        "confianca",
        "integracao",
        "metadados",
    ]:
        assert campo in dados


def test_contrato_json_v1_tem_identidade_e_status_validos():
    dados = carregar_contrato_exemplo()

    assert dados["origem"] == "OCR-LEITOR"
    assert dados["versao_contrato"] == "ocr_leitor.documento_fiscal.v1"
    assert dados["revisao"]["revisado"] is True
    assert dados["integracao"]["status"] == "pronto_para_destino"
    assert dados["integracao"]["modo"] == "simulado"


def test_contrato_json_v1_tem_documento_minimo_valido():
    dados = carregar_contrato_exemplo()
    documento = dados["documento"]

    assert documento["empresa"]
    assert documento.get("numero_nf") or documento.get("chave_acesso")

    chave = documento.get("chave_acesso")
    if chave:
        assert len(chave) == 44
        assert chave.isdigit()

    Decimal(documento["valor_total"])


def test_contrato_json_v1_nao_usa_dados_reais_no_exemplo():
    dados = carregar_contrato_exemplo()
    documento = dados["documento"]

    assert "EXEMPLO" in documento["empresa"]
    assert documento["chave_acesso"] == "0" * 44

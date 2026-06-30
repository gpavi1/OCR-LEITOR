from copy import deepcopy
from datetime import datetime
from decimal import Decimal
import json
from pathlib import Path
import sys

BASE_DIR = Path(__file__).resolve().parents[1]
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from contratos.contrato_documento_fiscal_v1 import validar_contrato_documento_fiscal_v1
from exportacao.json_validado import (
    EXPORT_DIR_RELATIVO,
    DESTINO_EXPORTACAO_LOCAL,
    MODO_EXPORTACAO_LOCAL,
    STATUS_DOCUMENTO_EXPORTAVEL,
    exportar_documento_revisado,
    gerar_nome_arquivo_exportacao,
    montar_payload_exportacao_documento,
)
from web.app import app

EXPORTADOR_PATH = BASE_DIR / "exportacao" / "json_validado.py"
DOC_PATH = BASE_DIR / "docs" / "exportacao" / "EXPORT-OCR-01_JSON_VALIDADO.md"
DETAIL_HTML = BASE_DIR / "web" / "templates" / "documento_detalhe.html"
APP_PATH = BASE_DIR / "web" / "app.py"


def documento_exemplo(status="pendente_integracao", revisado=True):
    return {
        "id": 7,
        "cliente_id": 1,
        "arquivo_nome": "nota fiscal ../../cliente.pdf",
        "empresa": "EMPRESA EXEMPLO LTDA",
        "numero_nf": "123456",
        "chave_acesso": "0" * 44,
        "vencimento": "2026-08-30",
        "valor_total": Decimal("150.00"),
        "status": status,
        "revisado": revisado,
        "revisado_por": "operador_local",
        "revisado_em": datetime(2026, 6, 28, 12, 0, 0),
        "json_path": "output/json/documento_exemplo.json",
        "criado_em": datetime(2026, 6, 28, 11, 0, 0),
        "atualizado_em": datetime(2026, 6, 28, 12, 5, 0),
    }


def obter_documento_fixo(documento):
    return lambda _documento_id: deepcopy(documento)


def test_exportador_existe():
    assert EXPORTADOR_PATH.is_file()


def test_documentacao_exportacao_existe():
    assert DOC_PATH.is_file()


def test_app_contem_rota_exportar_json():
    conteudo = APP_PATH.read_text(encoding="utf-8")
    assert '"/documentos/<int:documento_id>/exportar-json"' in conteudo
    assert 'methods=["POST"]' in conteudo


def test_detalhe_contem_acao_manual_exportar_json():
    conteudo = DETAIL_HTML.read_text(encoding="utf-8")
    assert "/documentos/{{ documento.id }}/exportar-json" in conteudo
    assert "Exportar JSON validado" in conteudo
    assert "exports/json/" in conteudo


def test_exportador_nao_permite_documento_pendente_revisao(tmp_path):
    resultado = exportar_documento_revisado(
        7,
        obter_documento_fixo(documento_exemplo(status="pendente_revisao")),
        root_dir=tmp_path,
    )

    assert resultado["ok"] is False
    assert resultado["status"] == "erro_validacao"
    assert "Status não permite exportação" in resultado["erro"]


def test_exportador_nao_permite_status_incompletos(tmp_path):
    for status in ["recebido", "processando", "erro_ocr"]:
        resultado = exportar_documento_revisado(
            7,
            obter_documento_fixo(documento_exemplo(status=status)),
            root_dir=tmp_path,
        )
        assert resultado["ok"] is False
        assert resultado["status"] == "erro_validacao"


def test_exportador_permite_status_pendente_integracao(tmp_path):
    resultado = exportar_documento_revisado(
        7,
        obter_documento_fixo(documento_exemplo(status="pendente_integracao")),
        root_dir=tmp_path,
    )

    assert resultado["ok"] is True
    assert resultado["status"] == "exportado_local"


def test_exportador_permite_status_integrado(tmp_path):
    resultado = exportar_documento_revisado(
        7,
        obter_documento_fixo(documento_exemplo(status="integrado")),
        root_dir=tmp_path,
    )

    assert resultado["ok"] is True
    assert resultado["status"] == "exportado_local"


def test_exportador_nao_exporta_sem_revisao(tmp_path):
    resultado = exportar_documento_revisado(
        7,
        obter_documento_fixo(documento_exemplo(revisado=False)),
        root_dir=tmp_path,
    )

    assert resultado["ok"] is False
    assert resultado["status"] == "erro_validacao"
    assert "revisado/aprovado" in resultado["erro"]


def test_exportador_cria_arquivo_json_em_pasta_controlada(tmp_path):
    resultado = exportar_documento_revisado(
        7,
        obter_documento_fixo(documento_exemplo()),
        root_dir=tmp_path,
        agora=datetime(2026, 6, 28, 15, 30, 45),
    )

    caminho = tmp_path / resultado["caminho_relativo"]
    assert caminho.exists()
    assert caminho.parent.resolve() == (tmp_path / EXPORT_DIR_RELATIVO).resolve()
    assert caminho.name == "documento_7_20260628153045.json"


def test_exportador_nao_aceita_caminho_arbitrario_do_usuario(tmp_path):
    documento = documento_exemplo()
    documento["arquivo_nome"] = "..\\..\\segredo.pdf"
    resultado = exportar_documento_revisado(
        7,
        obter_documento_fixo(documento),
        root_dir=tmp_path,
        agora=datetime(2026, 6, 28, 15, 30, 45),
    )

    assert resultado["ok"] is True
    assert resultado["caminho_relativo"].startswith("exports/json/")
    assert "segredo" not in Path(resultado["caminho_relativo"]).name
    assert ".." not in resultado["caminho_relativo"]


def test_exportador_sanitiza_nome_do_arquivo():
    nome = gerar_nome_arquivo_exportacao("doc-7../x", agora=datetime(2026, 6, 28, 15, 30, 45))
    assert nome == "documento_7_20260628153045.json"


def test_exportador_usa_contrato_json_oficial():
    payload = montar_payload_exportacao_documento(documento_exemplo())
    assert payload["versao_contrato"] == "ocr_leitor.documento_fiscal.v1"
    assert payload["integracao"]["destino"] == DESTINO_EXPORTACAO_LOCAL
    assert payload["integracao"]["modo"] == MODO_EXPORTACAO_LOCAL


def test_exportador_gera_json_valido(tmp_path):
    resultado = exportar_documento_revisado(
        7,
        obter_documento_fixo(documento_exemplo()),
        root_dir=tmp_path,
    )

    payload = json.loads((tmp_path / resultado["caminho_relativo"]).read_text(encoding="utf-8"))
    assert validar_contrato_documento_fiscal_v1(payload) is True


def test_exportador_falha_de_forma_segura_quando_documento_nao_existe(tmp_path):
    resultado = exportar_documento_revisado(
        999,
        lambda _documento_id: None,
        root_dir=tmp_path,
    )

    assert resultado == {
        "ok": False,
        "status": "documento_nao_encontrado",
        "caminho_relativo": None,
        "erro": "Documento não encontrado.",
    }


def test_exportador_falha_de_forma_segura_quando_payload_nao_e_validado(tmp_path):
    documento = documento_exemplo()
    documento["empresa"] = ""
    resultado = exportar_documento_revisado(
        7,
        obter_documento_fixo(documento),
        root_dir=tmp_path,
    )

    assert resultado["ok"] is False
    assert resultado["status"] == "erro_validacao"
    assert "documento.empresa" in resultado["erro"]


def test_exportador_nao_altera_ocr_parser_ou_pipeline():
    conteudo = EXPORTADOR_PATH.read_text(encoding="utf-8")
    assert "ocr_pipeline_s1" not in conteudo
    assert "parser_nf" not in conteudo
    assert "pytesseract" not in conteudo


def test_exportador_nao_exige_dependencia_nova():
    conteudo = EXPORTADOR_PATH.read_text(encoding="utf-8")
    assert "requests" not in conteudo
    assert "pandas" not in conteudo
    assert "numpy" not in conteudo


def test_exportador_nao_cria_api():
    conteudo = EXPORTADOR_PATH.read_text(encoding="utf-8")
    assert "@app.route" not in conteudo
    assert "/api" not in conteudo
    assert "Blueprint" not in conteudo


def test_exportador_nao_integra_plataformas_externas():
    conteudo = EXPORTADOR_PATH.read_text(encoding="utf-8")
    assert "Monday" not in conteudo and "monday" not in conteudo
    assert "Sheets" not in conteudo and "sheets" not in conteudo
    assert "ERP" not in conteudo and "erp" not in conteudo
    assert "FechaMes" not in conteudo and "fechames" not in conteudo


def test_exportador_nao_escreve_no_banco_do_fechames():
    conteudo = EXPORTADOR_PATH.read_text(encoding="utf-8")
    assert "INSERT INTO" not in conteudo
    assert "UPDATE " not in conteudo
    assert "fechames" not in conteudo.lower()


def test_status_exportavel_usa_status_reais_do_projeto():
    assert STATUS_DOCUMENTO_EXPORTAVEL == {"pendente_integracao", "integrado"}


def test_rota_exportar_json_post_retorna_redirect_e_registra_tentativa(tmp_path, monkeypatch):
    tentativas = []

    def fake_fetch_one(_query, _params):
        return documento_exemplo()

    def fake_registrar(**kwargs):
        tentativas.append(kwargs)
        return 1

    monkeypatch.setattr("web.app.fetch_one", fake_fetch_one)
    monkeypatch.setattr("web.app._obter_integracao_manual", lambda _cliente_id: 99)
    monkeypatch.setattr("web.app._registrar_tentativa_integracao", fake_registrar)
    monkeypatch.setattr("web.app.ROOT_DIR", tmp_path)

    with app.test_client() as client:
        with client.session_transaction() as sess:
            sess["autenticado"] = True
            sess["csrf_token"] = "ct"
        resp = client.post("/documentos/7/exportar-json", data={"csrf_token": "ct"})

    assert resp.status_code == 302
    assert tentativas and tentativas[0]["status"] == "sucesso"
    assert tentativas[0]["documento_id"] == 7
    assert tentativas[0]["destino_externo_id"].startswith("exports/json/")


def test_rota_exportar_json_get_rejeitado():
    with app.test_client() as client:
        with client.session_transaction() as sess:
            sess["autenticado"] = True
        resp = client.get("/documentos/7/exportar-json")

    assert resp.status_code == 405

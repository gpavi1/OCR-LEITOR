from copy import deepcopy
from datetime import datetime
from decimal import Decimal
from pathlib import Path
import sys

BASE_DIR = Path(__file__).resolve().parents[1]
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from exportacao.markdown_relatorio import (
    EXPORT_MARKDOWN_DIR_RELATIVO,
    gerar_markdown_documento_revisado,
    gerar_nome_arquivo_markdown,
    montar_relatorio_markdown_documento,
)
from web.app import app

MARKDOWN_PATH = BASE_DIR / "exportacao" / "markdown_relatorio.py"
DOC_PATH = BASE_DIR / "docs" / "exportacao" / "MARKDOWN-OCR-01_RELATORIO_HUMANO.md"
APP_PATH = BASE_DIR / "web" / "app.py"
DETAIL_HTML = BASE_DIR / "web" / "templates" / "documento_detalhe.html"


def documento_exemplo(status="pendente_integracao", revisado=True):
    return {
        "id": 9,
        "cliente_id": 1,
        "arquivo_nome": "nota fiscal ../../cliente.pdf",
        "empresa": "EMPRESA ORIGINAL LTDA",
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


def test_gerador_markdown_existe():
    assert MARKDOWN_PATH.is_file()


def test_documentacao_markdown_existe():
    assert DOC_PATH.is_file()


def test_app_contem_rota_gerar_markdown():
    conteudo = APP_PATH.read_text(encoding="utf-8")
    assert '"/documentos/<int:documento_id>/gerar-markdown"' in conteudo
    assert 'methods=["POST"]' in conteudo


def test_detalhe_contem_acao_manual_markdown():
    conteudo = DETAIL_HTML.read_text(encoding="utf-8")
    assert "/documentos/{{ documento.id }}/gerar-markdown" in conteudo
    assert "Gerar relatório Markdown" in conteudo
    assert "exports/markdown/" in conteudo


def test_gerador_nao_permite_documento_pendente_revisao(tmp_path):
    resultado = gerar_markdown_documento_revisado(
        9,
        obter_documento_fixo(documento_exemplo(status="pendente_revisao")),
        root_dir=tmp_path,
    )

    assert resultado["ok"] is False
    assert resultado["status"] == "erro_validacao"
    assert "Status não permite exportação" in resultado["erro"]


def test_gerador_nao_permite_status_incompletos(tmp_path):
    for status in ["recebido", "processando", "erro_ocr"]:
        resultado = gerar_markdown_documento_revisado(
            9,
            obter_documento_fixo(documento_exemplo(status=status)),
            root_dir=tmp_path,
        )
        assert resultado["ok"] is False
        assert resultado["status"] == "erro_validacao"


def test_gerador_permite_status_pendente_integracao(tmp_path):
    resultado = gerar_markdown_documento_revisado(
        9,
        obter_documento_fixo(documento_exemplo(status="pendente_integracao")),
        root_dir=tmp_path,
    )

    assert resultado["ok"] is True
    assert resultado["status"] == "markdown_gerado_local"


def test_gerador_permite_status_integrado(tmp_path):
    resultado = gerar_markdown_documento_revisado(
        9,
        obter_documento_fixo(documento_exemplo(status="integrado")),
        root_dir=tmp_path,
    )

    assert resultado["ok"] is True
    assert resultado["status"] == "markdown_gerado_local"


def test_gerador_cria_arquivo_md_em_pasta_controlada(tmp_path):
    resultado = gerar_markdown_documento_revisado(
        9,
        obter_documento_fixo(documento_exemplo()),
        root_dir=tmp_path,
        agora=datetime(2026, 6, 28, 16, 45, 30),
    )

    caminho = tmp_path / resultado["caminho_relativo"]
    assert caminho.exists()
    assert caminho.parent.resolve() == (tmp_path / EXPORT_MARKDOWN_DIR_RELATIVO).resolve()
    assert caminho.name == "documento_9_20260628164530.md"


def test_gerador_nao_aceita_caminho_arbitrario_do_usuario(tmp_path):
    documento = documento_exemplo()
    documento["arquivo_nome"] = "..\\..\\segredo.pdf"
    resultado = gerar_markdown_documento_revisado(
        9,
        obter_documento_fixo(documento),
        root_dir=tmp_path,
        agora=datetime(2026, 6, 28, 16, 45, 30),
    )

    assert resultado["ok"] is True
    assert resultado["caminho_relativo"].startswith("exports/markdown/")
    assert "segredo" not in Path(resultado["caminho_relativo"]).name
    assert ".." not in resultado["caminho_relativo"]


def test_gerador_sanitiza_nome_do_arquivo():
    nome = gerar_nome_arquivo_markdown("doc-9../x", agora=datetime(2026, 6, 28, 16, 45, 30))
    assert nome == "documento_9_20260628164530.md"


def test_gerador_usa_json_validado_como_fonte(monkeypatch):
    payload_fake = {
        "origem": "OCR-LEITOR",
        "versao_contrato": "ocr_leitor.documento_fiscal.v1",
        "documento": {
            "empresa": "EMPRESA DO PAYLOAD",
            "numero_nf": "999",
            "chave_acesso": "1" * 44,
            "vencimento": "2026-09-01",
            "valor_total": "250.00",
        },
        "revisao": {
            "revisado": True,
            "revisado_por": "auditor_payload",
            "revisado_em": "2026-06-28T12:00:00",
        },
        "integracao": {
            "status": "pronto_para_destino",
            "destino": "arquivo_local_json",
            "modo": "manual_local",
        },
        "metadados": {
            "arquivo_nome": "arquivo_payload.pdf",
            "json_path": "exports/json/documento_9_20260628120000.json",
            "gerado_em": "2026-06-28T12:05:00",
        },
    }

    monkeypatch.setattr("exportacao.markdown_relatorio.montar_payload_exportacao_documento", lambda _documento: payload_fake)
    markdown, payload = montar_relatorio_markdown_documento(documento_exemplo())

    assert payload == payload_fake
    assert "EMPRESA DO PAYLOAD" in markdown
    assert "auditor_payload" in markdown
    assert "exports/json/documento_9_20260628120000.json" in markdown
    assert "EMPRESA ORIGINAL LTDA" not in markdown


def test_markdown_nao_usa_markdown_como_fonte_oficial():
    markdown, _payload = montar_relatorio_markdown_documento(documento_exemplo())
    assert "apenas para leitura humana e auditoria operacional" in markdown
    assert "A fonte oficial para integração é o JSON estruturado validado" in markdown
    assert "nao substitui o JSON validado oficial" in markdown


def test_markdown_nao_expoe_ocr_bruto_completo_por_padrao():
    markdown, _payload = montar_relatorio_markdown_documento(documento_exemplo())
    assert "texto_extraido" not in markdown
    assert "OCR bruto" not in markdown


def test_gerador_nao_cria_api():
    conteudo = MARKDOWN_PATH.read_text(encoding="utf-8")
    assert "@app.route" not in conteudo
    assert "/api" not in conteudo
    assert "Blueprint" not in conteudo


def test_gerador_nao_integra_plataformas_externas():
    conteudo = MARKDOWN_PATH.read_text(encoding="utf-8")
    assert "Monday" not in conteudo and "monday" not in conteudo
    assert "Sheets" not in conteudo and "sheets" not in conteudo
    assert "ERP" not in conteudo and "erp" not in conteudo
    assert "FechaMes" not in conteudo and "fechames" not in conteudo


def test_gerador_nao_altera_ocr_parser_pipeline_banco_ou_requirements():
    conteudo = MARKDOWN_PATH.read_text(encoding="utf-8")
    assert "ocr_pipeline_s1" not in conteudo
    assert "parser_nf" not in conteudo
    assert "pytesseract" not in conteudo
    assert "INSERT INTO" not in conteudo
    assert "UPDATE " not in conteudo
    assert "requirements.txt" not in conteudo


def test_gerador_falha_de_forma_segura_quando_documento_nao_existe(tmp_path):
    resultado = gerar_markdown_documento_revisado(
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


def test_gerador_falha_de_forma_segura_quando_payload_nao_e_valido(tmp_path):
    documento = documento_exemplo()
    documento["empresa"] = ""
    resultado = gerar_markdown_documento_revisado(
        9,
        obter_documento_fixo(documento),
        root_dir=tmp_path,
    )

    assert resultado["ok"] is False
    assert resultado["status"] == "erro_validacao"
    assert "documento.empresa" in resultado["erro"]


def test_rota_markdown_post_retorna_redirect_e_registra_tentativa(tmp_path, monkeypatch):
    tentativas = []

    def fake_fetch_one(_query, _params):
        return documento_exemplo()

    def fake_registrar(**kwargs):
        tentativas.append(kwargs)
        return 1

    monkeypatch.setattr("web.app.fetch_one", fake_fetch_one)
    monkeypatch.setattr("web.app._obter_integracao_manual", lambda _cliente_id: 88)
    monkeypatch.setattr("web.app._registrar_tentativa_integracao", fake_registrar)
    monkeypatch.setattr("web.app.ROOT_DIR", tmp_path)

    with app.test_client() as client:
        with client.session_transaction() as sess:
            sess["autenticado"] = True
        resp = client.post("/documentos/9/gerar-markdown")

    assert resp.status_code == 302
    assert tentativas and tentativas[0]["status"] == "sucesso"
    assert tentativas[0]["documento_id"] == 9
    assert tentativas[0]["destino_externo_id"].startswith("exports/markdown/")


def test_rota_markdown_get_rejeitado():
    with app.test_client() as client:
        with client.session_transaction() as sess:
            sess["autenticado"] = True
        resp = client.get("/documentos/9/gerar-markdown")

    assert resp.status_code == 405

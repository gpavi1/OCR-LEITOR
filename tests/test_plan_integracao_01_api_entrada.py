from pathlib import Path


BASE_DIR = Path(__file__).resolve().parents[1]
ADR_PATH = BASE_DIR / "docs" / "integracao" / "ADR-PLAN-INTEGRACAO-01-api-entrada.md"


def ler_adr():
    return ADR_PATH.read_text(encoding="utf-8")


def test_adr_plan_integracao_01_existe():
    assert ADR_PATH.is_file()


def test_adr_define_export_antes_de_api():
    conteudo = ler_adr()
    assert "EXPORT-OCR-01" in conteudo
    assert "API-IN-01" in conteudo
    assert "EXPORT-OCR-01` vem antes de `API-IN-01" in conteudo


def test_adr_define_api_local_controlada():
    conteudo = ler_adr().lower()
    assert "primeira api sera local e controlada" in conteudo


def test_adr_proibe_api_publica_inicial():
    conteudo = ler_adr().lower()
    assert "nao podera ser uma api publica" in conteudo


def test_adr_define_bearer_token():
    conteudo = ler_adr()
    assert "Bearer Token" in conteudo
    assert "variavel de ambiente" in conteudo


def test_adr_define_multipart_form_data():
    conteudo = ler_adr()
    assert "multipart/form-data" in conteudo


def test_adr_proibe_url_base64_e_caminho_arbitrario():
    conteudo = ler_adr().lower()
    assert "json com url esta proibido na primeira versao" in conteudo
    assert "base64 esta proibido na primeira versao" in conteudo
    assert "caminho arbitrario" in conteudo
    assert "permanentemente proibido" in conteudo


def test_adr_proibe_processamento_automatico():
    conteudo = ler_adr().lower()
    assert "apenas salvara o arquivo em `input/`" in conteudo
    assert "nao disparara ocr automaticamente" in conteudo


def test_adr_proibe_alteracao_de_banco():
    conteudo = ler_adr().lower()
    assert "nao escrevera diretamente no banco" in conteudo
    assert "nenhum schema de banco sera alterado agora" in conteudo


def test_adr_mantem_fechames_separado():
    conteudo = ler_adr()
    assert "FechaMes" in conteudo
    assert "nao integrara Monday, Sheets, ERP ou FechaMes" in conteudo


def test_adr_define_resposta_202():
    conteudo = ler_adr()
    assert "HTTP 202 Accepted" in conteudo


def test_adr_define_limite_extensoes_logs_e_idempotencia():
    conteudo = ler_adr()
    assert "10 MB" in conteudo
    assert ".jpg" in conteudo
    assert ".jpeg" in conteudo
    assert ".png" in conteudo
    assert "Logs nao podem conter token" in conteudo
    assert "Logs nao podem conter conteudo OCR sensivel" in conteudo
    assert "Logs nao podem conter dados completos do documento" in conteudo
    assert "SHA-256" in conteudo
    assert "X-Idempotency-Key" in conteudo


def test_adr_define_markdown_como_relatorio_humano():
    conteudo = ler_adr().lower()
    assert "markdown sera um relatorio humano futuro" in conteudo
    assert "nao a fonte oficial de integracao" in conteudo


def test_adr_define_json_como_fonte_oficial():
    conteudo = ler_adr().lower()
    assert "json estruturado continuara sendo a fonte oficial para integracao" in conteudo


def test_adr_define_pdf_somente_depois_de_fase_especifica():
    conteudo = ler_adr().lower()
    assert "pdf" in conteudo
    assert "so podera entrar depois de fase especifica do pipeline" in conteudo


def test_adr_registra_que_nao_ha_implementacao_nesta_fase():
    conteudo = ler_adr().lower()
    assert "nenhuma rota `/api` sera criada agora" in conteudo
    assert "nenhum endpoint flask sera criado agora" in conteudo
    assert "nenhum blueprint sera criado agora" in conteudo

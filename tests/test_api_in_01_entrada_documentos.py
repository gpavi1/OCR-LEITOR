from io import BytesIO
from pathlib import Path
import hashlib
import sys

BASE_DIR = Path(__file__).resolve().parents[1]
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from web.app import (
    TAMANHO_MAXIMO_UPLOAD,
    app,
    extensao_permitida_api_entrada,
)

APP_PATH = BASE_DIR / "web" / "app.py"
DOC_PATH = BASE_DIR / "docs" / "integracao" / "API-IN-01_ENTRADA_DOCUMENTOS.md"
API_PATH = "/api/v1/documentos/entrada"
TOKEN = "token-seguro-de-teste"


def trecho_rota_api():
    conteudo = APP_PATH.read_text(encoding="utf-8")
    inicio = conteudo.index('@app.route("/api/v1/documentos/entrada"')
    fim = conteudo.index('@app.route("/health")', inicio)
    return conteudo[inicio:fim]


def post_arquivo(client, nome="nota.jpg", conteudo=b"imagem", token=TOKEN, headers=None):
    req_headers = {"Authorization": f"Bearer {token}"}
    if headers:
        req_headers.update(headers)

    return client.post(
        API_PATH,
        data={"documento": (BytesIO(conteudo), nome)},
        content_type="multipart/form-data",
        headers=req_headers,
    )


def test_endpoint_existe_apenas_para_post(monkeypatch, tmp_path):
    monkeypatch.setenv("OCR_API_TOKEN", TOKEN)
    monkeypatch.setattr("web.app.ROOT_DIR", tmp_path)
    with app.test_client() as client:
        get_resp = client.get(API_PATH, headers={"Authorization": f"Bearer {TOKEN}"})
        post_resp = post_arquivo(client)

    assert get_resp.status_code == 405
    assert post_resp.status_code == 202


def test_requisicao_sem_authorization_retorna_401(monkeypatch):
    monkeypatch.setenv("OCR_API_TOKEN", TOKEN)
    with app.test_client() as client:
        resp = client.post(API_PATH)

    assert resp.status_code == 401
    assert resp.get_json()["status"] == "nao_autorizado"


def test_requisicao_com_token_invalido_retorna_401(monkeypatch):
    monkeypatch.setenv("OCR_API_TOKEN", TOKEN)
    with app.test_client() as client:
        resp = post_arquivo(client, token="token-invalido")

    assert resp.status_code == 401
    assert "token-invalido" not in resp.get_data(as_text=True)


def test_ocr_api_token_ausente_falha_de_forma_segura(monkeypatch):
    monkeypatch.delenv("OCR_API_TOKEN", raising=False)
    with app.test_client() as client:
        resp = post_arquivo(client)

    assert resp.status_code == 401
    assert resp.get_json()["status"] == "token_nao_configurado"
    assert TOKEN not in resp.get_data(as_text=True)


def test_requisicao_sem_multipart_retorna_400(monkeypatch):
    monkeypatch.setenv("OCR_API_TOKEN", TOKEN)
    with app.test_client() as client:
        resp = client.post(
            API_PATH,
            data=b"conteudo",
            content_type="application/octet-stream",
            headers={"Authorization": f"Bearer {TOKEN}"},
        )

    assert resp.status_code == 400
    assert resp.get_json()["status"] == "payload_invalido"


def test_requisicao_sem_campo_documento_retorna_400(monkeypatch):
    monkeypatch.setenv("OCR_API_TOKEN", TOKEN)
    with app.test_client() as client:
        resp = client.post(
            API_PATH,
            data={"outro": "valor"},
            content_type="multipart/form-data",
            headers={"Authorization": f"Bearer {TOKEN}"},
        )

    assert resp.status_code == 400
    assert resp.get_json()["status"] == "documento_ausente"


def test_arquivo_jpg_valido_retorna_202(monkeypatch, tmp_path):
    monkeypatch.setenv("OCR_API_TOKEN", TOKEN)
    monkeypatch.setattr("web.app.ROOT_DIR", tmp_path)
    with app.test_client() as client:
        resp = post_arquivo(client, nome="nota.jpg", conteudo=b"jpg")

    assert resp.status_code == 202
    assert resp.get_json()["arquivo_nome"].endswith(".jpg")


def test_arquivo_jpeg_valido_retorna_202(monkeypatch, tmp_path):
    monkeypatch.setenv("OCR_API_TOKEN", TOKEN)
    monkeypatch.setattr("web.app.ROOT_DIR", tmp_path)
    with app.test_client() as client:
        resp = post_arquivo(client, nome="nota.jpeg", conteudo=b"jpeg")

    assert resp.status_code == 202
    assert resp.get_json()["arquivo_nome"].endswith(".jpeg")


def test_arquivo_png_valido_retorna_202(monkeypatch, tmp_path):
    monkeypatch.setenv("OCR_API_TOKEN", TOKEN)
    monkeypatch.setattr("web.app.ROOT_DIR", tmp_path)
    with app.test_client() as client:
        resp = post_arquivo(client, nome="nota.png", conteudo=b"png")

    assert resp.status_code == 202
    assert resp.get_json()["arquivo_nome"].endswith(".png")


def test_arquivo_pdf_rejeitado_nesta_fase(monkeypatch):
    monkeypatch.setenv("OCR_API_TOKEN", TOKEN)
    with app.test_client() as client:
        resp = post_arquivo(client, nome="nota.pdf")

    assert resp.status_code == 415
    assert extensao_permitida_api_entrada("nota.pdf") is False


def test_arquivo_exe_rejeitado(monkeypatch):
    monkeypatch.setenv("OCR_API_TOKEN", TOKEN)
    with app.test_client() as client:
        resp = post_arquivo(client, nome="virus.exe")

    assert resp.status_code == 415


def test_arquivo_acima_de_10mb_rejeitado(monkeypatch):
    monkeypatch.setenv("OCR_API_TOKEN", TOKEN)
    conteudo = b"0" * (TAMANHO_MAXIMO_UPLOAD + 1)
    with app.test_client() as client:
        resp = post_arquivo(client, nome="grande.jpg", conteudo=conteudo)

    assert resp.status_code == 413
    assert resp.get_json()["status"] == "arquivo_muito_grande"


def test_nome_do_arquivo_e_sanitizado(monkeypatch, tmp_path):
    monkeypatch.setenv("OCR_API_TOKEN", TOKEN)
    monkeypatch.setattr("web.app.ROOT_DIR", tmp_path)
    with app.test_client() as client:
        resp = post_arquivo(client, nome="nota fiscal @@@.jpg")

    nome = resp.get_json()["arquivo_nome"]
    assert resp.status_code == 202
    assert " " not in nome
    assert "@" not in nome
    assert nome.endswith(".jpg")


def test_path_traversal_e_bloqueado(monkeypatch, tmp_path):
    monkeypatch.setenv("OCR_API_TOKEN", TOKEN)
    monkeypatch.setattr("web.app.ROOT_DIR", tmp_path)
    with app.test_client() as client:
        resp = post_arquivo(client, nome="../../segredo.jpg")

    nome = resp.get_json()["arquivo_nome"]
    assert resp.status_code == 202
    assert "/" not in nome
    assert "\\" not in nome
    assert ".." not in nome
    assert (tmp_path / "input" / nome).is_file()


def test_resposta_contem_processamento_automatico_false(monkeypatch, tmp_path):
    monkeypatch.setenv("OCR_API_TOKEN", TOKEN)
    monkeypatch.setattr("web.app.ROOT_DIR", tmp_path)
    with app.test_client() as client:
        resp = post_arquivo(client)

    assert resp.get_json()["processamento_automatico"] is False


def test_resposta_contem_fluxo_aguardando_processamento_manual(monkeypatch, tmp_path):
    monkeypatch.setenv("OCR_API_TOKEN", TOKEN)
    monkeypatch.setattr("web.app.ROOT_DIR", tmp_path)
    with app.test_client() as client:
        resp = post_arquivo(client)

    assert resp.get_json()["fluxo"] == "aguardando_processamento_manual"
    assert resp.get_json()["proxima_acao"] == "processar_manual_pelo_painel"


def test_resposta_contem_hash_sha256(monkeypatch, tmp_path):
    monkeypatch.setenv("OCR_API_TOKEN", TOKEN)
    monkeypatch.setattr("web.app.ROOT_DIR", tmp_path)
    conteudo = b"conteudo-controlado"
    with app.test_client() as client:
        resp = post_arquivo(client, conteudo=conteudo)

    assert resp.get_json()["hash_sha256"] == hashlib.sha256(conteudo).hexdigest()


def test_arquivo_e_salvo_apenas_em_input(monkeypatch, tmp_path):
    monkeypatch.setenv("OCR_API_TOKEN", TOKEN)
    monkeypatch.setattr("web.app.ROOT_DIR", tmp_path)
    with app.test_client() as client:
        resp = post_arquivo(client)

    nome = resp.get_json()["arquivo_nome"]
    assert (tmp_path / "input" / nome).is_file()
    assert not (tmp_path / "exports" / "json").exists()
    assert not (tmp_path / "exports" / "markdown").exists()


def test_api_nao_chama_ocr_parser_ou_pipeline():
    trecho = trecho_rota_api()
    assert "ocr_pipeline_s1" not in trecho
    assert "processar_input" not in trecho
    assert "parser_nf" not in trecho
    assert "pytesseract" not in trecho


def test_api_nao_cria_json_exportado():
    trecho = trecho_rota_api()
    assert "exportar_documento_revisado" not in trecho
    assert "exports/json" not in trecho


def test_api_nao_cria_markdown():
    trecho = trecho_rota_api()
    assert "gerar_markdown" not in trecho
    assert "exports/markdown" not in trecho


def test_api_nao_altera_banco_ou_schema():
    trecho = trecho_rota_api()
    assert "INSERT INTO" not in trecho
    assert "UPDATE " not in trecho
    assert "ALTER TABLE" not in trecho
    assert "DROP TABLE" not in trecho


def test_api_nao_exige_dependencia_nova():
    trecho = trecho_rota_api()
    assert "requests" not in trecho
    assert "pandas" not in trecho
    assert "numpy" not in trecho


def test_api_nao_integra_plataformas_externas():
    trecho = trecho_rota_api()
    assert "Monday" not in trecho and "monday" not in trecho
    assert "Sheets" not in trecho and "sheets" not in trecho
    assert "ERP" not in trecho and "erp" not in trecho
    assert "FechaMes" not in trecho and "fechames" not in trecho


def test_token_nao_aparece_na_resposta(monkeypatch, tmp_path):
    monkeypatch.setenv("OCR_API_TOKEN", TOKEN)
    monkeypatch.setattr("web.app.ROOT_DIR", tmp_path)
    with app.test_client() as client:
        resp = post_arquivo(client)

    assert TOKEN not in resp.get_data(as_text=True)


def test_x_idempotency_key_opcional_nao_bloqueia_upload(monkeypatch, tmp_path):
    monkeypatch.setenv("OCR_API_TOKEN", TOKEN)
    monkeypatch.setattr("web.app.ROOT_DIR", tmp_path)
    with app.test_client() as client:
        resp = post_arquivo(client, headers={"X-Idempotency-Key": "pedido-123"})

    assert resp.status_code == 202
    assert "hash_sha256" in resp.get_json()

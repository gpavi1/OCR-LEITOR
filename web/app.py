from pathlib import Path
import json
import os
import hmac
import hashlib
import csv
import sys
import uuid
import datetime
import time
import secrets
from datetime import timedelta
from io import StringIO
from decimal import Decimal, InvalidOperation

from flask import Flask, Response, abort, flash, redirect, render_template, request, session, url_for

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from database.mysql_db import fetch_all, fetch_one, execute
from exportacao.json_validado import exportar_documento_revisado
from exportacao.markdown_relatorio import gerar_markdown_documento_revisado
from conectores.monday_dryrun import gerar_dryrun_monday
from conectores.monday_envio import enviar_documento_monday


app = Flask(__name__)


def _carregar_web_secret_key():
    valor = os.getenv("WEB_SECRET_KEY", "").strip()
    if valor:
        return valor
    return secrets.token_hex(32)


app.secret_key = _carregar_web_secret_key()

app.permanent_session_lifetime = timedelta(minutes=30)
app.config["SESSION_COOKIE_HTTPONLY"] = True
app.config["SESSION_COOKIE_SAMESITE"] = "Lax"
app.config["SESSION_COOKIE_SECURE"] = os.getenv("WEB_SESSION_COOKIE_SECURE", "").strip().lower() in ("1", "true", "sim", "yes")


_LOGIN_RATE_LIMIT = {}


def _obter_max_tentativas():
    return int(os.getenv("WEB_LOGIN_MAX_TENTATIVAS", "3"))


def _obter_bloqueio_segundos():
    return int(os.getenv("WEB_LOGIN_BLOQUEIO_SEGUNDOS", "30"))


def _verificar_rate_limit_login(ip, username):
    chave = (ip, username)
    if chave not in _LOGIN_RATE_LIMIT:
        return True
    tentativas, inicio = _LOGIN_RATE_LIMIT[chave]
    if tentativas >= _obter_max_tentativas():
        if time.time() - inicio < _obter_bloqueio_segundos():
            return False
        _LOGIN_RATE_LIMIT.pop(chave, None)
    return True


def _registrar_tentativa_login(ip, username):
    chave = (ip, username)
    agora = time.time()
    if chave in _LOGIN_RATE_LIMIT:
        tentativas, inicio = _LOGIN_RATE_LIMIT[chave]
        _LOGIN_RATE_LIMIT[chave] = (tentativas + 1, inicio)
    else:
        _LOGIN_RATE_LIMIT[chave] = (1, agora)


def _limpar_rate_limit_login(ip, username):
    chave = (ip, username)
    _LOGIN_RATE_LIMIT.pop(chave, None)

EXTENSOES_PERMITIDAS_UPLOAD = {".jpg", ".jpeg", ".png", ".pdf"}
EXTENSOES_PERMITIDAS_API_ENTRADA = {".jpg", ".jpeg", ".png"}
TAMANHO_MAXIMO_UPLOAD = 10 * 1024 * 1024

STATUS_LABEL = {
    "recebido": "Recebido",
    "processando": "Processando",
    "pendente_revisao": "Precisa revisão",
    "pendente_integracao": "Aguardando integração",
    "integrado": "Integrado",
    "falha_integracao": "Falha na integração",
    "dry_run_apto": "Monday Dry-run: apto",
    "dry_run_bloqueado": "Monday Dry-run: bloqueado",
    "dry_run_erro": "Monday Dry-run: erro",
    "monday_envio_sucesso": "Monday Envio Real: sucesso",
    "monday_envio_falha": "Monday Envio Real: falha",
    "monday_envio_bloqueado": "Monday Envio Real: bloqueado",
    "erro_ocr": "Erro OCR — revisar",
}

STATUS_PRECISA_REVISAO = {"pendente_revisao", "erro_ocr"}


def status_label(status):
    return STATUS_LABEL.get(status, status.replace("_", " ").title())


def campo_pendente(valor):
    if valor is None:
        return True

    return not str(valor).strip()


@app.context_processor
def inject_globals():
    return dict(
        status_label=status_label,
        precisa_revisao=STATUS_PRECISA_REVISAO,
        campo_pendente=campo_pendente,
    )


def extensao_permitida_upload(nome_arquivo):
    nome = Path(nome_arquivo).name
    ext = Path(nome).suffix.lower()
    return ext in EXTENSOES_PERMITIDAS_UPLOAD


def extensao_permitida_api_entrada(nome_arquivo):
    nome = Path(nome_arquivo).name
    ext = Path(nome).suffix.lower()
    return ext in EXTENSOES_PERMITIDAS_API_ENTRADA


def gerar_nome_upload_seguro(nome_original):
    nome = Path(nome_original).name
    ext = Path(nome).suffix.lower()
    base = Path(nome).stem
    base = "".join(c for c in base if c.isalnum() or c in ("-", "_")).strip()
    if not base:
        base = "documento"
    timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    uuid_part = str(uuid.uuid4())[:8]
    return f"{base}_{timestamp}_{uuid_part}{ext}"


def resolver_pasta_input():
    pasta = ROOT_DIR / "input"
    pasta.mkdir(parents=True, exist_ok=True)
    return pasta


def _resposta_api_erro(status_http, codigo, mensagem):
    return {
        "ok": False,
        "status": codigo,
        "erro": mensagem,
        "processamento_automatico": False,
    }, status_http


def _validar_bearer_api_entrada():
    token_esperado = os.getenv("OCR_API_TOKEN")
    if not token_esperado:
        return False, _resposta_api_erro(
            401,
            "token_nao_configurado",
            "API de entrada não configurada.",
        )

    authorization = request.headers.get("Authorization", "")
    if not authorization.startswith("Bearer "):
        return False, _resposta_api_erro(
            401,
            "nao_autorizado",
            "Authorization Bearer é obrigatório.",
        )

    token_recebido = authorization[len("Bearer "):]
    if not hmac.compare_digest(token_recebido, token_esperado):
        return False, _resposta_api_erro(
            401,
            "nao_autorizado",
            "Token inválido.",
        )

    return True, None


def _web_credentials():
    return (
        os.getenv("WEB_USERNAME", "admin"),
        os.getenv("WEB_PASSWORD", "admin")
    )



def _valor_decimal_br(valor):
    if valor is None:
        return None

    texto_valor = str(valor).strip()
    if not texto_valor:
        return None

    texto_valor = texto_valor.replace("R$", "").replace(" ", "")

    if "," in texto_valor:
        texto_valor = texto_valor.replace(".", "").replace(",", ".")

    try:
        return Decimal(texto_valor)
    except InvalidOperation:
        return None


def _obter_integracao_monday_envio(cliente_id):
    integracao = fetch_one("""
        SELECT id
        FROM integracoes
        WHERE cliente_id = %s
          AND tipo = 'monday'
          AND ativo = TRUE
        LIMIT 1
    """, (cliente_id,))
    if integracao:
        return integracao["id"]
    return execute("""
        INSERT INTO integracoes (
            cliente_id, tipo, nome, ativo, config_json
        )
        VALUES (
            %s, 'monday', 'Monday Envio Real Local', TRUE,
            JSON_OBJECT('envio_real', TRUE, 'anexo', FALSE)
        )
    """, (cliente_id,))


def _config_monday_envio():
    token = os.getenv("MONDAY_API_TOKEN", "")
    board_id = os.getenv("MONDAY_BOARD_ID", "")
    mapa_colunas = {}
    col_mapping = {
        "empresa": "MONDAY_COLUMN_EMPRESA",
        "numero_nf": "MONDAY_COLUMN_NUMERO_NF",
        "chave_acesso": "MONDAY_COLUMN_CHAVE_ACESSO",
        "vencimento": "MONDAY_COLUMN_VENCIMENTO",
        "valor_total": "MONDAY_COLUMN_VALOR_TOTAL",
        "observacao_revisao": "MONDAY_COLUMN_OBSERVACAO",
    }
    for campo, env_var in col_mapping.items():
        valor = os.getenv(env_var, "")
        if valor:
            mapa_colunas[campo] = valor
    return token, board_id, mapa_colunas


def _validar_duplicidade_monday(documento_id):
    existente = fetch_one("""
        SELECT id
        FROM integracao_tentativas
        WHERE documento_id = %s
          AND status = 'monday_envio_sucesso'
          AND destino_externo_id IS NOT NULL
        LIMIT 1
    """, (documento_id,))
    return existente is not None


def _texto_ou_none(valor):
    if valor is None:
        return None

    valor = str(valor).strip()
    return valor or None


@app.before_request
def exigir_login():
    if request.path.startswith("/api/"):
        return None

    rotas_livres = {"login", "static", "health", "api_entrada_documentos"}
    if request.endpoint in rotas_livres:
        return None

    if not session.get("autenticado"):
        return redirect(url_for("login"))

    return None


@app.route("/login", methods=["GET", "POST"])
def login():
    erro = None

    if request.method == "POST":
        username = request.form.get("username", "")
        password = request.form.get("password", "")

        ip = request.remote_addr or "127.0.0.1"

        if not _verificar_rate_limit_login(ip, username):
            erro = "Muitas tentativas. Aguarde alguns segundos."

        else:
            expected_user, expected_password = _web_credentials()

            usuario_ok = hmac.compare_digest(username, expected_user)
            senha_ok = hmac.compare_digest(password, expected_password)

            if usuario_ok and senha_ok:
                session.permanent = True
                session["autenticado"] = True
                session["usuario"] = username
                _limpar_rate_limit_login(ip, username)
                return redirect(url_for("index"))

            _registrar_tentativa_login(ip, username)
            erro = "Usuário ou senha inválidos."

    return render_template("login.html", erro=erro)


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))



def _obter_integracao_manual(cliente_id):
    integracao = fetch_one("""
        SELECT id
        FROM integracoes
        WHERE cliente_id = %s
          AND tipo = 'manual'
          AND nome = 'Operacao Manual Local'
        LIMIT 1
    """, (cliente_id,))

    if integracao:
        return integracao["id"]

    return execute("""
        INSERT INTO integracoes (
            cliente_id,
            tipo,
            nome,
            ativo,
            config_json
        )
        VALUES (
            %s,
            'manual',
            'Operacao Manual Local',
            TRUE,
            JSON_OBJECT()
        )
    """, (cliente_id,))


def _obter_integracao_dryrun(cliente_id):
    integracao = fetch_one("""
        SELECT id
        FROM integracoes
        WHERE cliente_id = %s
          AND tipo = 'monday_dryrun'
          AND ativo = TRUE
        LIMIT 1
    """, (cliente_id,))

    if integracao:
        return integracao["id"]

    return execute("""
        INSERT INTO integracoes (
            cliente_id,
            tipo,
            nome,
            ativo,
            config_json
        )
        VALUES (
            %s,
            'monday_dryrun',
            'Monday Dry-run Local',
            TRUE,
            JSON_OBJECT('envio_real', FALSE)
        )
    """, (cliente_id,))


def _registrar_tentativa_integracao(
    documento_id,
    integracao_id,
    status,
    destino_externo_id=None,
    erro=None,
    resposta_resumida=None
):
    return execute("""
        INSERT INTO integracao_tentativas (
            documento_id,
            integracao_id,
            status,
            destino_externo_id,
            erro,
            resposta_resumida
        )
        VALUES (%s, %s, %s, %s, %s, %s)
    """, (
        documento_id,
        integracao_id,
        status,
        destino_externo_id,
        erro,
        resposta_resumida
    ))



@app.route("/integracoes/documentos/<int:documento_id>/reenfileirar", methods=["POST"])
def reenfileirar_documento_integracao(documento_id):
    documento = fetch_one("""
        SELECT id, cliente_id, status
        FROM documentos
        WHERE id = %s
    """, (documento_id,))

    if not documento:
        flash("Documento não encontrado.", "error")
        return redirect(url_for("historico_integracoes"))

    if documento["status"] == "pendente_integracao":
        flash("Documento já está na fila de integração.", "warning")
        return redirect(url_for("integracoes"))

    integracao_id = _obter_integracao_manual(documento["cliente_id"])

    execute("""
        UPDATE documentos
        SET status = 'pendente_integracao',
            atualizado_em = NOW()
        WHERE id = %s
    """, (documento_id,))

    _registrar_tentativa_integracao(
        documento["id"],
        integracao_id,
        "reenfileirado",
        destino_externo_id=f"manual-reenfileirado-{documento_id}",
        resposta_resumida="Documento reenfileirado manualmente."
    )

    flash("Documento reenfileirado para integração.", "success")
    return redirect(url_for("integracoes"))


@app.route("/upload", methods=["GET", "POST"])
def upload_documento():
    if request.method == "GET":
        return render_template("upload_documento.html")

    if "documento" not in request.files:
        flash("Nenhum arquivo enviado.", "error")
        return redirect(url_for("upload_documento"))

    arquivo = request.files["documento"]

    if not arquivo.filename or arquivo.filename.strip() == "":
        flash("Nome do arquivo vazio.", "error")
        return redirect(url_for("upload_documento"))

    if not extensao_permitida_upload(arquivo.filename):
        flash("Extensão não permitida. Use .jpg, .jpeg, .png ou .pdf.", "error")
        return redirect(url_for("upload_documento"))

    dados = arquivo.read()

    if len(dados) > TAMANHO_MAXIMO_UPLOAD:
        flash("Arquivo excede o limite de 10 MB.", "error")
        return redirect(url_for("upload_documento"))

    nome_seguro = gerar_nome_upload_seguro(arquivo.filename)
    pasta_input = resolver_pasta_input()
    caminho = pasta_input / nome_seguro
    caminho.write_bytes(dados)

    flash(f"Documento enviado com sucesso: {nome_seguro}", "success")
    return redirect(url_for("upload_documento"))


@app.route("/upload/processar", methods=["POST"])
def processar_upload():
    from ocr_pipeline_s1 import INPUT_FOLDER, processar_input

    pasta = Path(INPUT_FOLDER)
    if not pasta.exists():
        flash("Pasta input/ não encontrada.", "error")
        return redirect(url_for("upload_documento"))

    arquivos = [p for p in pasta.iterdir() if p.is_file()]
    if not arquivos:
        flash("Nenhum arquivo para processar em input/.", "warning")
        return redirect(url_for("upload_documento"))

    try:
        processar_input(cliente_id=1, mover=True)
        flash(f"Processamento concluído. Verifique a lista de documentos.", "success")
    except Exception as exc:
        flash(f"Erro durante o processamento: {exc}", "error")

    return redirect(url_for("upload_documento"))


@app.route("/api/v1/documentos/entrada", methods=["POST"])
def api_entrada_documentos():
    autorizado, resposta = _validar_bearer_api_entrada()
    if not autorizado:
        return resposta

    content_type = request.content_type or ""
    if not content_type.lower().startswith("multipart/form-data"):
        return _resposta_api_erro(
            400,
            "payload_invalido",
            "A requisição deve usar multipart/form-data.",
        )

    if "documento" not in request.files:
        return _resposta_api_erro(
            400,
            "documento_ausente",
            "Campo documento é obrigatório.",
        )

    arquivo = request.files["documento"]
    if not arquivo.filename or arquivo.filename.strip() == "":
        return _resposta_api_erro(
            400,
            "nome_arquivo_ausente",
            "Nome do arquivo é obrigatório.",
        )

    if not extensao_permitida_api_entrada(arquivo.filename):
        return _resposta_api_erro(
            415,
            "extensao_nao_permitida",
            "Extensão não permitida nesta API. Use .jpg, .jpeg ou .png.",
        )

    dados = arquivo.read()
    if len(dados) > TAMANHO_MAXIMO_UPLOAD:
        return _resposta_api_erro(
            413,
            "arquivo_muito_grande",
            "Arquivo excede o limite de 10 MB.",
        )

    hash_sha256 = hashlib.sha256(dados).hexdigest()
    nome_seguro = gerar_nome_upload_seguro(arquivo.filename)
    caminho = resolver_pasta_input() / nome_seguro
    caminho.write_bytes(dados)

    return {
        "ok": True,
        "status": "recebido",
        "fluxo": "aguardando_processamento_manual",
        "processamento_automatico": False,
        "arquivo_nome": nome_seguro,
        "hash_sha256": hash_sha256,
        "proxima_acao": "processar_manual_pelo_painel",
    }, 202


@app.route("/health")
def health():
    return {
        "status": "ok",
        "app": "OCR-LEITOR WEB",
        "modo": "local-readonly"
    }


@app.route("/")
def index():
    documentos = fetch_all("""
        SELECT
            id,
            cliente_id,
            arquivo_nome,
            empresa,
            numero_nf,
            chave_acesso,
            vencimento,
            valor_total,
            status,
            revisado,
            criado_em
        FROM documentos
        ORDER BY id DESC
        LIMIT 100
    """)

    resumo = fetch_one("""
        SELECT
            COUNT(*) AS total,
            SUM(CASE WHEN status = 'pendente_integracao' THEN 1 ELSE 0 END) AS pendente_integracao,
            SUM(CASE WHEN status = 'pendente_revisao' THEN 1 ELSE 0 END) AS pendente_revisao,
            SUM(CASE WHEN status LIKE 'erro%' THEN 1 ELSE 0 END) AS erros,
            SUM(CASE WHEN revisado = TRUE THEN 1 ELSE 0 END) AS revisados
        FROM documentos
    """)

    return render_template(
        "documentos.html",
        documentos=documentos,
        resumo=resumo
    )





@app.route("/integracoes/dashboard")
def dashboard_integracoes():
    resumo_documentos = fetch_one("""
        SELECT
            COUNT(*) AS total_documentos,
            SUM(CASE WHEN status = 'pendente_integracao' THEN 1 ELSE 0 END) AS pendentes,
            SUM(CASE WHEN status = 'integrado' THEN 1 ELSE 0 END) AS integrados,
            SUM(CASE WHEN status = 'falha_integracao' THEN 1 ELSE 0 END) AS falhas
        FROM documentos
    """)

    resumo_tentativas = fetch_one("""
        SELECT
            COUNT(*) AS total_tentativas,
            SUM(CASE WHEN status = 'sucesso' THEN 1 ELSE 0 END) AS sucessos,
            SUM(CASE WHEN status = 'falha' THEN 1 ELSE 0 END) AS tentativas_falha,
            SUM(CASE WHEN status = 'reenfileirado' THEN 1 ELSE 0 END) AS reenfileirados
        FROM integracao_tentativas
    """)

    ultimas_tentativas = fetch_all("""
        SELECT
            t.id,
            t.documento_id,
            d.arquivo_nome,
            d.empresa,
            d.numero_nf,
            t.status,
            t.destino_externo_id,
            t.erro,
            t.resposta_resumida,
            t.criado_em
        FROM integracao_tentativas t
        LEFT JOIN documentos d ON d.id = t.documento_id
        ORDER BY t.criado_em DESC, t.id DESC
        LIMIT 8
    """)

    ultimas_falhas = fetch_all("""
        SELECT
            t.id,
            t.documento_id,
            d.empresa,
            d.numero_nf,
            t.erro,
            t.criado_em
        FROM integracao_tentativas t
        LEFT JOIN documentos d ON d.id = t.documento_id
        WHERE t.status = 'falha'
        ORDER BY t.criado_em DESC, t.id DESC
        LIMIT 5
    """)

    return render_template(
        "dashboard_integracoes.html",
        resumo_documentos=resumo_documentos or {},
        resumo_tentativas=resumo_tentativas or {},
        ultimas_tentativas=ultimas_tentativas,
        ultimas_falhas=ultimas_falhas
    )


@app.route("/integracoes")
def integracoes():
    documentos = fetch_all("""
        SELECT
            id,
            empresa,
            numero_nf,
            chave_acesso,
            vencimento,
            valor_total,
            revisado,
            revisado_por,
            revisado_em,
            status
        FROM documentos
        WHERE status = 'pendente_integracao'
        ORDER BY revisado_em DESC, id DESC
        LIMIT 100
    """)

    return render_template(
        "integracoes.html",
        documentos=documentos
    )



@app.route("/integracoes/historico")
def historico_integracoes():
    tentativas = fetch_all("""
        SELECT
            t.id,
            t.documento_id,
            d.arquivo_nome,
            d.empresa,
            d.numero_nf,
            t.integracao_id,
            i.nome AS integracao_nome,
            i.tipo AS integracao_tipo,
            t.status,
            t.destino_externo_id,
            t.erro,
            t.resposta_resumida,
            t.criado_em,
            d.status AS status_atual
        FROM integracao_tentativas t
        LEFT JOIN documentos d ON d.id = t.documento_id
        LEFT JOIN integracoes i ON i.id = t.integracao_id
        ORDER BY t.criado_em DESC, t.id DESC
        LIMIT 100
    """)

    return render_template(
        "historico_integracoes.html",
        tentativas=tentativas
    )



@app.route("/exportar/documentos/<int:documento_id>.csv")
def exportar_documento_csv(documento_id):
    documento = fetch_one("""
        SELECT
            id,
            cliente_id,
            arquivo_nome,
            empresa,
            numero_nf,
            chave_acesso,
            vencimento,
            valor_total,
            status,
            revisado,
            revisado_por,
            revisado_em,
            observacao_revisao,
            json_path,
            criado_em,
            atualizado_em
        FROM documentos
        WHERE id = %s
    """, (documento_id,))

    if not documento:
        abort(404)

    output = StringIO()
    writer = csv.writer(output, delimiter=";", lineterminator="\n")

    writer.writerow([
        "id",
        "cliente_id",
        "arquivo_nome",
        "empresa",
        "numero_nf",
        "chave_acesso",
        "vencimento",
        "valor_total",
        "status",
        "revisado",
        "revisado_por",
        "revisado_em",
        "observacao_revisao",
        "json_path",
        "criado_em",
        "atualizado_em"
    ])

    writer.writerow([
        documento.get("id"),
        documento.get("cliente_id"),
        documento.get("arquivo_nome"),
        documento.get("empresa"),
        documento.get("numero_nf"),
        documento.get("chave_acesso"),
        documento.get("vencimento"),
        documento.get("valor_total"),
        documento.get("status"),
        documento.get("revisado"),
        documento.get("revisado_por"),
        documento.get("revisado_em"),
        documento.get("observacao_revisao"),
        documento.get("json_path"),
        documento.get("criado_em"),
        documento.get("atualizado_em")
    ])

    integracao_id = _obter_integracao_manual(documento["cliente_id"])
    _registrar_tentativa_integracao(
        documento_id=documento["id"],
        integracao_id=integracao_id,
        status="sucesso",
        destino_externo_id=f"csv-documento-{documento['id']}",
        resposta_resumida="CSV individual gerado manualmente."
    )

    return Response(
        output.getvalue(),
        mimetype="text/csv; charset=utf-8",
        headers={
            "Content-Disposition": f"attachment; filename=ocr_documento_{documento_id}.csv"
        }
    )


@app.route("/integracoes/documentos/<int:documento_id>/marcar-integrado", methods=["POST"])
def marcar_documento_integrado(documento_id):
    documento = fetch_one("""
        SELECT id, cliente_id, status
        FROM documentos
        WHERE id = %s
    """, (documento_id,))

    if not documento:
        abort(404)

    integracao_id = _obter_integracao_manual(documento["cliente_id"])

    execute("""
        UPDATE documentos
        SET
            status = 'integrado',
            atualizado_em = NOW()
        WHERE id = %s
    """, (documento_id,))

    _registrar_tentativa_integracao(
        documento_id=documento_id,
        integracao_id=integracao_id,
        status="sucesso",
        destino_externo_id=f"manual-integrado-{documento_id}",
        resposta_resumida="Documento marcado como integrado manualmente."
    )

    return redirect(url_for("historico_integracoes"))


@app.route("/integracoes/documentos/<int:documento_id>/registrar-falha", methods=["POST"])
def registrar_falha_integracao(documento_id):
    documento = fetch_one("""
        SELECT id, cliente_id, status
        FROM documentos
        WHERE id = %s
    """, (documento_id,))

    if not documento:
        abort(404)

    erro = _texto_ou_none(request.form.get("erro")) or "Falha de integração registrada manualmente."
    integracao_id = _obter_integracao_manual(documento["cliente_id"])

    execute("""
        UPDATE documentos
        SET
            status = 'falha_integracao',
            atualizado_em = NOW()
        WHERE id = %s
    """, (documento_id,))

    _registrar_tentativa_integracao(
        documento_id=documento_id,
        integracao_id=integracao_id,
        status="falha",
        destino_externo_id=f"manual-falha-{documento_id}",
        erro=erro,
        resposta_resumida="Falha de integração registrada manualmente."
    )

    return redirect(url_for("historico_integracoes"))


@app.route("/integracoes/documentos/<int:documento_id>/monday-dryrun", methods=["POST"])
def simular_monday_documento(documento_id):
    documento = fetch_one("""
        SELECT *
        FROM documentos
        WHERE id = %s
    """, (documento_id,))

    if not documento:
        abort(404)

    integracao_id = _obter_integracao_dryrun(documento.get("cliente_id") or 0)

    try:
        resultado = gerar_dryrun_monday(documento)

        if resultado["status"] == "apto":
            _registrar_tentativa_integracao(
                documento_id=documento_id,
                integracao_id=integracao_id,
                status="dry_run_apto",
                destino_externo_id=f"monday-dryrun-documento-{documento_id}",
                resposta_resumida=resultado.get("mensagem"),
            )
            flash("Monday dry-run: documento apto para envio.", "success")
        else:
            erro_texto = "; ".join(resultado.get("bloqueios") or [])
            _registrar_tentativa_integracao(
                documento_id=documento_id,
                integracao_id=integracao_id,
                status="dry_run_bloqueado",
                destino_externo_id=f"monday-dryrun-documento-{documento_id}",
                erro=erro_texto or "Documento bloqueado para dry-run.",
                resposta_resumida=resultado.get("mensagem"),
            )
            flash(f"Monday dry-run: {resultado.get('mensagem')}", "warning")
    except Exception as exc:
        _registrar_tentativa_integracao(
            documento_id=documento_id,
            integracao_id=integracao_id,
            status="dry_run_erro",
            destino_externo_id=f"monday-dryrun-documento-{documento_id}",
            erro=str(exc)[:2000],
            resposta_resumida="Excecao local durante dry-run.",
        )
        flash(f"Erro no dry-run: {exc}", "error")

    return redirect(url_for("historico_integracoes"))


@app.route("/integracoes/documentos/<int:documento_id>/enviar-monday", methods=["POST"])
def enviar_monday_documento(documento_id):
    documento = fetch_one("""
        SELECT *
        FROM documentos
        WHERE id = %s
    """, (documento_id,))

    if not documento:
        abort(404)

    confirmar = request.form.get("confirmar", "")
    if confirmar != "sim":
        flash(
            "Envio para Monday requer confirmacao explicita "
            "(confirmar=sim). Nenhuma alteracao foi feita.",
            "warning",
        )
        return redirect(url_for("documento_detalhe", documento_id=documento_id))

    token, board_id, mapa_colunas = _config_monday_envio()
    integracao_id = _obter_integracao_monday_envio(
        documento.get("cliente_id") or 0
    )

    try:
        resultado = enviar_documento_monday(
            documento, token, board_id, mapa_colunas,
        )

        if resultado["status"] == "sucesso":
            _registrar_tentativa_integracao(
                documento_id=documento_id,
                integracao_id=integracao_id,
                status="monday_envio_sucesso",
                destino_externo_id=resultado["item_id"],
                resposta_resumida=(
                    f"Item criado no Monday (ID {resultado['item_id']})."
                ),
            )
            execute("""
                UPDATE documentos
                SET status = 'integrado',
                    atualizado_em = NOW()
                WHERE id = %s
            """, (documento_id,))
            flash("Documento enviado para Monday com sucesso!", "success")
        elif resultado["status"] == "bloqueado":
            bloqueios = "; ".join(resultado.get("bloqueios") or [])
            _registrar_tentativa_integracao(
                documento_id=documento_id,
                integracao_id=integracao_id,
                status="monday_envio_bloqueado",
                erro=bloqueios or "Documento bloqueado para envio Monday.",
                resposta_resumida=resultado.get("mensagem"),
            )
            flash(
                "Monday: " + (resultado.get("mensagem") or "Documento bloqueado."),
                "warning",
            )
        else:
            erro_texto = resultado.get("erro") or "Erro desconhecido na API Monday."
            _registrar_tentativa_integracao(
                documento_id=documento_id,
                integracao_id=integracao_id,
                status="monday_envio_falha",
                destino_externo_id=resultado.get("item_id"),
                erro=erro_texto[:2000],
                resposta_resumida=resultado.get("mensagem"),
            )
            flash(f"Falha no envio Monday: {erro_texto}", "error")
    except Exception as exc:
        _registrar_tentativa_integracao(
            documento_id=documento_id,
            integracao_id=integracao_id,
            status="monday_envio_falha",
            erro=str(exc)[:2000],
            resposta_resumida="Excecao local durante envio Monday.",
        )
        flash(f"Erro no envio Monday: {exc}", "error")

    return redirect(url_for("historico_integracoes"))


@app.route("/exportar/documentos.csv")
def exportar_documentos_csv():
    documentos = fetch_all("""
        SELECT
            id,
            cliente_id,
            arquivo_nome,
            empresa,
            numero_nf,
            chave_acesso,
            vencimento,
            valor_total,
            status,
            revisado,
            revisado_por,
            revisado_em,
            observacao_revisao,
            json_path,
            criado_em,
            atualizado_em
        FROM documentos
        ORDER BY id DESC
    """)

    output = StringIO()
    writer = csv.writer(output, delimiter=";", lineterminator="\n")

    writer.writerow([
        "id",
        "cliente_id",
        "arquivo_nome",
        "empresa",
        "numero_nf",
        "chave_acesso",
        "vencimento",
        "valor_total",
        "status",
        "revisado",
        "revisado_por",
        "revisado_em",
        "observacao_revisao",
        "json_path",
        "criado_em",
        "atualizado_em",
    ])

    for doc in documentos:
        writer.writerow([
            doc.get("id"),
            doc.get("cliente_id"),
            doc.get("arquivo_nome"),
            doc.get("empresa"),
            doc.get("numero_nf"),
            doc.get("chave_acesso"),
            doc.get("vencimento"),
            doc.get("valor_total"),
            doc.get("status"),
            "sim" if doc.get("revisado") else "nao",
            doc.get("revisado_por"),
            doc.get("revisado_em"),
            doc.get("observacao_revisao"),
            doc.get("json_path"),
            doc.get("criado_em"),
            doc.get("atualizado_em"),
        ])

    csv_text = "\ufeff" + output.getvalue()

    return Response(
        csv_text,
        mimetype="text/csv; charset=utf-8",
        headers={
            "Content-Disposition": "attachment; filename=ocr_documentos.csv"
        }
    )


@app.route("/documentos/<int:documento_id>")
def documento_detalhe(documento_id):
    documento = fetch_one("""
        SELECT
            *
        FROM documentos
        WHERE id = %s
    """, (documento_id,))

    if not documento:
        abort(404)

    json_text = None
    json_obj = None

    json_path = documento.get("json_path")
    if json_path:
        path = Path(json_path)
        if path.exists():
            try:
                json_text = path.read_text(encoding="utf-8")
                json_obj = json.loads(json_text)
                json_text = json.dumps(json_obj, ensure_ascii=False, indent=2)
            except Exception as exc:
                json_text = f"Erro ao ler JSON: {exc}"

    texto_ocr = None
    if json_obj:
        texto_ocr = (
            json_obj.get("ocr", {})
            .get("texto_extraido")
        )

    return render_template(
        "documento_detalhe.html",
        documento=documento,
        json_text=json_text,
        texto_ocr=texto_ocr
    )




@app.route("/documentos/<int:documento_id>/editar", methods=["POST"])
def editar_documento(documento_id):
    documento = fetch_one("""
        SELECT id
        FROM documentos
        WHERE id = %s
    """, (documento_id,))

    if not documento:
        abort(404)

    empresa = _texto_ou_none(request.form.get("empresa"))
    numero_nf = _texto_ou_none(request.form.get("numero_nf"))
    chave_acesso = _texto_ou_none(request.form.get("chave_acesso"))
    vencimento = _texto_ou_none(request.form.get("vencimento"))
    valor_total = _valor_decimal_br(request.form.get("valor_total"))
    observacao_revisao = _texto_ou_none(request.form.get("observacao_revisao"))

    execute("""
        UPDATE documentos
        SET
            empresa = %s,
            numero_nf = %s,
            chave_acesso = %s,
            vencimento = %s,
            valor_total = %s,
            observacao_revisao = COALESCE(%s, observacao_revisao),
            status = CASE
                WHEN revisado = TRUE THEN status
                ELSE 'pendente_revisao'
            END
        WHERE id = %s
    """, (
        empresa,
        numero_nf,
        chave_acesso,
        vencimento,
        valor_total,
        observacao_revisao,
        documento_id
    ))

    flash("Campos salvos. Revise os pendentes antes de aprovar.", "success")

    return redirect(url_for("documento_detalhe", documento_id=documento_id))


@app.route("/documentos/<int:documento_id>/revisar", methods=["POST"])
def revisar_documento(documento_id):
    documento = fetch_one("""
        SELECT id, status
        FROM documentos
        WHERE id = %s
    """, (documento_id,))

    if not documento:
        abort(404)

    observacao = request.form.get("observacao_revisao") or None
    novo_status = "pendente_integracao" if documento["status"] in {"pendente_revisao", "erro_ocr"} else documento["status"]

    execute("""
        UPDATE documentos
        SET
            revisado = TRUE,
            revisado_por = %s,
            revisado_em = NOW(),
            observacao_revisao = COALESCE(%s, observacao_revisao),
            status = %s
        WHERE id = %s
    """, ("operador_local", observacao, novo_status, documento_id))

    flash("Documento revisado e enviado para a próxima etapa.", "success")

    return redirect(url_for("documento_detalhe", documento_id=documento_id))


@app.route("/documentos/<int:documento_id>/desfazer-revisao", methods=["POST"])
def desfazer_revisao_documento(documento_id):
    documento = fetch_one("""
        SELECT id
        FROM documentos
        WHERE id = %s
    """, (documento_id,))

    if not documento:
        abort(404)

    execute("""
        UPDATE documentos
        SET
            revisado = FALSE,
            revisado_por = NULL,
            revisado_em = NULL,
            observacao_revisao = NULL
        WHERE id = %s
    """, (documento_id,))

    flash("Revisão desfeita.", "warning")

    return redirect(url_for("documento_detalhe", documento_id=documento_id))


@app.route("/documentos/<int:documento_id>/exportar-json", methods=["POST"])
def exportar_documento_json_validado(documento_id):
    documento = fetch_one("""
        SELECT
            id,
            cliente_id,
            arquivo_nome,
            empresa,
            numero_nf,
            chave_acesso,
            vencimento,
            valor_total,
            status,
            revisado,
            revisado_por,
            revisado_em,
            json_path,
            criado_em,
            atualizado_em
        FROM documentos
        WHERE id = %s
    """, (documento_id,))

    if not documento:
        abort(404)

    resultado = exportar_documento_revisado(
        documento_id,
        obter_documento=lambda _documento_id: documento,
        root_dir=ROOT_DIR,
    )

    integracao_id = _obter_integracao_manual(documento["cliente_id"])

    if resultado["ok"]:
        _registrar_tentativa_integracao(
            documento_id=documento_id,
            integracao_id=integracao_id,
            status="sucesso",
            destino_externo_id=resultado["caminho_relativo"],
            resposta_resumida="JSON validado exportado localmente.",
        )
        flash(f"JSON validado exportado em {resultado['caminho_relativo']}.", "success")
    else:
        _registrar_tentativa_integracao(
            documento_id=documento_id,
            integracao_id=integracao_id,
            status="falha",
            destino_externo_id=f"json-validado-documento-{documento_id}",
            erro=resultado["erro"],
            resposta_resumida="Exportação local do JSON validado recusada ou falhou.",
        )
        flash(resultado["erro"], "error")

    return redirect(url_for("documento_detalhe", documento_id=documento_id))


@app.route("/documentos/<int:documento_id>/gerar-markdown", methods=["POST"])
def gerar_markdown_documento(documento_id):
    documento = fetch_one("""
        SELECT
            id,
            cliente_id,
            arquivo_nome,
            empresa,
            numero_nf,
            chave_acesso,
            vencimento,
            valor_total,
            status,
            revisado,
            revisado_por,
            revisado_em,
            json_path,
            criado_em,
            atualizado_em
        FROM documentos
        WHERE id = %s
    """, (documento_id,))

    if not documento:
        abort(404)

    resultado = gerar_markdown_documento_revisado(
        documento_id,
        obter_documento=lambda _documento_id: documento,
        root_dir=ROOT_DIR,
    )

    integracao_id = _obter_integracao_manual(documento["cliente_id"])

    if resultado["ok"]:
        _registrar_tentativa_integracao(
            documento_id=documento_id,
            integracao_id=integracao_id,
            status="sucesso",
            destino_externo_id=resultado["caminho_relativo"],
            resposta_resumida="Relatório Markdown gerado localmente.",
        )
        flash(f"Relatório Markdown gerado em {resultado['caminho_relativo']}.", "success")
    else:
        _registrar_tentativa_integracao(
            documento_id=documento_id,
            integracao_id=integracao_id,
            status="falha",
            destino_externo_id=f"markdown-documento-{documento_id}",
            erro=resultado["erro"],
            resposta_resumida="Geração local do relatório Markdown recusada ou falhou.",
        )
        flash(resultado["erro"], "error")

    return redirect(url_for("documento_detalhe", documento_id=documento_id))


PLATAFORMAS_INTEGRACAO = [
    {
        "id": "monday",
        "nome": "Monday.com",
        "status_plataforma": "suportada",
        "variaveis": [
            {"chave": "MONDAY_API_TOKEN", "rotulo": "Token da API", "sensivel": True},
            {"chave": "MONDAY_BOARD_ID", "rotulo": "ID do Board", "sensivel": False},
            {"chave": "MONDAY_COLUMN_EMPRESA", "rotulo": "Coluna: Empresa", "sensivel": False},
            {"chave": "MONDAY_COLUMN_NUMERO_NF", "rotulo": "Coluna: N\u00famero NF", "sensivel": False},
            {"chave": "MONDAY_COLUMN_CHAVE_ACESSO", "rotulo": "Coluna: Chave de Acesso", "sensivel": False},
            {"chave": "MONDAY_COLUMN_VENCIMENTO", "rotulo": "Coluna: Vencimento", "sensivel": False},
            {"chave": "MONDAY_COLUMN_VALOR_TOTAL", "rotulo": "Coluna: Valor Total", "sensivel": False},
            {"chave": "MONDAY_COLUMN_OBSERVACAO", "rotulo": "Coluna: Observa\u00e7\u00e3o", "sensivel": False},
        ],
        "observacao": "Plataforma suportada. Configure por vari\u00e1veis de ambiente.",
    },
    {
        "id": "google_sheets",
        "nome": "Google Sheets",
        "status_plataforma": "planejada",
        "variaveis": [
            {"chave": "GOOGLE_SHEETS_CREDENTIALS", "rotulo": "Credencial JSON", "sensivel": True},
            {"chave": "GOOGLE_SHEETS_SPREADSHEET_ID", "rotulo": "ID da Planilha", "sensivel": False},
            {"chave": "GOOGLE_SHEETS_ABA_NOME", "rotulo": "Nome da Aba", "sensivel": False},
        ],
        "observacao": "Integra\u00e7\u00e3o planejada para fase futura.",
    },
    {
        "id": "erp_api",
        "nome": "ERP / API pr\u00f3pria",
        "status_plataforma": "planejada",
        "variaveis": [
            {"chave": "ERP_API_BASE_URL", "rotulo": "URL base da API", "sensivel": False},
            {"chave": "ERP_API_TOKEN", "rotulo": "Token de autentica\u00e7\u00e3o", "sensivel": True},
        ],
        "observacao": "Integra\u00e7\u00e3o planejada para fase futura.",
    },
]


def _classificar_variavel_config(valor):
    if valor is None:
        return "AUSENTE"
    texto = str(valor).strip()
    if not texto:
        return "AUSENTE"
    texto_lower = texto.lower()
    placeholders = ("cole", "aqui", "exemplo", "nao_cole", "n\u00e3o_cole", "seu_")
    if any(p in texto_lower for p in placeholders):
        return "PLACEHOLDER"
    if texto_lower.startswith("exemplo_"):
        return "PLACEHOLDER"
    return "CONFIGURADO"


def _status_variaveis_plataforma(plataforma):
    resultado = []
    for var_info in plataforma["variaveis"]:
        valor = os.getenv(var_info["chave"], "")
        status = _classificar_variavel_config(valor)
        resultado.append({
            "chave": var_info["chave"],
            "rotulo": var_info["rotulo"],
            "sensivel": var_info["sensivel"],
            "status": status,
        })
    return resultado


def _montar_status_plataformas_integracao():
    resultado = []
    for plataforma in PLATAFORMAS_INTEGRACAO:
        variaveis_status = _status_variaveis_plataforma(plataforma)
        if plataforma["status_plataforma"] == "planejada":
            status_geral = "PLANEJADA"
        else:
            statuses = {v["status"] for v in variaveis_status}
            if statuses == {"CONFIGURADO"}:
                status_geral = "CONFIGURADA"
            else:
                status_geral = "INCOMPLETA"
        resultado.append({
            "id": plataforma["id"],
            "nome": plataforma["nome"],
            "status_geral": status_geral,
            "observacao": plataforma["observacao"],
            "variaveis": variaveis_status,
        })
    return resultado


@app.route("/integracoes/configuracao")
def config_integracoes():
    plataformas = _montar_status_plataformas_integracao()
    return render_template("config_integracoes.html", plataformas=plataformas)


if __name__ == "__main__":
    app.run(
        host="127.0.0.1",
        port=5000,
        debug=False
    )

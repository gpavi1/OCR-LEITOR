from pathlib import Path
import json
import os
import hmac
import csv
import sys
import uuid
import datetime
from io import StringIO
from decimal import Decimal, InvalidOperation

from flask import Flask, Response, abort, flash, redirect, render_template, request, session, url_for

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from database.mysql_db import fetch_all, fetch_one, execute


app = Flask(__name__)
app.secret_key = os.getenv("WEB_SECRET_KEY", "ocr-leitor-local-dev")

EXTENSOES_PERMITIDAS_UPLOAD = {".jpg", ".jpeg", ".png", ".pdf"}
TAMANHO_MAXIMO_UPLOAD = 10 * 1024 * 1024


def extensao_permitida_upload(nome_arquivo):
    nome = Path(nome_arquivo).name
    ext = Path(nome).suffix.lower()
    return ext in EXTENSOES_PERMITIDAS_UPLOAD


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


def _texto_ou_none(valor):
    if valor is None:
        return None

    valor = str(valor).strip()
    return valor or None


@app.before_request
def exigir_login():
    rotas_livres = {"login", "static", "health"}
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

        expected_user, expected_password = _web_credentials()

        usuario_ok = hmac.compare_digest(username, expected_user)
        senha_ok = hmac.compare_digest(password, expected_password)

        if usuario_ok and senha_ok:
            session["autenticado"] = True
            session["usuario"] = username
            return redirect(url_for("index"))

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
            t.criado_em
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

    return redirect(url_for("documento_detalhe", documento_id=documento_id))


@app.route("/documentos/<int:documento_id>/revisar", methods=["POST"])
def revisar_documento(documento_id):
    documento = fetch_one("""
        SELECT id
        FROM documentos
        WHERE id = %s
    """, (documento_id,))

    if not documento:
        abort(404)

    observacao = request.form.get("observacao_revisao") or None

    execute("""
        UPDATE documentos
        SET
            revisado = TRUE,
            revisado_por = %s,
            revisado_em = NOW(),
            observacao_revisao = COALESCE(%s, observacao_revisao),
            status = CASE
                WHEN status = 'pendente_revisao' THEN 'pendente_integracao'
                ELSE status
            END
        WHERE id = %s
    """, ("operador_local", observacao, documento_id))

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

    return redirect(url_for("documento_detalhe", documento_id=documento_id))


if __name__ == "__main__":
    app.run(
        host="127.0.0.1",
        port=5000,
        debug=False
    )

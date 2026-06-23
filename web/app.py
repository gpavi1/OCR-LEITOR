from pathlib import Path
import json
import os
import hmac
import csv
import sys
from io import StringIO

from flask import Flask, render_template, abort, redirect, url_for, request, session, Response

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from database.mysql_db import fetch_all, fetch_one, execute


app = Flask(__name__)
app.secret_key = os.getenv("WEB_SECRET_KEY", "ocr-leitor-local-dev")




def _web_credentials():
    return (
        os.getenv("WEB_USERNAME", "admin"),
        os.getenv("WEB_PASSWORD", "admin")
    )


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
            observacao_revisao = %s,
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

from pathlib import Path
import json
import sys

from flask import Flask, render_template, abort

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from database.mysql_db import fetch_all, fetch_one


app = Flask(__name__)


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


if __name__ == "__main__":
    app.run(
        host="127.0.0.1",
        port=5000,
        debug=False
    )

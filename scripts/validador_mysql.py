import sys
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BASE_DIR))

TABELAS_ESPERADAS = {"clientes", "documentos", "integracoes", "integracao_tentativas"}


def _ok(nome, detalhe=""):
    return {"nome": nome, "status": "OK", "detalhe": detalhe}


def _erro(nome, detalhe=""):
    return {"nome": nome, "status": "ERRO", "detalhe": detalhe}


def _aviso(nome, detalhe=""):
    return {"nome": nome, "status": "AVISO", "detalhe": detalhe}


def verificar_conexao():
    try:
        from database.mysql_db import fetch_all, testar_conexao
    except ImportError as exc:
        return [_erro("Import database.mysql_db", f"module nao encontrado: {exc}")]

    resultados = []
    ok, msg = testar_conexao()
    if not ok:
        resultados.append(_erro("Conexao MySQL", msg or "falha na conexao"))
        return resultados

    resultados.append(_ok("Conexao MySQL", "conexao bem-sucedida"))

    try:
        rows = fetch_all(
            "SELECT TABLE_NAME FROM information_schema.TABLES "
            "WHERE TABLE_SCHEMA = DATABASE()"
        )
        tabelas_existentes = {row["TABLE_NAME"] for row in rows} if rows else set()
        resultados.append(_ok("Tabelas encontradas", ", ".join(sorted(tabelas_existentes)) if tabelas_existentes else "nenhuma"))

        for tabela in sorted(TABELAS_ESPERADAS):
            if tabela in tabelas_existentes:
                row = fetch_all(f"SELECT COUNT(*) AS total FROM {tabela}")
                total = row[0]["total"] if row else 0
                resultados.append(_ok(f"Tabela {tabela}", f"existe ({total} registros)"))
            else:
                resultados.append(_erro(f"Tabela {tabela}", "ausente"))
    except Exception as exc:
        resultados.append(_erro("Listagem de tabelas", str(exc)))

    return resultados


def imprimir_relatorio(resultados):
    print("OCR-LEITOR - Validador MySQL")
    print("=" * 30)
    for item in resultados:
        detalhe = f" - {item['detalhe']}" if item.get("detalhe") else ""
        print(f"[{item['status']}] {item['nome']}{detalhe}")


def main():
    resultados = verificar_conexao()
    imprimir_relatorio(resultados)
    return 1 if any(item["status"] == "ERRO" for item in resultados) else 0


if __name__ == "__main__":
    sys.exit(main())

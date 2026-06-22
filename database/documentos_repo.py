from typing import Optional

from database.mysql_db import execute, fetch_all, fetch_one


def criar_documento_recebido(
    cliente_id: int,
    arquivo_nome: str,
    arquivo_origem: str,
    arquivo_hash: Optional[str] = None,
) -> int:
    sql = """
        INSERT INTO documentos (
            cliente_id, arquivo_nome, arquivo_origem, arquivo_hash, status
        ) VALUES (%s, %s, %s, %s, %s)
    """
    return execute(sql, (cliente_id, arquivo_nome, arquivo_origem, arquivo_hash, "recebido"))


def marcar_processando(documento_id: int) -> None:
    execute("UPDATE documentos SET status = %s WHERE id = %s", ("processando", documento_id))


def atualizar_documento_extraido(
    documento_id: int,
    tipo_documento: str,
    empresa: Optional[str],
    numero_nf: Optional[str],
    chave_acesso: Optional[str],
    vencimento_iso: Optional[str],
    valor_total: Optional[float],
    json_path: str,
    status: str,
    arquivo_destino: Optional[str] = None,
) -> None:
    sql = """
        UPDATE documentos
        SET tipo_documento = %s,
            empresa = %s,
            numero_nf = %s,
            chave_acesso = %s,
            vencimento = %s,
            valor_total = %s,
            json_path = %s,
            status = %s,
            arquivo_destino = %s
        WHERE id = %s
    """
    execute(
        sql,
        (
            tipo_documento,
            empresa,
            numero_nf,
            chave_acesso,
            vencimento_iso,
            valor_total,
            json_path,
            status,
            arquivo_destino,
            documento_id,
        ),
    )


def marcar_erro(documento_id: int, status: str, erro: str) -> None:
    sql = """
        UPDATE documentos
        SET status = %s,
            ultimo_erro = %s,
            tentativas = tentativas + 1
        WHERE id = %s
    """
    execute(sql, (status, erro[:4000], documento_id))


def obter_documento(documento_id: int):
    return fetch_one("SELECT * FROM documentos WHERE id = %s", (documento_id,))


def listar_pendentes_integracao(cliente_id: Optional[int] = None):
    if cliente_id:
        return fetch_all(
            "SELECT * FROM documentos WHERE cliente_id = %s AND status = %s ORDER BY criado_em ASC",
            (cliente_id, "pendente_integracao"),
        )
    return fetch_all(
        "SELECT * FROM documentos WHERE status = %s ORDER BY criado_em ASC",
        ("pendente_integracao",),
    )

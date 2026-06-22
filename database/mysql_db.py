import os
from contextlib import contextmanager
from typing import Any, Dict, Iterable, List, Optional, Tuple

from dotenv import load_dotenv

load_dotenv()


def _config() -> Dict[str, Any]:
    return {
        "host": os.getenv("DB_HOST", "localhost"),
        "port": int(os.getenv("DB_PORT", "3306")),
        "database": os.getenv("DB_NAME", "ocr_leitor"),
        "user": os.getenv("DB_USER", "ocr_app"),
        "password": os.getenv("DB_PASSWORD", ""),
        "charset": "utf8mb4",
        "use_unicode": True,
    }


def _connect():
    # Import lazy para o projeto continuar gerando JSON mesmo antes de instalar MySQL.
    import mysql.connector

    cfg = _config()
    if not cfg["password"]:
        raise RuntimeError("DB_PASSWORD não configurado no .env")
    return mysql.connector.connect(**cfg)


@contextmanager
def get_connection():
    conn = _connect()
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def execute(sql: str, params: Optional[Tuple[Any, ...]] = None) -> int:
    with get_connection() as conn:
        cursor = conn.cursor(dictionary=True)
        cursor.execute(sql, params or ())
        last_id = cursor.lastrowid or 0
        cursor.close()
        return last_id


def fetch_one(sql: str, params: Optional[Tuple[Any, ...]] = None) -> Optional[Dict[str, Any]]:
    with get_connection() as conn:
        cursor = conn.cursor(dictionary=True)
        cursor.execute(sql, params or ())
        row = cursor.fetchone()
        cursor.close()
        return row


def fetch_all(sql: str, params: Optional[Tuple[Any, ...]] = None) -> List[Dict[str, Any]]:
    with get_connection() as conn:
        cursor = conn.cursor(dictionary=True)
        cursor.execute(sql, params or ())
        rows = cursor.fetchall()
        cursor.close()
        return rows


def testar_conexao() -> Tuple[bool, str]:
    try:
        row = fetch_one("SELECT 1 AS ok")
        return bool(row and row.get("ok") == 1), "Conexão MySQL OK"
    except Exception as exc:
        return False, str(exc)

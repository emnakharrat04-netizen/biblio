"""
database.py – MySQL connection pool and query helpers.
All other backend modules import from here; nothing else touches the DB directly.
"""

import os
import mysql.connector
from mysql.connector import pooling
from contextlib import contextmanager

# ── Configuration ─────────────────────────────────────────────────────────────
DB_CONFIG = {
    "host":     os.getenv("DB_HOST",     "localhost"),
    "port":     int(os.getenv("DB_PORT", "3306")),
    "user":     os.getenv("DB_USER",     "root"),
    "password": os.getenv("DB_PASSWORD", ""),
    "database": os.getenv("DB_NAME",     "bibliotheque"),
}

_pool: pooling.MySQLConnectionPool | None = None


def get_pool() -> pooling.MySQLConnectionPool:
    global _pool
    if _pool is None:
        _pool = pooling.MySQLConnectionPool(
            pool_name="biblio_pool",
            pool_size=5,
            **DB_CONFIG,
        )
    return _pool


@contextmanager
def get_connection():
    """Yield a connection from the pool; commit on success, rollback on error."""
    conn = get_pool().get_connection()
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


# ── Convenience helpers ────────────────────────────────────────────────────────

def fetchall(query: str, params: tuple = ()) -> list[dict]:
    """Execute a SELECT and return all rows as a list of dicts."""
    with get_connection() as conn:
        cur = conn.cursor(dictionary=True)
        cur.execute(query, params)
        return cur.fetchall()


def fetchone(query: str, params: tuple = ()) -> dict | None:
    """Execute a SELECT and return the first row as a dict (or None)."""
    rows = fetchall(query, params)
    return rows[0] if rows else None


def execute(query: str, params: tuple = ()) -> int:
    """Execute an INSERT / UPDATE / DELETE. Returns lastrowid."""
    with get_connection() as conn:
        cur = conn.cursor()
        cur.execute(query, params)
        return cur.lastrowid


def ping() -> bool:
    """Return True if the database is reachable."""
    try:
        fetchone("SELECT 1 AS ok")
        return True
    except Exception:
        return False

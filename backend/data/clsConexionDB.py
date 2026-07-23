"""Conexión a PostgreSQL para Climb, con una capa de compatibilidad.

El resto del data layer (clsInteraccionDB) fue escrito contra la API de sqlite3:
`conexion.execute("... ?", params)`, `cursor.lastrowid`, `fila["columna"]`, etc.
Para no reescribir cientos de llamadas, `obtener_conexion()` devuelve un envoltorio
(`_ConexionCompat`) que imita esa API sobre psycopg2:

  - `.execute(sql, params)` traduce los placeholders '?' a '%s' y devuelve un cursor.
  - el cursor es RealDictCursor, así que `fila["columna"]` sigue funcionando.
  - `.cursor()`, `.commit()`, `.close()` se comportan igual que en sqlite3.

`cursor.lastrowid` NO existe en psycopg2: los INSERT que necesitan el id usan
`INSERT ... RETURNING <pk>` + `fetchone()` (ver clsInteraccionDB).
"""

import os

import psycopg2
from psycopg2.extras import RealDictCursor


def obtener_conexion():
    """Devuelve una conexión a PostgreSQL (envuelta para imitar sqlite3)."""
    url = os.getenv("DATABASE_URL")
    if not url:
        raise RuntimeError("DATABASE_URL no está definida en el entorno.")
    return _ConexionCompat(psycopg2.connect(url, cursor_factory=RealDictCursor))


def inicializar_db():
    """El esquema lo crea el contenedor de PostgreSQL vía database/init.sql.

    Se mantiene la función porque main.py la llama al arrancar; aquí es un no-op.
    """
    print("[INFO] Esquema gestionado por PostgreSQL (database/init.sql).")


def _traducir(sql):
    """psycopg2 usa '%s' como placeholder en vez del '?' de sqlite3."""
    return sql.replace("?", "%s")


class _CursorCompat:
    """Cursor que traduce '?'->'%s' en execute(). El resto (fetchone, fetchall,
    rowcount, etc.) se delega al cursor real de psycopg2."""

    def __init__(self, cur):
        self._cur = cur

    def execute(self, sql, params=()):
        self._cur.execute(_traducir(sql), params)
        return self

    def fetchone(self):
        return self._cur.fetchone()

    def fetchall(self):
        return self._cur.fetchall()

    def __getattr__(self, name):
        return getattr(self._cur, name)


class _ConexionCompat:
    """Imita sqlite3.Connection sobre psycopg2 para el data layer existente."""

    def __init__(self, conn):
        self._c = conn

    def execute(self, sql, params=()):
        cur = self._c.cursor()
        cur.execute(_traducir(sql), params)
        return _CursorCompat(cur)

    def cursor(self):
        return _CursorCompat(self._c.cursor())

    def commit(self):
        self._c.commit()

    def rollback(self):
        self._c.rollback()

    def close(self):
        self._c.close()

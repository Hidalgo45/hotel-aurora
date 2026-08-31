"""Acceso a PostgreSQL.

Todas las consultas del proyecto pasan por aqui y siempre son parametrizadas
(los valores viajan aparte de la sentencia), que es la defensa contra
inyeccion SQL.
"""
from __future__ import annotations

from contextlib import contextmanager

import psycopg
from psycopg.rows import dict_row

from .config import Config


@contextmanager
def obtener_conexion():
    """Entrega una conexion que devuelve las filas como diccionarios."""
    conn = psycopg.connect(Config.cadena_conexion(), row_factory=dict_row)
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def consultar(sql: str, params: tuple | None = None) -> list[dict]:
    """Devuelve todas las filas de una consulta."""
    with obtener_conexion() as conn:
        return conn.execute(sql, params).fetchall()


def consultar_uno(sql: str, params: tuple | None = None) -> dict | None:
    """Devuelve la primera fila o None."""
    with obtener_conexion() as conn:
        return conn.execute(sql, params).fetchone()


def ejecutar(sql: str, params: tuple | None = None) -> None:
    """Ejecuta una sentencia que no devuelve filas."""
    with obtener_conexion() as conn:
        conn.execute(sql, params)


def probar_conexion() -> tuple[bool, str]:
    """Se usa al arrancar para avisar con claridad si la base no responde."""
    try:
        with obtener_conexion() as conn:
            fila = conn.execute(
                "SELECT COUNT(*) AS n FROM habitacion").fetchone()
        return True, f"Conectado. {fila['n']} habitaciones cargadas."
    except Exception as e:                                   # noqa: BLE001
        return False, str(e).split("\n")[0]

"""Configuracion de la aplicacion, leida del archivo .env."""
from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv

RAIZ = Path(__file__).resolve().parent.parent
load_dotenv(RAIZ / ".env")


class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "clave-de-desarrollo")

    DB_HOST = os.getenv("DB_HOST", "localhost")
    DB_PORT = os.getenv("DB_PORT", "5432")
    DB_NAME = os.getenv("DB_NAME", "hotel_aurora")
    DB_USER = os.getenv("DB_USER", "postgres")
    DB_PASSWORD = os.getenv("DB_PASSWORD", "")

    DEBUG = os.getenv("FLASK_DEBUG", "0") == "1"

    HOTEL_NOMBRE = "Hotel Aurora"
    HOTEL_CIUDAD = "Quito, Ecuador"
    HOTEL_TELEFONO = "(02) 299 1700"

    @classmethod
    def cadena_conexion(cls) -> str:
        return (f"host={cls.DB_HOST} port={cls.DB_PORT} dbname={cls.DB_NAME} "
                f"user={cls.DB_USER} password={cls.DB_PASSWORD}")

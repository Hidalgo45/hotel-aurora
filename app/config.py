"""QUE HACE: reune en un solo lugar todos los ajustes del sistema.

Lee el archivo .env, que es donde vive la contrasena de la base y los datos
del correo.

SI PREGUNTAN POR ESTE ARCHIVO:
"Las contrasenas no estan escritas en el codigo. Estan en un archivo aparte
que no se sube al repositorio, y cada integrante tiene el suyo con sus
propios datos."
"""
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

    # ---- Envio del comprobante de reserva por correo ----
    # "archivo": guarda el mensaje en la carpeta correos_enviados en lugar de
    #            enviarlo. Es el valor por defecto: la aplicacion funciona sin
    #            conexion y el flujo se puede demostrar en la sustentacion.
    # "smtp":    envia de verdad con los datos de abajo.
    CORREO_BACKEND = os.getenv("CORREO_BACKEND", "archivo")
    SMTP_HOST = os.getenv("SMTP_HOST", "smtp.gmail.com")
    SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
    SMTP_USUARIO = os.getenv("SMTP_USUARIO", "")
    SMTP_CLAVE = os.getenv("SMTP_CLAVE", "")
    SMTP_REMITENTE = os.getenv("SMTP_REMITENTE", "reservas@hotelaurora.ec")
    SMTP_TIEMPO_LIMITE = int(os.getenv("SMTP_TIEMPO_LIMITE", "10"))
    CARPETA_CORREOS = RAIZ / "correos_enviados"

    @classmethod
    def cadena_conexion(cls) -> str:
        return (f"host={cls.DB_HOST} port={cls.DB_PORT} dbname={cls.DB_NAME} "
                f"user={cls.DB_USER} password={cls.DB_PASSWORD}")

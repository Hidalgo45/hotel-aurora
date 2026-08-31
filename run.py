"""Punto de entrada del Hotel Aurora.

Uso normal, solo en este computador:

    .venv\\Scripts\\python.exe run.py

Para que otras personas de la misma red WiFi puedan entrar (pruebas de
usabilidad), se enlaza a todas las interfaces:

    .venv\\Scripts\\python.exe run.py --publico
"""
import os
import socket
import sys

from app import create_app
from app.db import probar_conexion

app = create_app()


def ip_local() -> str:
    """Devuelve la IP de esta maquina en la red local, para compartirla."""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.connect(("8.8.8.8", 80))       # no envia nada, solo resuelve la ruta
            return s.getsockname()[0]
    except OSError:
        return "no disponible"


if __name__ == "__main__":
    publico = "--publico" in sys.argv
    host = "0.0.0.0" if publico else "127.0.0.1"
    debug = app.config["DEBUG"]

    # El depurador de Flask permite ejecutar codigo arbitrario desde el
    # navegador cuando ocurre un error. En local es comodo; expuesto a la red
    # es una puerta abierta al computador. Por eso se apaga solo.
    if publico and debug:
        debug = False
        aviso = ("  Modo depuracion DESACTIVADO por seguridad: el servidor\n"
                 "  esta abierto a la red y el depurador permitiria ejecutar\n"
                 "  codigo desde fuera.")
    else:
        aviso = ""

    ok, mensaje = probar_conexion()
    print("\n  HOTEL AURORA")
    print("  " + "=" * 52)
    if ok:
        print(f"  Base de datos: {mensaje}")
    else:
        print("  No se pudo conectar a PostgreSQL:")
        print(f"    {mensaje}")
        print("  Revisa el archivo .env y ejecuta:  python setup_db.py")

    if publico:
        print(f"  En este equipo: http://127.0.0.1:5000")
        print(f"  Desde otros:    http://{ip_local()}:5000")
        print("  " + "=" * 52)
        print(aviso)
    else:
        print("  Servidor:      http://127.0.0.1:5000")
        print("  " + "=" * 52)
        print("  Solo visible en este computador.")
        print("  Para compartirlo en la red WiFi:  run.py --publico")

    print()
    app.run(host=host, port=5000, debug=debug)

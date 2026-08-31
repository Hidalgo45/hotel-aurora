"""Punto de entrada del Hotel Aurora.

    .venv\\Scripts\\python.exe run.py
"""
from app import create_app
from app.db import probar_conexion

app = create_app()

if __name__ == "__main__":
    ok, mensaje = probar_conexion()
    print("\n  HOTEL AURORA")
    print("  " + "=" * 46)
    if ok:
        print(f"  Base de datos: {mensaje}")
    else:
        print("  No se pudo conectar a PostgreSQL:")
        print(f"    {mensaje}")
        print("  Revisa el archivo .env y ejecuta:  python setup_db.py")
    print("  Servidor:      http://127.0.0.1:5000")
    print("  " + "=" * 46 + "\n")

    app.run(host="127.0.0.1", port=5000, debug=app.config["DEBUG"])

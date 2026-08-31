"""Instalador de la base de datos del Hotel Aurora.

Crea la base de datos si no existe y ejecuta los siete scripts SQL en orden.
Se puede volver a correr las veces que haga falta: reconstruye todo desde cero.

Uso:
    .venv\\Scripts\\python.exe setup_db.py
"""
from __future__ import annotations

import sys
from pathlib import Path

import psycopg
from dotenv import dotenv_values

RAIZ = Path(__file__).resolve().parent
CARPETA_SQL = RAIZ / "database"

SCRIPTS = [
    "01_schema.sql",
    "02_constraints.sql",
    "03_triggers.sql",
    "04_procedures.sql",
    "05_reportes.sql",
    "06_seguridad.sql",
    "07_datos_prueba.sql",
]


def leer_configuracion() -> dict[str, str]:
    config = dotenv_values(RAIZ / ".env")
    if not config.get("DB_PASSWORD"):
        print("\n  Falta la contrasena de PostgreSQL.")
        print("  Abre el archivo .env y escribe tu contrasena en la linea")
        print("  DB_PASSWORD=  (la misma que usas en pgAdmin con el usuario postgres)\n")
        sys.exit(1)
    return config


def cadena_conexion(config: dict[str, str], base: str) -> str:
    return (
        f"host={config['DB_HOST']} port={config['DB_PORT']} "
        f"dbname={base} user={config['DB_USER']} password={config['DB_PASSWORD']}"
    )


def crear_base_si_no_existe(config: dict[str, str]) -> None:
    nombre = config["DB_NAME"]
    with psycopg.connect(cadena_conexion(config, "postgres"), autocommit=True) as conn:
        existe = conn.execute(
            "SELECT 1 FROM pg_database WHERE datname = %s", (nombre,)
        ).fetchone()
        if existe:
            print(f"  La base de datos '{nombre}' ya existe.")
        else:
            conn.execute(f'CREATE DATABASE "{nombre}" ENCODING \'UTF8\'')
            print(f"  Base de datos '{nombre}' creada.")


def ejecutar_scripts(config: dict[str, str]) -> None:
    with psycopg.connect(cadena_conexion(config, config["DB_NAME"])) as conn:
        conn.autocommit = True
        for nombre in SCRIPTS:
            ruta = CARPETA_SQL / nombre
            if not ruta.exists():
                print(f"  [FALTA]  {nombre}")
                continue
            sql = ruta.read_text(encoding="utf-8")
            try:
                conn.execute(sql)
                print(f"  [OK]     {nombre}")
            except psycopg.Error as e:
                print(f"  [ERROR]  {nombre}")
                print(f"           {e}")
                sys.exit(1)


def resumen(config: dict[str, str]) -> None:
    consulta = """
        SELECT 'Habitaciones' AS entidad, COUNT(*)::text AS total FROM habitacion
        UNION ALL SELECT 'Usuarios',  COUNT(*)::text FROM usuario
        UNION ALL SELECT 'Reservas',  COUNT(*)::text FROM reserva
        UNION ALL SELECT 'Pagos',     COUNT(*)::text FROM pago
        UNION ALL SELECT 'Triggers',  COUNT(*)::text FROM pg_trigger
                                       WHERE NOT tgisinternal
        UNION ALL SELECT 'Procedimientos y funciones', COUNT(*)::text
                    FROM pg_proc p JOIN pg_namespace n ON n.oid = p.pronamespace
                   WHERE n.nspname = 'public'
        UNION ALL SELECT 'Restricciones CHECK', COUNT(*)::text
                    FROM pg_constraint
                   WHERE contype = 'c' AND connamespace = 'public'::regnamespace
    """
    with psycopg.connect(cadena_conexion(config, config["DB_NAME"])) as conn:
        print("\n  RESUMEN DE LA CARGA")
        print("  " + "-" * 40)
        for entidad, total in conn.execute(consulta):
            print(f"  {entidad:<28} {total:>8}")


if __name__ == "__main__":
    print("\n  HOTEL AURORA - instalacion de la base de datos")
    print("  " + "=" * 46 + "\n")
    cfg = leer_configuracion()
    crear_base_si_no_existe(cfg)
    ejecutar_scripts(cfg)
    resumen(cfg)
    print("\n  Listo. Ahora ejecuta:  .venv\\Scripts\\python.exe run.py\n")

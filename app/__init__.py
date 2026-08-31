"""Fabrica de la aplicacion Flask del Hotel Aurora."""
from __future__ import annotations

from datetime import date, timedelta

from flask import Flask, render_template

from .config import Config


def create_app() -> Flask:
    app = Flask(__name__)
    app.config.from_object(Config)

    # ---- Blueprints ----
    from .blueprints.publico import bp as bp_publico
    from .blueprints.cuenta import bp as bp_cuenta
    from .blueprints.admin import bp as bp_admin

    app.register_blueprint(bp_publico)
    app.register_blueprint(bp_cuenta)
    app.register_blueprint(bp_admin)

    # ---- Valores disponibles en todas las plantillas ----
    @app.context_processor
    def inyectar_globales():
        from flask import session
        return {
            "hotel": {
                "nombre": Config.HOTEL_NOMBRE,
                "ciudad": Config.HOTEL_CIUDAD,
                "telefono": Config.HOTEL_TELEFONO,
            },
            "usuario_actual": session.get("usuario"),
            "hoy": date.today().isoformat(),
            "manana": (date.today() + timedelta(days=1)).isoformat(),
        }

    # ---- Filtros de plantilla ----
    @app.template_filter("dinero")
    def filtro_dinero(valor):
        try:
            return f"${float(valor):,.2f}"
        except (TypeError, ValueError):
            return "$0.00"

    @app.template_filter("fecha")
    def filtro_fecha(valor):
        MESES = ["ene", "feb", "mar", "abr", "may", "jun",
                 "jul", "ago", "sep", "oct", "nov", "dic"]
        if not valor:
            return "-"
        return f"{valor.day:02d} {MESES[valor.month - 1]} {valor.year}"

    # ---- Paginas de error con mensajes utiles ----
    @app.errorhandler(404)
    def no_encontrado(e):
        return render_template("errores/404.html"), 404

    @app.errorhandler(500)
    def error_interno(e):
        return render_template("errores/500.html"), 500

    return app

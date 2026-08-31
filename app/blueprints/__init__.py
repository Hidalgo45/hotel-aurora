"""Capa web: rutas agrupadas por area funcional."""
from __future__ import annotations

from functools import wraps

from flask import flash, redirect, session, url_for


def requiere_sesion(func):
    """Protege una ruta que exige haber iniciado sesion."""

    @wraps(func)
    def envoltura(*args, **kwargs):
        if not session.get("usuario"):
            flash("Inicia sesion para continuar con tu reserva.", "warning")
            return redirect(url_for("cuenta.login"))
        return func(*args, **kwargs)

    return envoltura


def requiere_rol(*roles: str):
    """Protege una ruta que exige un rol concreto."""

    def decorador(func):
        @wraps(func)
        def envoltura(*args, **kwargs):
            usuario = session.get("usuario")
            if not usuario:
                flash("Inicia sesion para acceder al panel.", "warning")
                return redirect(url_for("cuenta.login"))
            if usuario["rol"] not in roles:
                flash("Tu cuenta no tiene permiso para entrar a esa seccion.",
                      "danger")
                return redirect(url_for("publico.home"))
            return func(*args, **kwargs)

        return envoltura

    return decorador

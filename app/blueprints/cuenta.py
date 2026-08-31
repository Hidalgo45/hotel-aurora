"""Autenticacion y area privada del huesped."""
from __future__ import annotations

from datetime import datetime

from flask import (Blueprint, flash, redirect, render_template, request,
                   session, url_for)

from . import requiere_sesion
from ..dominio import FabricaUsuarios
from ..dominio.excepciones import ErrorDominio
from ..repositorios import ReservaRepositorioPG, UsuarioRepositorioPG

bp = Blueprint("cuenta", __name__, url_prefix="/cuenta")

usuarios_repo = UsuarioRepositorioPG()
reservas_repo = ReservaRepositorioPG()


@bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email", "").strip()
        clave = request.form.get("password", "")

        fila = usuarios_repo.buscar_por_email(email)

        # Mensaje deliberadamente generico: no revela si el correo existe.
        if not fila:
            flash("Correo o contrasena incorrectos.", "danger")
            return render_template("cuenta/login.html", email=email)

        usuario = FabricaUsuarios.desde_fila(fila)
        if not usuario.verificar_clave(clave):
            flash("Correo o contrasena incorrectos.", "danger")
            return render_template("cuenta/login.html", email=email)

        session["usuario"] = {
            "id": fila["id_usuario"],
            "nombre": usuario.nombre_completo(),
            "email": usuario.email,
            "rol": fila["rol"],
            "descripcion_rol": usuario.descripcion_rol(),
        }

        flash(f"Hola, {usuario.nombres}.", "success")
        if fila["rol"] in ("ADMIN", "RECEPCION"):
            return redirect(url_for("admin.dashboard"))
        return redirect(request.args.get("next") or url_for("publico.home"))

    return render_template("cuenta/login.html", email="")


@bp.route("/registro", methods=["GET", "POST"])
def registro():
    if request.method == "POST":
        datos = {
            "cedula": request.form.get("cedula", "").strip(),
            "nombres": request.form.get("nombres", "").strip(),
            "apellidos": request.form.get("apellidos", "").strip(),
            "email": request.form.get("email", "").strip(),
            "telefono": request.form.get("telefono", "").strip() or None,
            "ciudad": request.form.get("ciudad", "").strip() or None,
            "password": request.form.get("password", ""),
        }

        try:
            if len(datos["password"]) < 8:
                raise ErrorDominio(
                    "La contrasena debe tener al menos 8 caracteres.")
            if datos["password"] != request.form.get("password2", ""):
                raise ErrorDominio("Las dos contrasenas no coinciden.")

            datos["fecha_nacimiento"] = datetime.strptime(
                request.form.get("fecha_nacimiento", ""), "%Y-%m-%d").date()

            id_usuario = usuarios_repo.registrar_cliente(datos)

            session["usuario"] = {
                "id": id_usuario,
                "nombre": f"{datos['nombres']} {datos['apellidos']}".title(),
                "email": datos["email"].lower(),
                "rol": "CLIENTE",
                "descripcion_rol": "Huesped",
            }
            flash("Cuenta creada. Ya puedes reservar.", "success")
            return redirect(url_for("publico.home"))

        except ValueError:
            flash("Revisa el formato de la fecha de nacimiento.", "danger")
        except ErrorDominio as e:
            flash(str(e), "danger")

        return render_template("cuenta/registro.html", datos=datos)

    return render_template("cuenta/registro.html", datos={})


@bp.route("/logout")
def logout():
    session.pop("usuario", None)
    flash("Cerraste sesion correctamente.", "success")
    return redirect(url_for("publico.home"))


@bp.route("/reservas")
@requiere_sesion
def mis_reservas():
    usuario = session["usuario"]
    if usuario["rol"] != "CLIENTE":
        return redirect(url_for("admin.reservas"))

    reservas = reservas_repo.listar_de_cliente(usuario["id"])
    for r in reservas:
        r["habitaciones_detalle"] = reservas_repo.habitaciones_de(r["id_reserva"])

    return render_template("cuenta/mis_reservas.html", reservas=reservas)

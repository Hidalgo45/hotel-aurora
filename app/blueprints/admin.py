"""QUE HACE: el panel del personal: tablero, gestion de reservas,
inventario y reportes.

SI PREGUNTAN POR ESTE ARCHIVO:
"Cuando aqui se cambia el estado de una reserva, nosotros no tocamos las
habitaciones. Solo cambiamos la reserva, y la base de datos se encarga sola
de actualizar el inventario y de anotarlo en la bitacora."

Los reportes son exclusivos del administrador; recepcion no los ve.
"""
from __future__ import annotations

import csv
import io

from flask import (Blueprint, Response, flash, redirect, render_template,
                   request, url_for)

from . import requiere_rol
from ..dominio.excepciones import ErrorDominio
from ..repositorios import (HabitacionRepositorioPG, ReporteRepositorioPG,
                            ReservaRepositorioPG)

bp = Blueprint("admin", __name__, url_prefix="/admin")

habitaciones_repo = HabitacionRepositorioPG()
reservas_repo = ReservaRepositorioPG()
reportes_repo = ReporteRepositorioPG()


@bp.route("/")
@requiere_rol("ADMIN", "RECEPCION")
def dashboard():
    return render_template(
        "admin/dashboard.html",
        indicadores=reportes_repo.indicadores_hoy(),
        estado_hotel=reportes_repo.estado_hotel(),
        llegadas=reportes_repo.llegadas_proximas(7),
        bitacora=reservas_repo.bitacora_reciente(8),
    )


@bp.route("/reservas")
@requiere_rol("ADMIN", "RECEPCION")
def reservas():
    estado = request.args.get("estado") or None
    busqueda = request.args.get("q") or None
    return render_template(
        "admin/reservas.html",
        reservas=reservas_repo.listar(estado, busqueda),
        estado=estado, busqueda=busqueda or "",
    )


@bp.route("/reservas/<codigo>/estado", methods=["POST"])
@requiere_rol("ADMIN", "RECEPCION")
def cambiar_estado(codigo: str):
    """Check-in, check-out o confirmacion. Dispara el trigger de la base."""
    nuevo = request.form.get("estado", "")
    validos = {"CONFIRMADA", "CHECK_IN", "CHECK_OUT", "NO_SHOW"}

    if nuevo not in validos:
        flash("Ese cambio de estado no esta permitido.", "danger")
        return redirect(url_for("admin.reservas"))

    try:
        reservas_repo.cambiar_estado(codigo, nuevo)
        etiquetas = {
            "CONFIRMADA": "confirmada",
            "CHECK_IN": "con check-in registrado",
            "CHECK_OUT": "con check-out registrado",
            "NO_SHOW": "marcada como no presentada",
        }
        flash(f"Reserva {codigo} {etiquetas[nuevo]}. "
              f"El estado de las habitaciones se actualizo automaticamente.",
              "success")
    except ErrorDominio as e:
        flash(str(e), "danger")
    except Exception:                                          # noqa: BLE001
        flash("No se pudo cambiar el estado de la reserva. Intenta de nuevo.",
              "danger")

    return redirect(request.referrer or url_for("admin.reservas"))


@bp.route("/habitaciones")
@requiere_rol("ADMIN", "RECEPCION")
def habitaciones():
    return render_template(
        "admin/habitaciones.html",
        habitaciones=habitaciones_repo.listar_todas(),
        resumen=reportes_repo.estado_hotel(),
    )


@bp.route("/habitaciones/<int:id_habitacion>/estado", methods=["POST"])
@requiere_rol("ADMIN")
def estado_habitacion(id_habitacion: int):
    nuevo = request.form.get("estado", "")
    if nuevo not in {"DISPONIBLE", "LIMPIEZA", "MANTENIMIENTO"}:
        flash("Solo puedes marcar una habitacion como disponible, "
              "en limpieza o en mantenimiento.", "danger")
        return redirect(url_for("admin.habitaciones"))

    habitaciones_repo.cambiar_estado(id_habitacion, nuevo)
    flash("Estado de la habitacion actualizado.", "success")
    return redirect(url_for("admin.habitaciones"))


@bp.route("/reportes")
@requiere_rol("ADMIN")
def reportes():
    return render_template(
        "admin/reportes.html",
        ocupacion=reportes_repo.ocupacion(),
        clientes=reportes_repo.clientes(10),
        calidad=reportes_repo.calidad_datos(),
    )


@bp.route("/reportes/<nombre>.csv")
@requiere_rol("ADMIN")
def exportar(nombre: str):
    fuentes = {
        "ocupacion": reportes_repo.ocupacion,
        "clientes": lambda: reportes_repo.clientes(100),
    }
    if nombre not in fuentes:
        flash("Ese reporte no existe.", "warning")
        return redirect(url_for("admin.reportes"))

    filas = fuentes[nombre]()
    salida = io.StringIO()
    if filas:
        escritor = csv.DictWriter(salida, fieldnames=list(filas[0].keys()),
                                  delimiter=";")
        escritor.writeheader()
        escritor.writerows(filas)

    return Response(
        salida.getvalue().encode("utf-8-sig"),
        mimetype="text/csv",
        headers={"Content-Disposition":
                 f"attachment; filename=reporte_{nombre}.csv"},
    )

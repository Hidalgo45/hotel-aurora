"""Rutas publicas: inicio, catalogo, detalle, reserva y confirmacion."""
from __future__ import annotations

from datetime import date, datetime, timedelta
from decimal import Decimal

from flask import (Blueprint, current_app, flash, redirect, render_template,
                   request, session, url_for)

from . import requiere_sesion
from ..config import Config
from ..dominio import (FabricaHabitaciones, ReglaNegocioError, Reserva,
                       ValorInvalidoError)
from ..dominio.excepciones import ErrorDominio
from ..repositorios import HabitacionRepositorioPG, ReservaRepositorioPG
from ..servicios import ErrorCorreo, servicio_correo

bp = Blueprint("publico", __name__)

habitaciones_repo = HabitacionRepositorioPG()
reservas_repo = ReservaRepositorioPG()


def _enviar_comprobante(codigo: str) -> tuple[bool, str]:
    """Arma el comprobante de una reserva y lo entrega por correo.

    Devuelve (exito, detalle). Nunca deja escapar la excepcion: el correo es
    un aviso posterior a la reserva, y una falla de red no puede dejar al
    cliente creyendo que su reserva no quedo registrada.
    """
    reserva = reservas_repo.buscar_por_codigo(codigo)
    if not reserva:
        return False, f"No existe la reserva {codigo}."

    total = Decimal(reserva["total"]) + Decimal(reserva["servicios"])
    contexto = {
        "r": reserva,
        "habitaciones": reservas_repo.habitaciones_de(reserva["id_reserva"]),
        "servicios": reservas_repo.servicios_de(reserva["id_reserva"]),
        "total": total,
        "saldo": total - Decimal(reserva["pagado"]),
    }

    try:
        detalle = servicio_correo(Config).enviar_comprobante(
            reserva,
            render_template("correo/comprobante.html", **contexto),
            render_template("correo/comprobante.txt", **contexto),
        )
        current_app.logger.info("Comprobante %s: %s", codigo, detalle)
        return True, detalle
    except ErrorCorreo as e:
        current_app.logger.warning("Comprobante %s no entregado: %s", codigo, e)
        return False, str(e)


def _leer_fechas() -> tuple[date, date, int]:
    """Lee las fechas del formulario y aplica valores por defecto sensatos."""
    hoy = date.today()
    try:
        checkin = datetime.strptime(
            request.args.get("checkin", ""), "%Y-%m-%d").date()
    except ValueError:
        checkin = hoy + timedelta(days=1)
    try:
        checkout = datetime.strptime(
            request.args.get("checkout", ""), "%Y-%m-%d").date()
    except ValueError:
        checkout = checkin + timedelta(days=2)

    if checkout <= checkin:
        checkout = checkin + timedelta(days=1)

    try:
        huespedes = max(1, min(10, int(request.args.get("huespedes", 2))))
    except ValueError:
        huespedes = 2

    return checkin, checkout, huespedes


@bp.route("/")
def home():
    tipos = habitaciones_repo.listar_tipos()
    return render_template("publico/home.html", tipos=tipos)


@bp.route("/habitaciones")
def catalogo():
    checkin, checkout, huespedes = _leer_fechas()
    noches = (checkout - checkin).days

    if checkin < date.today():
        flash("Esa fecha ya paso. Te mostramos disponibilidad desde manana.",
              "warning")
        checkin = date.today() + timedelta(days=1)
        checkout = checkin + timedelta(days=noches or 1)

    filas = habitaciones_repo.buscar_disponibles(checkin, checkout, huespedes)

    # Se construyen objetos del dominio para calcular el precio de forma
    # polimorfica: cada tipo aplica su propia formula.
    disponibles = []
    for fila in filas:
        habitacion = FabricaHabitaciones.desde_fila(fila)
        disponibles.append({
            "datos": fila,
            "objeto": habitacion,
            "precio_total": habitacion.calcular_tarifa(noches),
            "servicios": habitacion.servicios_incluidos(),
        })

    return render_template(
        "publico/catalogo.html",
        disponibles=disponibles, checkin=checkin, checkout=checkout,
        huespedes=huespedes, noches=noches,
    )


@bp.route("/habitaciones/<int:id_habitacion>")
def detalle(id_habitacion: int):
    fila = habitaciones_repo.obtener(id_habitacion)
    if not fila:
        flash("Esa habitacion no existe o fue retirada del catalogo.", "warning")
        return redirect(url_for("publico.catalogo"))

    checkin, checkout, huespedes = _leer_fechas()
    noches = (checkout - checkin).days
    habitacion = FabricaHabitaciones.desde_fila(fila)

    return render_template(
        "publico/detalle.html",
        h=fila, objeto=habitacion, checkin=checkin, checkout=checkout,
        huespedes=huespedes, noches=noches,
        precio_total=habitacion.calcular_tarifa(noches),
        servicios_incluidos=habitacion.servicios_incluidos(),
        ocupadas=habitaciones_repo.fechas_ocupadas(id_habitacion),
        servicios_extra=habitaciones_repo.listar_servicios(),
    )


@bp.route("/reservar", methods=["POST"])
@requiere_sesion
def reservar():
    usuario = session["usuario"]

    if usuario["rol"] != "CLIENTE":
        flash("El personal del hotel crea reservas desde el panel de gestion.",
              "warning")
        return redirect(url_for("admin.reservas"))

    try:
        id_habitacion = int(request.form["id_habitacion"])
        checkin = datetime.strptime(request.form["checkin"], "%Y-%m-%d").date()
        checkout = datetime.strptime(request.form["checkout"], "%Y-%m-%d").date()
        adultos = int(request.form.get("adultos", 1))
        ninos = int(request.form.get("ninos", 0))
    except (KeyError, ValueError):
        flash("Revisa las fechas y el numero de huespedes antes de continuar.",
              "danger")
        return redirect(url_for("publico.catalogo"))

    servicios = [int(s) for s in request.form.getlist("servicios") if s.isdigit()]

    try:
        # ---- Capa 2: las reglas de negocio se validan en el dominio ----
        fila = habitaciones_repo.obtener(id_habitacion)
        if not fila:
            raise ReglaNegocioError("La habitacion seleccionada ya no existe.")

        reserva = Reserva(usuario, checkin, checkout, adultos, ninos)
        reserva.validar_fecha_inicio()
        reserva.agregar_habitacion(FabricaHabitaciones.desde_fila(fila))
        reserva.confirmar()          # valida capacidad contra los huespedes

        # ---- Capa 3: la base ejecuta el procedimiento almacenado ----
        codigo, total = reservas_repo.crear(
            usuario["id"], [id_habitacion], checkin, checkout, adultos, ninos)

        if servicios:
            detalle_reserva = reservas_repo.buscar_por_codigo(codigo)
            reservas_repo.agregar_servicios(
                detalle_reserva["id_reserva"],
                [(s, (checkout - checkin).days) for s in servicios])

        flash(f"Reserva {codigo} creada. Te esperamos el "
              f"{checkin.strftime('%d/%m/%Y')}.", "success")

        # El comprobante se envia despues de que la reserva ya esta guardada.
        # Si el correo falla, se avisa pero la reserva se mantiene.
        enviado, detalle = _enviar_comprobante(codigo)
        if enviado:
            flash(f"Te enviamos el comprobante a {usuario['email']}.", "info")
        else:
            flash(f"Tu reserva esta confirmada, pero no pudimos enviarte el "
                  f"comprobante por correo ({detalle}). Guarda el codigo "
                  f"{codigo} o pide que te lo reenviemos.", "warning")

        return redirect(url_for("publico.confirmacion", codigo=codigo))

    except ErrorDominio as e:
        flash(str(e), "danger")
        return redirect(url_for("publico.detalle", id_habitacion=id_habitacion,
                                checkin=checkin, checkout=checkout,
                                huespedes=adultos + ninos))


@bp.route("/reservas/<codigo>/comprobante", methods=["POST"])
@requiere_sesion
def reenviar_comprobante(codigo: str):
    """Vuelve a enviar el comprobante de una reserva ya existente."""
    reserva = reservas_repo.buscar_por_codigo(codigo)
    if not reserva:
        flash(f"No encontramos ninguna reserva con el codigo {codigo}.",
              "warning")
        return redirect(url_for("publico.home"))

    usuario = session["usuario"]
    if usuario["rol"] == "CLIENTE" and reserva["id_cliente"] != usuario["id"]:
        flash("Solo puedes pedir el comprobante de tus propias reservas.",
              "danger")
        return redirect(url_for("cuenta.mis_reservas"))

    enviado, detalle = _enviar_comprobante(codigo)
    if enviado:
        flash(f"Comprobante reenviado a {reserva['email']}.", "success")
    else:
        flash(f"No pudimos reenviar el comprobante: {detalle}", "danger")

    return redirect(url_for("publico.confirmacion", codigo=codigo))


@bp.route("/reservas/<codigo>")
def confirmacion(codigo: str):
    reserva = reservas_repo.buscar_por_codigo(codigo)
    if not reserva:
        flash(f"No encontramos ninguna reserva con el codigo {codigo}.", "warning")
        return redirect(url_for("publico.home"))

    # reserva["total"] guarda solo el alojamiento: el procedimiento almacenado
    # lo calcula al crear la reserva, y los servicios se agregan despues. El
    # total que ve el cliente debe incluir ambos, igual que el comprobante que
    # se envia por correo.
    alojamiento = Decimal(reserva["total"])
    servicios_usd = Decimal(reserva["servicios"])
    total = alojamiento + servicios_usd

    return render_template(
        "publico/confirmacion.html",
        r=reserva,
        habitaciones=reservas_repo.habitaciones_de(reserva["id_reserva"]),
        servicios=reservas_repo.servicios_de(reserva["id_reserva"]),
        alojamiento=alojamiento,
        servicios_usd=servicios_usd,
        total=total,
        saldo=total - Decimal(reserva["pagado"]),
    )


@bp.route("/reservas/<codigo>/cancelar", methods=["POST"])
@requiere_sesion
def cancelar(codigo: str):
    motivo = request.form.get("motivo", "Cancelada por el huesped").strip()
    try:
        penalidad = reservas_repo.cancelar(codigo, motivo or "Sin motivo indicado")
        if penalidad > 0:
            flash(f"Reserva {codigo} cancelada. Se aplico un cargo de "
                  f"${penalidad} por cancelar con menos de 48 horas.", "warning")
        else:
            flash(f"Reserva {codigo} cancelada sin cargo. "
                  f"Esperamos recibirte pronto.", "success")
    except ErrorDominio as e:
        flash(str(e), "danger")

    destino = ("cuenta.mis_reservas"
               if session["usuario"]["rol"] == "CLIENTE" else "admin.reservas")
    return redirect(url_for(destino))

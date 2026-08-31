"""Reservas sobre PostgreSQL.

Las operaciones criticas no se arman con SQL suelto: se delegan a los
procedimientos almacenados, que las ejecutan dentro de una sola transaccion.
"""
from __future__ import annotations

from datetime import date
from decimal import Decimal

from psycopg import errors

from .. import db
from ..dominio.excepciones import ReglaNegocioError
from .base import RepositorioReservas


def _mensaje_limpio(error: Exception) -> str:
    """Deja solo la primera linea del mensaje que levanto PostgreSQL."""
    texto = str(error).split("\n")[0].strip()
    # Quita el prefijo de codigo interno: "RES-004: ..." -> "..."
    if ":" in texto and texto.split(":")[0].strip().isupper():
        texto = texto.split(":", 1)[1].strip()
    return texto or "No se pudo completar la operacion."


class ReservaRepositorioPG(RepositorioReservas):

    # ------------------------------------------------------------------
    # Operacion critica: delegada al procedimiento almacenado
    # ------------------------------------------------------------------
    def crear(self, id_cliente: int, habitaciones: list[int], checkin: date,
              checkout: date, adultos: int, ninos: int) -> tuple[str, Decimal]:
        try:
            with db.obtener_conexion() as conn:
                fila = conn.execute(
                    "CALL sp_crear_reserva(%s, %s, %s, %s, %s, %s, NULL, NULL)",
                    (id_cliente, habitaciones, checkin, checkout, adultos, ninos),
                ).fetchone()
            return fila["p_codigo"], Decimal(fila["p_total"])

        except errors.ExclusionViolation:
            raise ReglaNegocioError(
                "Una de las habitaciones acaba de ser reservada por otra persona. "
                "Vuelve a buscar disponibilidad para esas fechas."
            ) from None
        except errors.RaiseException as e:
            raise ReglaNegocioError(_mensaje_limpio(e)) from None

    def cancelar(self, codigo: str, motivo: str) -> Decimal:
        try:
            with db.obtener_conexion() as conn:
                fila = conn.execute(
                    "CALL sp_cancelar_reserva(%s, %s, NULL)", (codigo, motivo)
                ).fetchone()
            return Decimal(fila["p_penalidad"])
        except errors.RaiseException as e:
            raise ReglaNegocioError(_mensaje_limpio(e)) from None

    def registrar_pago(self, codigo: str, monto: Decimal,
                       metodo: str = "TARJETA") -> Decimal:
        try:
            with db.obtener_conexion() as conn:
                fila = conn.execute(
                    "CALL sp_registrar_pago(%s, %s, %s::metodo_pago, NULL)",
                    (codigo, monto, metodo),
                ).fetchone()
            return Decimal(fila["p_saldo"])
        except errors.RaiseException as e:
            raise ReglaNegocioError(_mensaje_limpio(e)) from None

    # ------------------------------------------------------------------
    # Consultas
    # ------------------------------------------------------------------
    _DETALLE = """
        SELECT r.*,
               u.nombres || ' ' || u.apellidos AS cliente,
               u.email, u.telefono, u.cedula,
               (r.fecha_checkout - r.fecha_checkin) AS noches,
               COALESCE((SELECT SUM(p.monto) FROM pago p
                          WHERE p.id_reserva = r.id_reserva), 0) AS pagado,
               COALESCE((SELECT SUM(rs.cantidad * rs.precio_unitario)
                           FROM reserva_servicio rs
                          WHERE rs.id_reserva = r.id_reserva), 0) AS servicios
          FROM reserva r
          JOIN usuario u ON u.id_usuario = r.id_cliente
    """

    def buscar_por_codigo(self, codigo: str) -> dict | None:
        return db.consultar_uno(
            self._DETALLE + " WHERE r.codigo = %s", (codigo,))

    def habitaciones_de(self, id_reserva: int) -> list[dict]:
        return db.consultar("""
            SELECT h.numero, h.piso, th.nombre AS tipo, th.codigo,
                   rh.subtotal, rh.anulado,
                   lower(rh.estadia) AS desde, upper(rh.estadia) AS hasta
              FROM reserva_habitacion rh
              JOIN habitacion h ON h.id_habitacion = rh.id_habitacion
              JOIN tipo_habitacion th ON th.id_tipo = h.id_tipo
             WHERE rh.id_reserva = %s
             ORDER BY h.numero
        """, (id_reserva,))

    def servicios_de(self, id_reserva: int) -> list[dict]:
        return db.consultar("""
            SELECT s.nombre, s.modo_cobro, rs.cantidad, rs.precio_unitario,
                   (rs.cantidad * rs.precio_unitario) AS subtotal
              FROM reserva_servicio rs
              JOIN servicio s ON s.id_servicio = rs.id_servicio
             WHERE rs.id_reserva = %s
             ORDER BY s.nombre
        """, (id_reserva,))

    def listar_de_cliente(self, id_cliente: int) -> list[dict]:
        return db.consultar(
            self._DETALLE + """
             WHERE r.id_cliente = %s
             ORDER BY r.fecha_checkin DESC
        """, (id_cliente,))

    def listar(self, estado: str | None = None,
               busqueda: str | None = None) -> list[dict]:
        sql = self._DETALLE + " WHERE 1 = 1"
        params: list = []
        if estado:
            sql += " AND r.estado = %s::estado_reserva"
            params.append(estado)
        if busqueda:
            sql += (" AND (r.codigo ILIKE %s OR u.nombres ILIKE %s"
                    " OR u.apellidos ILIKE %s OR u.cedula ILIKE %s)")
            patron = f"%{busqueda}%"
            params.extend([patron] * 4)
        sql += " ORDER BY r.fecha_checkin DESC LIMIT 200"
        return db.consultar(sql, tuple(params))

    def cambiar_estado(self, codigo: str, nuevo_estado: str) -> None:
        """Dispara el trigger que sincroniza el estado de las habitaciones."""
        db.ejecutar("""
            UPDATE reserva SET estado = %s::estado_reserva WHERE codigo = %s
        """, (nuevo_estado, codigo))

    def agregar_servicios(self, id_reserva: int,
                          servicios: list[tuple[int, int]]) -> None:
        """servicios: lista de (id_servicio, cantidad)."""
        if not servicios:
            return
        with db.obtener_conexion() as conn:
            for id_servicio, cantidad in servicios:
                conn.execute("""
                    INSERT INTO reserva_servicio
                           (id_reserva, id_servicio, cantidad, precio_unitario)
                    SELECT %s, s.id_servicio, %s, s.precio
                      FROM servicio s WHERE s.id_servicio = %s
                    ON CONFLICT (id_reserva, id_servicio) DO NOTHING
                """, (id_reserva, cantidad, id_servicio))
            conn.execute("""
                UPDATE reserva r
                   SET total = (SELECT COALESCE(SUM(rh.subtotal), 0)
                                  FROM reserva_habitacion rh
                                 WHERE rh.id_reserva = r.id_reserva
                                   AND rh.anulado = FALSE)
                             + (SELECT COALESCE(SUM(rs.cantidad * rs.precio_unitario), 0)
                                  FROM reserva_servicio rs
                                 WHERE rs.id_reserva = r.id_reserva)
                 WHERE r.id_reserva = %s
            """, (id_reserva,))

    def bitacora_reciente(self, limite: int = 15) -> list[dict]:
        return db.consultar("""
            SELECT b.ocurrido_en, h.numero, b.estado_anterior, b.estado_nuevo,
                   r.codigo, b.usuario_bd
              FROM bitacora_habitacion b
              JOIN habitacion h ON h.id_habitacion = b.id_habitacion
              LEFT JOIN reserva r ON r.id_reserva = b.id_reserva
             ORDER BY b.ocurrido_en DESC
             LIMIT %s
        """, (limite,))

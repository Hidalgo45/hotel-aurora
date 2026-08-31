"""Consultas de inventario y disponibilidad sobre PostgreSQL."""
from __future__ import annotations

from datetime import date

from .. import db
from .base import RepositorioHabitaciones


class HabitacionRepositorioPG(RepositorioHabitaciones):

    _CAMPOS = """
        h.id_habitacion, h.numero, h.piso, h.estado, h.activa,
        th.id_tipo, th.codigo, th.nombre AS tipo, th.descripcion,
        th.capacidad_max, th.tarifa_base, th.imagen
    """

    def listar_tipos(self) -> list[dict]:
        return db.consultar("""
            SELECT th.*, COUNT(h.id_habitacion) AS unidades,
                   COUNT(*) FILTER (WHERE h.estado = 'DISPONIBLE') AS libres_ahora
              FROM tipo_habitacion th
              LEFT JOIN habitacion h ON h.id_tipo = th.id_tipo AND h.activa
             GROUP BY th.id_tipo
             ORDER BY th.tarifa_base
        """)

    def buscar_disponibles(self, checkin: date, checkout: date,
                           huespedes: int = 1) -> list[dict]:
        """Habitaciones sin ninguna estadia que se cruce con el rango pedido.

        El operador && de PostgreSQL compara los dos rangos de fechas; el
        indice GiST sobre la columna estadia hace que la consulta sea rapida.
        """
        return db.consultar(f"""
            SELECT {self._CAMPOS}
              FROM habitacion h
              JOIN tipo_habitacion th ON th.id_tipo = h.id_tipo
             WHERE h.activa = TRUE
               AND h.estado <> 'MANTENIMIENTO'
               AND th.capacidad_max >= %s
               AND NOT EXISTS (
                     SELECT 1
                       FROM reserva_habitacion rh
                       JOIN reserva r ON r.id_reserva = rh.id_reserva
                      WHERE rh.id_habitacion = h.id_habitacion
                        AND rh.anulado = FALSE
                        AND r.estado NOT IN ('CANCELADA', 'NO_SHOW')
                        AND rh.estadia && daterange(%s, %s, '[)')
                   )
             ORDER BY th.tarifa_base, h.numero
        """, (huespedes, checkin, checkout))

    def obtener(self, id_habitacion: int) -> dict | None:
        return db.consultar_uno(f"""
            SELECT {self._CAMPOS}
              FROM habitacion h
              JOIN tipo_habitacion th ON th.id_tipo = h.id_tipo
             WHERE h.id_habitacion = %s
        """, (id_habitacion,))

    def listar_todas(self) -> list[dict]:
        return db.consultar(f"""
            SELECT {self._CAMPOS}
              FROM habitacion h
              JOIN tipo_habitacion th ON th.id_tipo = h.id_tipo
             ORDER BY h.numero
        """)

    def fechas_ocupadas(self, id_habitacion: int) -> list[dict]:
        """Rangos ya tomados, para pintar el calendario del detalle."""
        return db.consultar("""
            SELECT lower(rh.estadia) AS desde, upper(rh.estadia) AS hasta
              FROM reserva_habitacion rh
              JOIN reserva r ON r.id_reserva = rh.id_reserva
             WHERE rh.id_habitacion = %s
               AND rh.anulado = FALSE
               AND r.estado NOT IN ('CANCELADA', 'NO_SHOW')
               AND upper(rh.estadia) >= CURRENT_DATE
             ORDER BY desde
        """, (id_habitacion,))

    def cambiar_estado(self, id_habitacion: int, estado: str) -> None:
        db.ejecutar("""
            UPDATE habitacion SET estado = %s::estado_habitacion
             WHERE id_habitacion = %s
        """, (estado, id_habitacion))

    def listar_servicios(self) -> list[dict]:
        return db.consultar(
            "SELECT * FROM servicio WHERE activo ORDER BY modo_cobro, nombre")

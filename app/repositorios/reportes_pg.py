"""Reportes gerenciales.

Las consultas complejas viven en la base como vistas (database/05_reportes.sql);
aqui solo se las invoca. Asi el mismo SQL sirve en pgAdmin y en la aplicacion.
"""
from __future__ import annotations

from .. import db


class ReporteRepositorioPG:

    def ocupacion(self) -> list[dict]:
        """Reporte 1: ocupacion e ingresos por tipo de habitacion y mes."""
        return db.consultar("SELECT * FROM v_reporte_ocupacion")

    def clientes(self, limite: int = 10) -> list[dict]:
        """Reporte 2: ranking de clientes por valor total generado."""
        return db.consultar(
            "SELECT * FROM v_reporte_clientes LIMIT %s", (limite,))

    def estado_hotel(self) -> list[dict]:
        return db.consultar("SELECT * FROM v_estado_hotel")

    def calidad_datos(self) -> list[dict]:
        return db.consultar("SELECT * FROM v_calidad_datos")

    def indicadores_hoy(self) -> dict:
        """Cifras del tablero principal."""
        return db.consultar_uno("""
            SELECT
              (SELECT COUNT(*) FROM habitacion WHERE activa) AS habitaciones,
              (SELECT COUNT(*) FROM habitacion
                WHERE estado = 'OCUPADA')                    AS ocupadas_hoy,
              (SELECT COUNT(*) FROM reserva
                WHERE fecha_checkin = CURRENT_DATE
                  AND estado IN ('CONFIRMADA','CHECK_IN'))   AS entradas_hoy,
              (SELECT COUNT(*) FROM reserva
                WHERE fecha_checkout = CURRENT_DATE
                  AND estado IN ('CHECK_IN','CHECK_OUT'))    AS salidas_hoy,
              (SELECT COALESCE(SUM(p.monto), 0) FROM pago p
                WHERE date_trunc('month', p.fecha)
                      = date_trunc('month', CURRENT_DATE))   AS ingresos_mes,
              (SELECT COUNT(*) FROM reserva
                WHERE estado = 'CONFIRMADA'
                  AND fecha_checkin > CURRENT_DATE)          AS reservas_futuras
        """)

    def llegadas_proximas(self, dias: int = 7) -> list[dict]:
        return db.consultar("""
            SELECT r.codigo, r.fecha_checkin, r.fecha_checkout, r.estado,
                   u.nombres || ' ' || u.apellidos AS cliente,
                   string_agg(h.numero, ', ' ORDER BY h.numero) AS habitaciones,
                   r.total
              FROM reserva r
              JOIN usuario u ON u.id_usuario = r.id_cliente
              LEFT JOIN reserva_habitacion rh
                     ON rh.id_reserva = r.id_reserva AND rh.anulado = FALSE
              LEFT JOIN habitacion h ON h.id_habitacion = rh.id_habitacion
             WHERE r.fecha_checkin BETWEEN CURRENT_DATE AND CURRENT_DATE + %s
               AND r.estado IN ('CONFIRMADA', 'PENDIENTE')
             GROUP BY r.id_reserva, u.nombres, u.apellidos
             ORDER BY r.fecha_checkin
        """, (dias,))

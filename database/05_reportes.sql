-- QUE HACE: guarda las dos consultas de los reportes con un nombre, para
-- poder llamarlas facil desde el programa.
--
-- SI PREGUNTAN POR ESTE ARCHIVO:
-- "El reporte de ocupacion cruza cuatro tablas. Lo ingenioso es que convierte
--  cada estadia en noches sueltas (una reserva del 10 al 14 se vuelve cuatro
--  filas) para poder contarlas por mes, y despues las compara con las noches
--  que habia disponibles."
--
-- El segundo reporte suma por cliente todo lo que ha gastado en alojamiento y
-- servicios, y calcula si quedo debiendo algo.

-- ============================================================================
--  HOTEL AURORA  ·  05_reportes.sql
--  Criterio 1.4: dos reportes relevantes con consultas complejas que integran
--  multiples tablas.  Se exponen tambien en /admin/reportes de la aplicacion.
-- ============================================================================

-- ============================================================================
-- REPORTE 1  ·  OCUPACION E INGRESOS POR TIPO DE HABITACION Y MES
-- ----------------------------------------------------------------------------
--  Pregunta que responde: que tipo de habitacion rinde mas y en que mes.
--  Tecnicas: 2 CTE, CROSS JOIN LATERAL, generate_series, LEFT JOIN,
--            agregacion, calculo de porcentaje de ocupacion y tarifa media.
--  Tablas:   reserva_habitacion, reserva, habitacion, tipo_habitacion.
-- ============================================================================
CREATE OR REPLACE VIEW v_reporte_ocupacion AS
WITH noches_vendidas AS (
    SELECT th.nombre                        AS tipo,
           date_trunc('month', d.dia)::date AS mes,
           COUNT(*)                         AS noches,
           SUM(rh.subtotal / GREATEST(upper(rh.estadia) - lower(rh.estadia), 1))
                                            AS ingresos
      FROM reserva_habitacion rh
      JOIN reserva          r  ON r.id_reserva    = rh.id_reserva
      JOIN habitacion       h  ON h.id_habitacion = rh.id_habitacion
      JOIN tipo_habitacion  th ON th.id_tipo      = h.id_tipo
      CROSS JOIN LATERAL generate_series(lower(rh.estadia),
                                         upper(rh.estadia) - 1,
                                         INTERVAL '1 day') AS d(dia)
     WHERE rh.anulado = FALSE
       AND r.estado IN ('CONFIRMADA', 'CHECK_IN', 'CHECK_OUT')
     GROUP BY th.nombre, 2
),
inventario AS (
    SELECT th.nombre    AS tipo,
           m.mes::date  AS mes,
           COUNT(h.id_habitacion) *
           EXTRACT(DAY FROM (m.mes + INTERVAL '1 month - 1 day'))::int
               AS noches_disponibles
      FROM tipo_habitacion th
      JOIN habitacion h ON h.id_tipo = th.id_tipo AND h.activa
      CROSS JOIN generate_series(
                   date_trunc('month', CURRENT_DATE - INTERVAL '3 months'),
                   date_trunc('month', CURRENT_DATE + INTERVAL '2 months'),
                   INTERVAL '1 month') AS m(mes)
     -- Se agrupa por m.mes y no por su posicion: EXTRACT usa la columna sin
     -- castear, y al agrupar por m.mes::date PostgreSQL no la reconoce como
     -- agrupada y rechaza la consulta.
     GROUP BY th.nombre, m.mes
)
SELECT i.tipo,
       to_char(i.mes, 'YYYY-MM')                           AS periodo,
       i.noches_disponibles,
       COALESCE(nv.noches, 0)                              AS noches_vendidas,
       ROUND(100.0 * COALESCE(nv.noches, 0)
             / NULLIF(i.noches_disponibles, 0), 2)         AS ocupacion_pct,
       ROUND(COALESCE(nv.ingresos, 0), 2)                  AS ingresos_usd,
       ROUND(COALESCE(nv.ingresos, 0)
             / NULLIF(nv.noches, 0), 2)                    AS tarifa_promedio
  FROM inventario i
  LEFT JOIN noches_vendidas nv
         ON nv.tipo = i.tipo AND nv.mes = i.mes
 ORDER BY i.mes DESC, ocupacion_pct DESC NULLS LAST;


-- ============================================================================
-- REPORTE 2  ·  RANKING DE CLIENTES POR VALOR TOTAL GENERADO
-- ----------------------------------------------------------------------------
--  Pregunta que responde: quienes son los huespedes mas valiosos y cuanto
--  deben todavia.
--  Tecnicas: CTE, subconsultas correlacionadas, funcion de ventana RANK(),
--            GROUP BY, HAVING, calculo de saldo pendiente.
--  Tablas:   reserva, reserva_habitacion, reserva_servicio, pago,
--            cliente, usuario.
-- ============================================================================
CREATE OR REPLACE VIEW v_reporte_clientes AS
WITH base AS (
    SELECT r.id_reserva,
           r.id_cliente,
           r.total AS valor_alojamiento,
           (SELECT COALESCE(SUM(upper(rh.estadia) - lower(rh.estadia)), 0)
              FROM reserva_habitacion rh
             WHERE rh.id_reserva = r.id_reserva
               AND rh.anulado = FALSE)                    AS noches,
           (SELECT COALESCE(SUM(rs.cantidad * rs.precio_unitario), 0)
              FROM reserva_servicio rs
             WHERE rs.id_reserva = r.id_reserva)          AS consumo_servicios,
           (SELECT COALESCE(SUM(p.monto), 0)
              FROM pago p
             WHERE p.id_reserva = r.id_reserva)           AS pagado
      FROM reserva r
     WHERE r.estado IN ('CONFIRMADA', 'CHECK_IN', 'CHECK_OUT')
)
SELECT RANK() OVER (ORDER BY SUM(b.valor_alojamiento + b.consumo_servicios) DESC)
                                                          AS ranking,
       u.cedula,
       u.nombres || ' ' || u.apellidos                    AS cliente,
       u.email,
       COALESCE(c.ciudad, 'No registrada')                AS ciudad,
       COUNT(DISTINCT b.id_reserva)                       AS reservas,
       SUM(b.noches)                                      AS noches_totales,
       ROUND(SUM(b.valor_alojamiento), 2)                 AS alojamiento_usd,
       ROUND(SUM(b.consumo_servicios), 2)                 AS servicios_usd,
       ROUND(SUM(b.valor_alojamiento + b.consumo_servicios), 2) AS valor_total,
       ROUND(AVG(b.valor_alojamiento + b.consumo_servicios), 2) AS ticket_promedio,
       ROUND(SUM(b.valor_alojamiento + b.consumo_servicios - b.pagado), 2)
                                                          AS saldo_pendiente
  FROM base b
  JOIN cliente c ON c.id_cliente = b.id_cliente
  JOIN usuario u ON u.id_usuario = c.id_cliente
 GROUP BY u.cedula, u.nombres, u.apellidos, u.email, c.ciudad
HAVING SUM(b.valor_alojamiento + b.consumo_servicios) > 0
 ORDER BY valor_total DESC;


-- ============================================================================
-- REPORTE 3 (apoyo)  ·  Estado actual del hotel, usado por el dashboard
-- ============================================================================
CREATE OR REPLACE VIEW v_estado_hotel AS
SELECT th.nombre                                          AS tipo,
       COUNT(*)                                           AS total,
       COUNT(*) FILTER (WHERE h.estado = 'DISPONIBLE')    AS disponibles,
       COUNT(*) FILTER (WHERE h.estado = 'RESERVADA')     AS reservadas,
       COUNT(*) FILTER (WHERE h.estado = 'OCUPADA')       AS ocupadas,
       COUNT(*) FILTER (WHERE h.estado = 'LIMPIEZA')      AS limpieza,
       COUNT(*) FILTER (WHERE h.estado = 'MANTENIMIENTO') AS mantenimiento
  FROM habitacion h
  JOIN tipo_habitacion th ON th.id_tipo = h.id_tipo
 WHERE h.activa
 GROUP BY th.nombre
 ORDER BY th.nombre;


-- ============================================================================
-- Consultas de uso:
--   SELECT * FROM v_reporte_ocupacion;
--   SELECT * FROM v_reporte_clientes LIMIT 10;
--   SELECT * FROM v_estado_hotel;
-- ============================================================================

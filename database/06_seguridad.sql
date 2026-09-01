-- QUE HACE: define quien puede hacer que dentro de la base de datos.
--
-- SI PREGUNTAN POR ESTE ARCHIVO:
-- "Creamos tres usuarios distintos con permisos distintos. El que usa la
--  aplicacion ni siquiera puede borrar filas: cancelar una reserva no la
--  elimina, le cambia el estado. Asi el historial queda completo y los
--  reportes siguen siendo correctos."
--
-- Incluye tambien consultas para revisar la calidad de los datos: detectan
-- cosas que no deberian pasar, como una habitacion marcada como ocupada sin
-- ninguna reserva activa.

-- ============================================================================
--  HOTEL AURORA  ·  06_seguridad.sql
--  Criterio 1.5: control de acceso a los datos, calidad de la informacion
--  y estrategia de respaldo.
-- ============================================================================

-- ----------------------------------------------------------------------------
-- 1. ROLES CON PRIVILEGIO MINIMO
--    Cambiar las contrasenas antes de cualquier uso real.
-- ----------------------------------------------------------------------------
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'hotel_app') THEN
        CREATE ROLE hotel_app LOGIN PASSWORD 'cambiar_esta_clave';
    END IF;
    IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'hotel_reporte') THEN
        CREATE ROLE hotel_reporte LOGIN PASSWORD 'cambiar_esta_clave';
    END IF;
END $$;

-- Nadie tiene acceso por defecto
REVOKE ALL ON SCHEMA public FROM PUBLIC;

GRANT USAGE ON SCHEMA public TO hotel_app, hotel_reporte;

-- ---- Rol de la aplicacion web (Flask) --------------------------------------
-- Puede leer, insertar y actualizar, pero NO borrar: cancelar una reserva es
-- un cambio de estado, nunca un DELETE. Asi la historia nunca se pierde.
GRANT SELECT, INSERT, UPDATE ON ALL TABLES    IN SCHEMA public TO hotel_app;
GRANT USAGE, SELECT           ON ALL SEQUENCES IN SCHEMA public TO hotel_app;
GRANT EXECUTE                 ON ALL ROUTINES  IN SCHEMA public TO hotel_app;
REVOKE DELETE, TRUNCATE       ON ALL TABLES    IN SCHEMA public FROM hotel_app;

-- ---- Rol de solo lectura para gerencia -------------------------------------
-- Solo ve los reportes agregados, nunca la tabla de usuarios ni los hashes.
GRANT SELECT ON v_reporte_ocupacion, v_reporte_clientes, v_estado_hotel
      TO hotel_reporte;

-- ----------------------------------------------------------------------------
-- 2. SEGURIDAD A NIVEL DE FILA (RLS)
--    Un cliente solo puede ver sus propias reservas, aunque la consulta
--    llegue sin filtro desde la aplicacion.
-- ----------------------------------------------------------------------------
ALTER TABLE reserva ENABLE ROW LEVEL SECURITY;

DROP POLICY IF EXISTS pol_reserva_propia ON reserva;
CREATE POLICY pol_reserva_propia ON reserva
    FOR SELECT
    TO hotel_app
    USING (
        current_setting('app.rol', TRUE) IN ('ADMIN', 'RECEPCION')
        OR id_cliente = NULLIF(current_setting('app.id_cliente', TRUE), '')::int
    );

-- La aplicacion declara quien esta conectado al inicio de cada peticion:
--   SET LOCAL app.rol = 'CLIENTE';
--   SET LOCAL app.id_cliente = '7';

-- ----------------------------------------------------------------------------
-- 3. CALIDAD DE DATOS  ·  auditoria que se ejecuta cada semana
--    Si alguna fila devuelve un conteo mayor que cero, hay una inconsistencia
--    que debe corregirse.
-- ----------------------------------------------------------------------------
CREATE OR REPLACE VIEW v_calidad_datos AS
SELECT 'Reservas confirmadas sin habitacion asignada' AS incidencia,
       COUNT(*) AS casos
  FROM reserva r
 WHERE r.estado = 'CONFIRMADA'
   AND NOT EXISTS (SELECT 1 FROM reserva_habitacion rh
                    WHERE rh.id_reserva = r.id_reserva AND rh.anulado = FALSE)
UNION ALL
SELECT 'Habitaciones OCUPADA sin reserva en check-in',
       COUNT(*)
  FROM habitacion h
 WHERE h.estado = 'OCUPADA'
   AND NOT EXISTS (SELECT 1
                     FROM reserva_habitacion rh
                     JOIN reserva r ON r.id_reserva = rh.id_reserva
                    WHERE rh.id_habitacion = h.id_habitacion
                      AND rh.anulado = FALSE
                      AND r.estado = 'CHECK_IN')
UNION ALL
SELECT 'Reservas con pagos por encima del total',
       COUNT(*)
  FROM reserva r
 WHERE (SELECT COALESCE(SUM(monto), 0) FROM pago WHERE id_reserva = r.id_reserva)
       > r.total
UNION ALL
SELECT 'Clientes sin correo valido',
       COUNT(*)
  FROM usuario
 WHERE email !~* '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$'
UNION ALL
SELECT 'Reservas con total en cero',
       COUNT(*)
  FROM reserva
 WHERE total = 0 AND estado <> 'CANCELADA';

-- ----------------------------------------------------------------------------
-- 4. ESTRATEGIA DE RESPALDO
-- ----------------------------------------------------------------------------
--  Respaldo completo diario (formato custom: comprimido y restaurable por tabla)
--
--    pg_dump -U postgres -d hotel_aurora --format=custom --compress=9 ^
--            --file=C:\respaldos\aurora_%date%.dump
--
--  Solo el esquema, para versionarlo junto al codigo:
--
--    pg_dump -U postgres -d hotel_aurora --schema-only ^
--            --file=C:\respaldos\esquema.sql
--
--  Restauracion (PROBARLA, no solo escribirla):
--
--    createdb -U postgres aurora_prueba
--    pg_restore -U postgres -d aurora_prueba --clean C:\respaldos\aurora.dump
--
--  Politica de retencion 3-2-1:
--    · 7 respaldos diarios  · 4 semanales  · 12 mensuales
--    · 2 medios distintos (disco local + nube)
--    · 1 copia fuera del equipo
--    · Prueba de restauracion documentada una vez al mes
-- ----------------------------------------------------------------------------

-- ----------------------------------------------------------------------------
-- 5. RESUMEN DE MEDIDAS (para la sustentacion)
-- ----------------------------------------------------------------------------
--  Amenaza                        Medida implementada
--  -----------------------------  ------------------------------------------
--  Inyeccion SQL                  Consultas parametrizadas en psycopg
--  Fuga de contrasenas            Hash scrypt + trigger que bloquea texto plano
--  Escalada de privilegios        Tres roles; la app no es superusuario
--  Borrado accidental             REVOKE DELETE; cancelacion = cambio de estado
--  Acceso a datos ajenos          Row Level Security sobre reserva
--  Cambios sin responsable        bitacora_habitacion con current_user y fecha
--  Perdida del servidor           pg_dump diario + restauracion probada
-- ----------------------------------------------------------------------------

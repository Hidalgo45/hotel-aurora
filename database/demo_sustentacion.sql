-- ============================================================================
--  CONSULTAS PARA LA SUSTENTACION
--
--  Abre este archivo en pgAdmin ANTES de entrar al aula.
--  Son cuatro bloques. Ejecutas uno a la vez, en orden, seleccionando el
--  bloque con el mouse y presionando F5.
--
--  Comprobado el 01/09/2026: la secuencia completa funciona.
-- ============================================================================


-- ============================================================================
--  CONSULTA A  ·  El estado de las habitaciones
--  Ejecutala ANTES de empezar y deja el resultado a la vista.
--  Vas a volver a ella despues de confirmar la reserva.
-- ============================================================================

SELECT numero, estado
  FROM habitacion
 WHERE numero IN ('101', '102', '103')
 ORDER BY numero;

-- Debe mostrar las tres en DISPONIBLE.


-- ============================================================================
--  PASO 1  ·  Crear una reserva para la habitacion 101
--  Del 10 al 14 de mayo, para el cliente 4 (Carolina Naranjo), 2 adultos.
-- ============================================================================

CALL sp_crear_reserva(4, ARRAY[1], DATE '2027-05-10', DATE '2027-05-14',
                      2::smallint, 0::smallint);

-- Devuelve el codigo de la reserva y el total. Anota el codigo: lo necesitas
-- en el paso siguiente.


-- ============================================================================
--  PASO 2  ·  Confirmar la reserva
--  Aqui es donde se despierta el disparador.
--  Reemplaza el codigo por el que te devolvio el paso anterior.
-- ============================================================================

UPDATE reserva
   SET estado = 'CONFIRMADA'
 WHERE codigo = 'RSV-AQUI-EL-CODIGO';

-- Ahora vuelve a ejecutar la CONSULTA A.
-- La habitacion 101 paso de DISPONIBLE a RESERVADA sola.
--
-- Y para mostrar que quedo anotado:

SELECT b.ocurrido_en, h.numero, b.estado_anterior, b.estado_nuevo, b.usuario_bd
  FROM bitacora_habitacion b
  JOIN habitacion h ON h.id_habitacion = b.id_habitacion
 ORDER BY b.id_bitacora DESC
 LIMIT 3;


-- ============================================================================
--  CONSULTA B  ·  EL MOMENTO IMPORTANTE
--  Intento de vender la misma habitacion en fechas que se cruzan.
--  La 101 ya esta ocupada del 10 al 14; esta pide del 12 al 16.
--
--  DEJALA ESCRITA PERO SIN EJECUTAR hasta ese momento de la exposicion.
-- ============================================================================

CALL sp_crear_reserva(5, ARRAY[1], DATE '2027-05-12', DATE '2027-05-16',
                      1::smallint, 0::smallint);

-- PostgreSQL responde:
--   RES-006: una de las habitaciones seleccionadas ya esta reservada
--            en esas fechas
--
-- Aqui es donde haces dos segundos de silencio.


-- ============================================================================
--  DEJAR TODO COMO ESTABA  ·  Ejecutalo despues de la demostracion
--  Reemplaza el codigo por el de la reserva que creaste.
-- ============================================================================

-- 1. La reserva vuelve a pendiente y se anula su detalle
UPDATE reserva_habitacion
   SET anulado = TRUE
 WHERE id_reserva = (SELECT id_reserva FROM reserva
                      WHERE codigo = 'RSV-AQUI-EL-CODIGO');

UPDATE reserva
   SET estado = 'CANCELADA'
 WHERE codigo = 'RSV-AQUI-EL-CODIGO';

-- 2. La habitacion vuelve a estar disponible
UPDATE habitacion SET estado = 'DISPONIBLE' WHERE numero = '101';

-- 3. Comprobacion
SELECT numero, estado FROM habitacion WHERE numero = '101';


-- ============================================================================
--  SI ALGO SALE MAL Y QUIERES EMPEZAR DE CERO
--  Desde la terminal del proyecto:
--      .venv\Scripts\python.exe setup_db.py
--  Reconstruye la base completa en unos segundos.
-- ============================================================================

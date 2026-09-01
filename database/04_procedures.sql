-- QUE HACE: guarda dentro de la base las operaciones importantes, para
-- llamarlas por su nombre.
--
-- SI PREGUNTAN POR ESTE ARCHIVO:
-- "Crear una reserva son varios pasos: validar, guardar la cabecera, guardar
--  cada habitacion, calcular el total. O pasan todos o no pasa ninguno. Al
--  estar aqui dentro forman una sola operacion, y si algo falla a la mitad la
--  base deshace todo automaticamente."
--
-- Al final del procedimiento de crear reserva hay un bloque que atrapa el
-- error tecnico del choque de fechas y lo convierte en un mensaje que la
-- persona puede entender.

-- ============================================================================
--  HOTEL AURORA  ·  04_procedures.sql
--  Criterio 1.2: reglas de negocio en operaciones criticas mediante
--  procedimientos almacenados y funciones.
-- ============================================================================

-- ============================================================================
-- FUNCION  ·  fn_calcular_tarifa
--   Precio de una habitacion aplicando el factor de temporada noche por noche.
--   Es el espejo en SQL del metodo polimorfico calcular_tarifa() de Python.
-- ============================================================================
CREATE OR REPLACE FUNCTION fn_calcular_tarifa(
    p_id_habitacion INT,
    p_checkin       DATE,
    p_checkout      DATE
) RETURNS NUMERIC(12,2)
LANGUAGE plpgsql STABLE AS $$
DECLARE
    v_total NUMERIC(12,2);
BEGIN
    IF p_checkout <= p_checkin THEN
        RAISE EXCEPTION 'RES-002: la fecha de salida debe ser posterior a la de entrada';
    END IF;

    SELECT COALESCE(SUM(
               CASE th.codigo
                   -- Suite: 25 % de recargo por amenidades
                   WHEN 'SUI' THEN th.tarifa_base * 1.25
                   -- Familiar: tarifa base mas cargo por cama extra
                   WHEN 'FAM' THEN th.tarifa_base + 12.00
                   ELSE th.tarifa_base
               END * COALESCE(t.factor, 1.00)
           ), 0)
      INTO v_total
      FROM generate_series(p_checkin, p_checkout - 1, INTERVAL '1 day') AS noche(dia)
      CROSS JOIN habitacion h
      JOIN tipo_habitacion th ON th.id_tipo = h.id_tipo
      LEFT JOIN temporada t
             ON noche.dia::date BETWEEN t.fecha_inicio AND t.fecha_fin
     WHERE h.id_habitacion = p_id_habitacion;

    -- Descuento del 10 % en suites con estadia de 5 noches o mas
    IF (p_checkout - p_checkin) >= 5
       AND EXISTS (SELECT 1 FROM habitacion h
                     JOIN tipo_habitacion th ON th.id_tipo = h.id_tipo
                    WHERE h.id_habitacion = p_id_habitacion AND th.codigo = 'SUI')
    THEN
        v_total := ROUND(v_total * 0.90, 2);
    END IF;

    RETURN v_total;
END;
$$;


-- ============================================================================
-- PROCEDIMIENTO CRITICO  ·  sp_crear_reserva
--   Crea la cabecera y todo el detalle en UNA SOLA transaccion.
--   Si cualquier regla falla, no queda ni media reserva en la base.
-- ============================================================================
CREATE OR REPLACE PROCEDURE sp_crear_reserva(
    p_id_cliente    INT,
    p_habitaciones  INT[],
    p_checkin       DATE,
    p_checkout      DATE,
    p_adultos       SMALLINT,
    p_ninos         SMALLINT,
    INOUT p_codigo  VARCHAR DEFAULT NULL,
    INOUT p_total   NUMERIC DEFAULT NULL
)
LANGUAGE plpgsql AS $$
DECLARE
    v_id_reserva INT;
    v_hab        INT;
    v_subtotal   NUMERIC(12,2);
    v_capacidad  INT;
    v_total      NUMERIC(12,2) := 0;
BEGIN
    ------------------------------------------------------------------
    -- 1. Validaciones previas (mismas reglas que el formulario web)
    ------------------------------------------------------------------
    IF p_checkin < CURRENT_DATE THEN
        RAISE EXCEPTION 'RES-001: no se pueden reservar fechas pasadas';
    END IF;

    IF p_checkout <= p_checkin THEN
        RAISE EXCEPTION 'RES-002: la fecha de salida debe ser posterior a la de entrada';
    END IF;

    IF p_habitaciones IS NULL OR array_length(p_habitaciones, 1) IS NULL THEN
        RAISE EXCEPTION 'RES-003: debe seleccionar al menos una habitacion';
    END IF;

    IF NOT EXISTS (SELECT 1 FROM cliente WHERE id_cliente = p_id_cliente) THEN
        RAISE EXCEPTION 'RES-009: el cliente % no existe', p_id_cliente;
    END IF;

    SELECT COALESCE(SUM(th.capacidad_max), 0)
      INTO v_capacidad
      FROM habitacion h
      JOIN tipo_habitacion th ON th.id_tipo = h.id_tipo
     WHERE h.id_habitacion = ANY(p_habitaciones);

    IF (p_adultos + p_ninos) > v_capacidad THEN
        RAISE EXCEPTION
            'RES-004: % huespedes superan la capacidad de % personas de las habitaciones elegidas',
            p_adultos + p_ninos, v_capacidad;
    END IF;

    ------------------------------------------------------------------
    -- 2. Cabecera
    ------------------------------------------------------------------
    p_codigo := 'RSV-' || to_char(CURRENT_DATE, 'YYYYMMDD') || '-'
                || lpad(nextval('seq_codigo_reserva')::text, 4, '0');

    INSERT INTO reserva (codigo, id_cliente, fecha_checkin, fecha_checkout,
                         num_adultos, num_ninos, estado)
    VALUES (p_codigo, p_id_cliente, p_checkin, p_checkout,
            p_adultos, p_ninos, 'PENDIENTE')
    RETURNING id_reserva INTO v_id_reserva;

    ------------------------------------------------------------------
    -- 3. Detalle: una fila por habitacion
    ------------------------------------------------------------------
    FOREACH v_hab IN ARRAY p_habitaciones LOOP

        IF NOT EXISTS (SELECT 1 FROM habitacion
                        WHERE id_habitacion = v_hab
                          AND activa = TRUE
                          AND estado <> 'MANTENIMIENTO') THEN
            RAISE EXCEPTION 'RES-005: la habitacion % no esta disponible', v_hab;
        END IF;

        v_subtotal := fn_calcular_tarifa(v_hab, p_checkin, p_checkout);

        INSERT INTO reserva_habitacion (id_reserva, id_habitacion, estadia, subtotal)
        VALUES (v_id_reserva, v_hab,
                daterange(p_checkin, p_checkout, '[)'), v_subtotal);

        v_total := v_total + v_subtotal;
    END LOOP;

    ------------------------------------------------------------------
    -- 4. Cierre
    ------------------------------------------------------------------
    UPDATE reserva SET total = v_total WHERE id_reserva = v_id_reserva;
    p_total := v_total;

EXCEPTION
    -- SQLSTATE 23P01: la restriccion EXCLUDE detecto un cruce de fechas
    WHEN exclusion_violation THEN
        RAISE EXCEPTION
            'RES-006: una de las habitaciones seleccionadas ya esta reservada en esas fechas';
END;
$$;


-- ============================================================================
-- PROCEDIMIENTO  ·  sp_cancelar_reserva
--   Aplica la regla de penalizacion y libera el inventario.
-- ============================================================================
CREATE OR REPLACE PROCEDURE sp_cancelar_reserva(
    p_codigo          VARCHAR,
    p_motivo          TEXT,
    INOUT p_penalidad NUMERIC DEFAULT 0
)
LANGUAGE plpgsql AS $$
DECLARE
    r RECORD;
BEGIN
    SELECT * INTO r FROM reserva WHERE codigo = p_codigo FOR UPDATE;

    IF NOT FOUND THEN
        RAISE EXCEPTION 'CAN-001: no existe la reserva %', p_codigo;
    END IF;

    IF r.estado IN ('CHECK_IN', 'CHECK_OUT', 'CANCELADA') THEN
        RAISE EXCEPTION
            'CAN-002: una reserva en estado % no se puede cancelar', r.estado;
    END IF;

    -- Regla de negocio: menos de 48 horas de anticipacion => 20 % de penalidad
    p_penalidad := CASE
        WHEN r.fecha_checkin - CURRENT_DATE < 2 THEN ROUND(r.total * 0.20, 2)
        ELSE 0
    END;

    -- Liberar el detalle para que la restriccion EXCLUDE deje de bloquear
    UPDATE reserva_habitacion
       SET anulado = TRUE
     WHERE id_reserva = r.id_reserva;

    -- Este UPDATE dispara trg_reserva_estado y libera las habitaciones
    UPDATE reserva
       SET estado = 'CANCELADA',
           observaciones = COALESCE(observaciones, '') ||
               format(E'\n[%s] Cancelada: %s. Penalidad aplicada: %s',
                      CURRENT_DATE, p_motivo, p_penalidad)
     WHERE id_reserva = r.id_reserva;
END;
$$;


-- ============================================================================
-- PROCEDIMIENTO  ·  sp_registrar_pago
--   Registra un abono y confirma automaticamente la reserva al cubrir el 50 %.
-- ============================================================================
CREATE OR REPLACE PROCEDURE sp_registrar_pago(
    p_codigo         VARCHAR,
    p_monto          NUMERIC,
    p_metodo         metodo_pago,
    INOUT p_saldo    NUMERIC DEFAULT NULL
)
LANGUAGE plpgsql AS $$
DECLARE
    r         RECORD;
    v_pagado  NUMERIC(12,2);
BEGIN
    SELECT * INTO r FROM reserva WHERE codigo = p_codigo FOR UPDATE;

    IF NOT FOUND THEN
        RAISE EXCEPTION 'PAG-001: no existe la reserva %', p_codigo;
    END IF;

    IF p_monto <= 0 THEN
        RAISE EXCEPTION 'PAG-002: el monto del pago debe ser mayor que cero';
    END IF;

    INSERT INTO pago (id_reserva, monto, metodo)
    VALUES (r.id_reserva, p_monto, p_metodo);

    SELECT COALESCE(SUM(monto), 0) INTO v_pagado
      FROM pago WHERE id_reserva = r.id_reserva;

    -- Con el 50 % abonado la reserva se confirma sola (dispara el trigger)
    IF v_pagado >= r.total * 0.50 AND r.estado = 'PENDIENTE' THEN
        UPDATE reserva SET estado = 'CONFIRMADA' WHERE id_reserva = r.id_reserva;
    END IF;

    p_saldo := r.total - v_pagado;
END;
$$;


-- ============================================================================
-- EJEMPLOS DE USO
-- ----------------------------------------------------------------------------
-- CALL sp_crear_reserva(1, ARRAY[3,4], CURRENT_DATE + 10, CURRENT_DATE + 14,
--                       2::smallint, 1::smallint);
-- CALL sp_registrar_pago('RSV-20260830-0001', 150.00, 'TARJETA');
-- CALL sp_cancelar_reserva('RSV-20260830-0001', 'Cambio de itinerario');
-- ============================================================================

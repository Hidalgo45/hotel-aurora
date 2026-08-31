-- ============================================================================
--  HOTEL AURORA  ·  02_constraints.sql
--  Replica en la base de datos TODAS las validaciones del formulario web.
--  Criterio 1.2 de la rubrica: CHECK, DEFAULT, UNIQUE y restricciones de rango.
-- ============================================================================

-- ----------------------------------------------------------------------------
-- USUARIO  ·  identidad y contacto
-- ----------------------------------------------------------------------------
ALTER TABLE usuario
    ADD CONSTRAINT ck_usuario_cedula
        CHECK (cedula ~ '^[0-9]{10}$'),
    ADD CONSTRAINT ck_usuario_email
        CHECK (email ~* '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$'),
    ADD CONSTRAINT ck_usuario_telefono
        CHECK (telefono IS NULL OR telefono ~ '^[0-9+ -]{7,15}$'),
    ADD CONSTRAINT ck_usuario_nombres
        CHECK (length(btrim(nombres)) >= 2 AND length(btrim(apellidos)) >= 2);

-- ----------------------------------------------------------------------------
-- CLIENTE  ·  solo mayores de edad pueden reservar
-- ----------------------------------------------------------------------------
ALTER TABLE cliente
    ADD CONSTRAINT ck_cliente_mayor_edad
        CHECK (fecha_nacimiento <= CURRENT_DATE - INTERVAL '18 years'),
    ADD CONSTRAINT ck_cliente_nacimiento_real
        CHECK (fecha_nacimiento >= DATE '1900-01-01');

-- ----------------------------------------------------------------------------
-- INVENTARIO
-- ----------------------------------------------------------------------------
ALTER TABLE tipo_habitacion
    ADD CONSTRAINT ck_tipo_capacidad CHECK (capacidad_max BETWEEN 1 AND 8),
    ADD CONSTRAINT ck_tipo_tarifa    CHECK (tarifa_base > 0);

ALTER TABLE habitacion
    ADD CONSTRAINT ck_hab_piso   CHECK (piso BETWEEN 1 AND 12),
    ADD CONSTRAINT ck_hab_numero CHECK (numero ~ '^[0-9]{3,4}$');

ALTER TABLE temporada
    ADD CONSTRAINT ck_temp_rango  CHECK (fecha_fin > fecha_inicio),
    ADD CONSTRAINT ck_temp_factor CHECK (factor BETWEEN 0.50 AND 3.00),
    -- Dos temporadas no pueden traslaparse: si lo hicieran, no se sabria
    -- que factor de precio aplicar a una misma noche.
    ADD CONSTRAINT ex_temporada_solapada
        EXCLUDE USING gist (daterange(fecha_inicio, fecha_fin, '[]') WITH &&);

ALTER TABLE servicio
    ADD CONSTRAINT ck_servicio_precio CHECK (precio >= 0);

-- ----------------------------------------------------------------------------
-- RESERVA  ·  reglas temporales y de aforo
-- ----------------------------------------------------------------------------
ALTER TABLE reserva
    ADD CONSTRAINT ck_reserva_fechas
        CHECK (fecha_checkout > fecha_checkin),
    ADD CONSTRAINT ck_reserva_estancia
        CHECK (fecha_checkout - fecha_checkin <= 30),
    ADD CONSTRAINT ck_reserva_adultos
        CHECK (num_adultos BETWEEN 1 AND 10),
    ADD CONSTRAINT ck_reserva_ninos
        CHECK (num_ninos BETWEEN 0 AND 10),
    ADD CONSTRAINT ck_reserva_total
        CHECK (total >= 0),
    ADD CONSTRAINT ck_reserva_codigo
        CHECK (codigo ~ '^RSV-[0-9]{8}-[0-9]{4}$');

-- ----------------------------------------------------------------------------
-- RESERVA_HABITACION  ·  LA restriccion estrella del proyecto
-- ----------------------------------------------------------------------------
ALTER TABLE reserva_habitacion
    ADD CONSTRAINT ck_rh_subtotal    CHECK (subtotal >= 0),
    ADD CONSTRAINT ck_rh_estadia     CHECK (NOT isempty(estadia)),
    ADD CONSTRAINT uq_rh_reserva_hab UNIQUE (id_reserva, id_habitacion),

    -- Una misma habitacion NO puede tener dos estadias que se crucen.
    -- A diferencia de un SELECT previo, esta restriccion se evalua DENTRO de la
    -- transaccion, por lo que tambien resuelve la condicion de carrera entre
    -- dos usuarios que reservan en el mismo instante.  Error SQLSTATE 23P01.
    ADD CONSTRAINT ex_habitacion_ocupada
        EXCLUDE USING gist (id_habitacion WITH =, estadia WITH &&)
        WHERE (anulado = FALSE);

-- ----------------------------------------------------------------------------
-- RESERVA_SERVICIO y PAGO
-- ----------------------------------------------------------------------------
ALTER TABLE reserva_servicio
    ADD CONSTRAINT uq_rs_reserva_servicio UNIQUE (id_reserva, id_servicio),
    ADD CONSTRAINT ck_rs_cantidad CHECK (cantidad BETWEEN 1 AND 50),
    ADD CONSTRAINT ck_rs_precio   CHECK (precio_unitario >= 0);

ALTER TABLE pago
    ADD CONSTRAINT ck_pago_monto CHECK (monto > 0);

-- ----------------------------------------------------------------------------
-- VERIFICACION RAPIDA  ·  lista todas las restricciones creadas
-- ----------------------------------------------------------------------------
-- SELECT conrelid::regclass AS tabla, conname AS restriccion,
--        CASE contype WHEN 'c' THEN 'CHECK' WHEN 'u' THEN 'UNIQUE'
--                     WHEN 'x' THEN 'EXCLUDE' WHEN 'f' THEN 'FOREIGN KEY'
--                     WHEN 'p' THEN 'PRIMARY KEY' END AS tipo
--   FROM pg_constraint
--  WHERE connamespace = 'public'::regnamespace
--  ORDER BY tabla, tipo;

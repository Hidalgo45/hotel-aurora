-- ============================================================================
--  HOTEL AURORA  ·  07_datos_prueba.sql
--  Semilla de datos: 28 habitaciones, catalogo de servicios, temporadas,
--  usuarios de demostracion e historial de reservas para los reportes.
-- ============================================================================
--  Contrasena de todos los usuarios de demostracion:  aurora123
-- ============================================================================

-- ----------------------------------------------------------------------------
-- 1. ROLES DE APLICACION
-- ----------------------------------------------------------------------------
INSERT INTO rol (nombre, descripcion) VALUES
    ('ADMIN',     'Administrador del sistema: acceso total y reportes'),
    ('RECEPCION', 'Recepcionista: gestiona reservas, check-in y check-out'),
    ('CLIENTE',   'Huesped: consulta disponibilidad y reserva en linea');

-- ----------------------------------------------------------------------------
-- 2. USUARIOS DE DEMOSTRACION
-- ----------------------------------------------------------------------------
INSERT INTO usuario (id_rol, cedula, nombres, apellidos, email, telefono, password_hash) VALUES
    (1, '1712345678', 'Mateo',   'Hidalgo',  'mateo@aurora.ec',   '0991234567',
        'scrypt:32768:8:1$aPkdqXaWs17mfHCG$a37a652cb8b1ef5a45818d5b34fef9dccdaeb5db26b9b99a0d2f184dd14024bacd78766c9b533a39e48ed0c474700a96c367e90f4ff90f273bb2f0a649c722ce'),
    (2, '1723456789', 'Valeria', 'Suarez',   'valeria@aurora.ec', '0987654321',
        'scrypt:32768:8:1$aPkdqXaWs17mfHCG$a37a652cb8b1ef5a45818d5b34fef9dccdaeb5db26b9b99a0d2f184dd14024bacd78766c9b533a39e48ed0c474700a96c367e90f4ff90f273bb2f0a649c722ce'),
    (2, '1734567890', 'Isaac',   'Paredes',  'isaac@aurora.ec',   '0976543210',
        'scrypt:32768:8:1$aPkdqXaWs17mfHCG$a37a652cb8b1ef5a45818d5b34fef9dccdaeb5db26b9b99a0d2f184dd14024bacd78766c9b533a39e48ed0c474700a96c367e90f4ff90f273bb2f0a649c722ce');

INSERT INTO empleado (id_empleado, cargo, fecha_ingreso) VALUES
    (1, 'Administrador general', DATE '2024-01-15'),
    (2, 'Jefa de recepcion',     DATE '2024-03-01'),
    (3, 'Recepcionista',         DATE '2025-06-10');

-- Clientes
INSERT INTO usuario (id_rol, cedula, nombres, apellidos, email, telefono, password_hash) VALUES
    (3, '1801234567', 'Carolina', 'Naranjo',  'carolina.naranjo@correo.com', '0991112223',
        'scrypt:32768:8:1$aPkdqXaWs17mfHCG$a37a652cb8b1ef5a45818d5b34fef9dccdaeb5db26b9b99a0d2f184dd14024bacd78766c9b533a39e48ed0c474700a96c367e90f4ff90f273bb2f0a649c722ce'),
    (3, '1802345678', 'Andres',   'Villacis', 'andres.villacis@correo.com',  '0992223334',
        'scrypt:32768:8:1$aPkdqXaWs17mfHCG$a37a652cb8b1ef5a45818d5b34fef9dccdaeb5db26b9b99a0d2f184dd14024bacd78766c9b533a39e48ed0c474700a96c367e90f4ff90f273bb2f0a649c722ce'),
    (3, '1803456789', 'Gabriela', 'Moncayo',  'gabriela.moncayo@correo.com', '0993334445',
        'scrypt:32768:8:1$aPkdqXaWs17mfHCG$a37a652cb8b1ef5a45818d5b34fef9dccdaeb5db26b9b99a0d2f184dd14024bacd78766c9b533a39e48ed0c474700a96c367e90f4ff90f273bb2f0a649c722ce'),
    (3, '1804567890', 'Sebastian','Cordova',  'sebastian.cordova@correo.com','0994445556',
        'scrypt:32768:8:1$aPkdqXaWs17mfHCG$a37a652cb8b1ef5a45818d5b34fef9dccdaeb5db26b9b99a0d2f184dd14024bacd78766c9b533a39e48ed0c474700a96c367e90f4ff90f273bb2f0a649c722ce'),
    (3, '1805678901', 'Daniela',  'Espinosa', 'daniela.espinosa@correo.com', '0995556667',
        'scrypt:32768:8:1$aPkdqXaWs17mfHCG$a37a652cb8b1ef5a45818d5b34fef9dccdaeb5db26b9b99a0d2f184dd14024bacd78766c9b533a39e48ed0c474700a96c367e90f4ff90f273bb2f0a649c722ce'),
    (3, '1806789012', 'Joaquin',  'Benitez',  'joaquin.benitez@correo.com',  '0996667778',
        'scrypt:32768:8:1$aPkdqXaWs17mfHCG$a37a652cb8b1ef5a45818d5b34fef9dccdaeb5db26b9b99a0d2f184dd14024bacd78766c9b533a39e48ed0c474700a96c367e90f4ff90f273bb2f0a649c722ce'),
    (3, '1807890123', 'Micaela',  'Zambrano', 'micaela.zambrano@correo.com', '0997778889',
        'scrypt:32768:8:1$aPkdqXaWs17mfHCG$a37a652cb8b1ef5a45818d5b34fef9dccdaeb5db26b9b99a0d2f184dd14024bacd78766c9b533a39e48ed0c474700a96c367e90f4ff90f273bb2f0a649c722ce'),
    (3, '1808901234', 'Ricardo',  'Almeida',  'ricardo.almeida@correo.com',  '0998889990',
        'scrypt:32768:8:1$aPkdqXaWs17mfHCG$a37a652cb8b1ef5a45818d5b34fef9dccdaeb5db26b9b99a0d2f184dd14024bacd78766c9b533a39e48ed0c474700a96c367e90f4ff90f273bb2f0a649c722ce');

INSERT INTO cliente (id_cliente, fecha_nacimiento, ciudad, pais) VALUES
    (4,  DATE '1992-04-18', 'Quito',      'Ecuador'),
    (5,  DATE '1988-11-02', 'Guayaquil',  'Ecuador'),
    (6,  DATE '1995-07-25', 'Cuenca',     'Ecuador'),
    (7,  DATE '1990-01-30', 'Quito',      'Ecuador'),
    (8,  DATE '1997-09-12', 'Ambato',     'Ecuador'),
    (9,  DATE '1985-03-08', 'Bogota',     'Colombia'),
    (10, DATE '1993-12-21', 'Quito',      'Ecuador'),
    (11, DATE '1980-06-05', 'Lima',       'Peru');

-- ----------------------------------------------------------------------------
-- 3. TIPOS DE HABITACION
-- ----------------------------------------------------------------------------
INSERT INTO tipo_habitacion (codigo, nombre, descripcion, capacidad_max, tarifa_base, imagen) VALUES
    ('EST', 'Estandar',
     'Habitacion comoda con cama matrimonial, escritorio y bano privado. Ideal para viajes cortos.',
     2, 45.00, 'estandar.jpg'),
    ('FAM', 'Familiar',
     'Amplia habitacion con cama matrimonial y camas adicionales. Pensada para viajar en familia.',
     5, 65.00, 'familiar.jpg'),
    ('SUI', 'Suite',
     'Suite con sala independiente, jacuzzi, minibar y desayuno buffet incluido.',
     3, 85.00, 'suite.jpg');

-- ----------------------------------------------------------------------------
-- 4. LAS 28 HABITACIONES DEL HOTEL
-- ----------------------------------------------------------------------------
INSERT INTO habitacion (id_tipo, numero, piso) VALUES
    -- Piso 1 y 2: Estandar (16)
    (1, '101', 1), (1, '102', 1), (1, '103', 1), (1, '104', 1),
    (1, '105', 1), (1, '106', 1), (1, '107', 1), (1, '108', 1),
    (1, '201', 2), (1, '202', 2), (1, '203', 2), (1, '204', 2),
    (1, '205', 2), (1, '206', 2), (1, '207', 2), (1, '208', 2),
    -- Piso 3: Familiar (6)
    (2, '301', 3), (2, '302', 3), (2, '303', 3),
    (2, '304', 3), (2, '305', 3), (2, '306', 3),
    -- Piso 4: Suite (6)
    (3, '401', 4), (3, '402', 4), (3, '403', 4),
    (3, '404', 4), (3, '405', 4), (3, '406', 4);

-- ----------------------------------------------------------------------------
-- 5. TEMPORADAS  (el factor multiplica la tarifa noche por noche)
-- ----------------------------------------------------------------------------
INSERT INTO temporada (nombre, fecha_inicio, fecha_fin, factor) VALUES
    ('Temporada baja',        DATE '2026-05-01', DATE '2026-08-15', 0.90),
    ('Feriado de noviembre',  DATE '2026-11-01', DATE '2026-11-05', 1.35),
    ('Navidad y fin de ano',  DATE '2026-12-20', DATE '2027-01-06', 1.50);

-- ----------------------------------------------------------------------------
-- 6. CATALOGO DE SERVICIOS
-- ----------------------------------------------------------------------------
INSERT INTO servicio (nombre, descripcion, precio, modo_cobro) VALUES
    ('Desayuno buffet',      'Desayuno completo servido de 06:30 a 10:00',        8.50,  'POR_NOCHE'),
    ('Parqueadero cubierto', 'Espacio privado en el subsuelo del hotel',          5.00,  'POR_NOCHE'),
    ('Traslado aeropuerto',  'Transporte privado desde o hacia el aeropuerto',   25.00,  'POR_UNIDAD'),
    ('Lavanderia express',   'Servicio de lavado y planchado en 6 horas',        12.00,  'POR_UNIDAD'),
    ('Tour centro historico','Recorrido guiado de medio dia por el centro',      30.00,  'POR_UNIDAD'),
    ('Cena romantica',       'Cena de tres tiempos servida en la habitacion',    45.00,  'POR_UNIDAD');

-- ----------------------------------------------------------------------------
-- 7. HISTORIAL DE RESERVAS
--    Se generan reservas repartidas en los ultimos 4 meses y los proximos 2
--    para que los reportes tengan datos reales que mostrar.
--    Las reservas historicas se insertan directamente (no por el procedimiento)
--    porque sp_crear_reserva bloquea fechas pasadas, tal como debe hacerlo.
-- ----------------------------------------------------------------------------
DO $$
DECLARE
    v_cliente     INT;
    v_habitacion  INT;
    v_checkin     DATE;
    v_noches      INT;
    v_checkout    DATE;
    v_id_reserva  INT;
    v_subtotal    NUMERIC(12,2);
    v_codigo      VARCHAR(20);
    v_creadas     INT := 0;
    i             INT;
BEGIN
    FOR i IN 1..70 LOOP
        BEGIN
            v_cliente    := 4 + floor(random() * 8)::int;          -- clientes 4..11
            v_habitacion := 1 + floor(random() * 28)::int;         -- 28 habitaciones
            v_checkin    := CURRENT_DATE - 115 + floor(random() * 165)::int;
            v_noches     := 1 + floor(random() * 5)::int;
            v_checkout   := v_checkin + v_noches;

            v_codigo := 'RSV-' || to_char(v_checkin, 'YYYYMMDD') || '-'
                        || lpad(nextval('seq_codigo_reserva')::text, 4, '0');

            INSERT INTO reserva (codigo, id_cliente, id_empleado,
                                 fecha_checkin, fecha_checkout,
                                 num_adultos, num_ninos, estado, total, creada_en)
            VALUES (v_codigo, v_cliente,
                    CASE WHEN random() < 0.4 THEN 2 ELSE NULL END,
                    v_checkin, v_checkout,
                    1 + floor(random() * 2)::int,
                    floor(random() * 2)::int,
                    'PENDIENTE', 0,
                    v_checkin - 7)
            RETURNING id_reserva INTO v_id_reserva;

            v_subtotal := fn_calcular_tarifa(v_habitacion, v_checkin, v_checkout);

            INSERT INTO reserva_habitacion (id_reserva, id_habitacion, estadia, subtotal)
            VALUES (v_id_reserva, v_habitacion,
                    daterange(v_checkin, v_checkout, '[)'), v_subtotal);

            UPDATE reserva SET total = v_subtotal WHERE id_reserva = v_id_reserva;

            -- Servicios adicionales en aproximadamente la mitad de las reservas
            IF random() < 0.55 THEN
                INSERT INTO reserva_servicio (id_reserva, id_servicio, cantidad, precio_unitario)
                SELECT v_id_reserva, s.id_servicio,
                       CASE WHEN s.modo_cobro = 'POR_NOCHE' THEN v_noches ELSE 1 END,
                       s.precio
                  FROM servicio s
                 WHERE s.id_servicio = 1 + floor(random() * 6)::int;
            END IF;

            v_creadas := v_creadas + 1;

        EXCEPTION
            -- Si la habitacion sorteada ya estaba ocupada en esas fechas,
            -- simplemente se descarta ese intento y se continua.
            WHEN exclusion_violation THEN
                NULL;
        END;
    END LOOP;

    RAISE NOTICE 'Reservas creadas: %', v_creadas;
END $$;

-- ---- Estado segun la fecha --------------------------------------------------
UPDATE reserva SET estado = 'CHECK_OUT'  WHERE fecha_checkout <  CURRENT_DATE;
UPDATE reserva SET estado = 'CHECK_IN'   WHERE fecha_checkin  <= CURRENT_DATE
                                           AND fecha_checkout >  CURRENT_DATE;
UPDATE reserva SET estado = 'CONFIRMADA' WHERE fecha_checkin  >  CURRENT_DATE;

-- Un 10 % de las reservas futuras se cancela (datos realistas)
UPDATE reserva
   SET estado = 'CANCELADA',
       observaciones = 'Cancelada por el cliente antes del viaje'
 WHERE fecha_checkin > CURRENT_DATE + 5
   AND id_reserva % 9 = 0;

UPDATE reserva_habitacion rh
   SET anulado = TRUE
  FROM reserva r
 WHERE r.id_reserva = rh.id_reserva AND r.estado = 'CANCELADA';

-- ---- Pagos ------------------------------------------------------------------
-- Las estadias terminadas estan pagadas por completo
INSERT INTO pago (id_reserva, monto, metodo, fecha)
SELECT r.id_reserva, r.total,
       (ARRAY['EFECTIVO','TARJETA','TRANSFERENCIA']::metodo_pago[])[1 + floor(random()*3)::int],
       r.fecha_checkout
  FROM reserva r
 WHERE r.estado = 'CHECK_OUT' AND r.total > 0;

-- Las reservas futuras confirmadas tienen abonado el 50 %
INSERT INTO pago (id_reserva, monto, metodo, fecha)
SELECT r.id_reserva, ROUND(r.total * 0.50, 2), 'TARJETA'::metodo_pago, r.creada_en
  FROM reserva r
 WHERE r.estado IN ('CONFIRMADA', 'CHECK_IN') AND r.total > 0;

-- ----------------------------------------------------------------------------
-- 8. NORMALIZAR EL INVENTARIO
--    Los UPDATE anteriores dispararon el trigger muchas veces; aqui se deja el
--    estado fisico coherente con la realidad de hoy.
-- ----------------------------------------------------------------------------
UPDATE habitacion SET estado = 'DISPONIBLE';

UPDATE habitacion h SET estado = 'RESERVADA'
 WHERE EXISTS (SELECT 1 FROM reserva_habitacion rh
                 JOIN reserva r ON r.id_reserva = rh.id_reserva
                WHERE rh.id_habitacion = h.id_habitacion
                  AND rh.anulado = FALSE
                  AND r.estado = 'CONFIRMADA'
                  AND r.fecha_checkin BETWEEN CURRENT_DATE AND CURRENT_DATE + 2);

UPDATE habitacion h SET estado = 'OCUPADA'
 WHERE EXISTS (SELECT 1 FROM reserva_habitacion rh
                 JOIN reserva r ON r.id_reserva = rh.id_reserva
                WHERE rh.id_habitacion = h.id_habitacion
                  AND rh.anulado = FALSE
                  AND r.estado = 'CHECK_IN');

-- Dos habitaciones fuera de servicio, para demostrar que el trigger las respeta
UPDATE habitacion SET estado = 'MANTENIMIENTO' WHERE numero IN ('108', '306');

-- Limpiar la bitacora generada por la carga masiva
TRUNCATE bitacora_habitacion RESTART IDENTITY;

-- ----------------------------------------------------------------------------
-- 9. VERIFICACION
-- ----------------------------------------------------------------------------
SELECT 'Habitaciones' AS entidad, COUNT(*) AS registros FROM habitacion
UNION ALL SELECT 'Usuarios',   COUNT(*) FROM usuario
UNION ALL SELECT 'Clientes',   COUNT(*) FROM cliente
UNION ALL SELECT 'Reservas',   COUNT(*) FROM reserva
UNION ALL SELECT 'Detalles',   COUNT(*) FROM reserva_habitacion
UNION ALL SELECT 'Servicios vendidos', COUNT(*) FROM reserva_servicio
UNION ALL SELECT 'Pagos',      COUNT(*) FROM pago;

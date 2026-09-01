-- QUE HACE: crea las 13 tablas del sistema y las conecta entre si.
--
-- SI PREGUNTAN POR ESTE ARCHIVO:
-- "Es la estructura completa. Cada tabla tiene una columna que identifica sus
--  filas sin confusion, y las columnas que apuntan a otra tabla son las que
--  conectan la informacion: una reserva sabe de que cliente es porque guarda
--  su identificador."
--
-- La tabla reserva_habitacion existe porque una reserva puede tener varias
-- habitaciones y una habitacion aparece en muchas reservas. Cuando pasa eso,
-- hace falta una tabla en medio; no se puede resolver con una sola columna.

-- ============================================================================
--  HOTEL AURORA  ·  Sistema de Reservas y Gestion Hotelera
--  01_schema.sql  ·  Tipos, tablas, claves primarias, foraneas e indices
--  Proyecto Integrador - PUCE TEC - Segundo Nivel
-- ============================================================================
--  Ejecutar sobre la base de datos hotel_aurora, como usuario postgres.
--  Este script es idempotente: se puede volver a correr desde cero.
-- ============================================================================

DROP SCHEMA IF EXISTS public CASCADE;
CREATE SCHEMA public;

CREATE EXTENSION IF NOT EXISTS btree_gist;   -- requerida por la restriccion EXCLUDE

-- ----------------------------------------------------------------------------
-- 1. DOMINIOS ENUMERADOS  (integridad de dominio)
--    Impiden que exista un estado que el negocio no reconoce.
-- ----------------------------------------------------------------------------
CREATE TYPE estado_habitacion AS ENUM
    ('DISPONIBLE', 'RESERVADA', 'OCUPADA', 'LIMPIEZA', 'MANTENIMIENTO');

CREATE TYPE estado_reserva AS ENUM
    ('PENDIENTE', 'CONFIRMADA', 'CHECK_IN', 'CHECK_OUT', 'CANCELADA', 'NO_SHOW');

CREATE TYPE metodo_pago AS ENUM
    ('EFECTIVO', 'TARJETA', 'TRANSFERENCIA');

CREATE TYPE cobro_servicio AS ENUM
    ('POR_NOCHE', 'POR_UNIDAD');

-- ----------------------------------------------------------------------------
-- 2. PERSONAS   (supertipo usuario  ->  subtipos cliente / empleado)
-- ----------------------------------------------------------------------------
CREATE TABLE rol (
    id_rol       SMALLSERIAL  PRIMARY KEY,
    nombre       VARCHAR(20)  NOT NULL UNIQUE,
    descripcion  VARCHAR(120) NOT NULL
);

CREATE TABLE usuario (
    id_usuario     SERIAL       PRIMARY KEY,
    id_rol         SMALLINT     NOT NULL REFERENCES rol(id_rol),
    cedula         CHAR(10)     NOT NULL UNIQUE,
    nombres        VARCHAR(60)  NOT NULL,
    apellidos      VARCHAR(60)  NOT NULL,
    email          VARCHAR(120) NOT NULL UNIQUE,
    telefono       VARCHAR(15),
    password_hash  VARCHAR(255) NOT NULL,   -- hash scrypt/bcrypt, nunca texto plano
    activo         BOOLEAN      NOT NULL DEFAULT TRUE,
    creado_en      TIMESTAMPTZ  NOT NULL DEFAULT now()
);

CREATE TABLE cliente (
    id_cliente        INT PRIMARY KEY REFERENCES usuario(id_usuario) ON DELETE CASCADE,
    fecha_nacimiento  DATE        NOT NULL,
    ciudad            VARCHAR(60),
    pais              VARCHAR(60) NOT NULL DEFAULT 'Ecuador',
    preferencias      TEXT
);

CREATE TABLE empleado (
    id_empleado    INT PRIMARY KEY REFERENCES usuario(id_usuario) ON DELETE CASCADE,
    cargo          VARCHAR(40) NOT NULL,
    fecha_ingreso  DATE        NOT NULL DEFAULT CURRENT_DATE
);

-- ----------------------------------------------------------------------------
-- 3. INVENTARIO
-- ----------------------------------------------------------------------------
CREATE TABLE tipo_habitacion (
    id_tipo        SMALLSERIAL   PRIMARY KEY,
    codigo         VARCHAR(10)   NOT NULL UNIQUE,   -- EST, SUI, FAM
    nombre         VARCHAR(40)   NOT NULL,
    descripcion    TEXT,
    capacidad_max  SMALLINT      NOT NULL,
    tarifa_base    NUMERIC(10,2) NOT NULL,
    imagen         VARCHAR(120)
);

CREATE TABLE habitacion (
    id_habitacion  SERIAL     PRIMARY KEY,
    id_tipo        SMALLINT   NOT NULL REFERENCES tipo_habitacion(id_tipo),
    numero         VARCHAR(6) NOT NULL UNIQUE,
    piso           SMALLINT   NOT NULL,
    estado         estado_habitacion NOT NULL DEFAULT 'DISPONIBLE',
    activa         BOOLEAN    NOT NULL DEFAULT TRUE
);

CREATE TABLE temporada (
    id_temporada  SMALLSERIAL  PRIMARY KEY,
    nombre        VARCHAR(40)  NOT NULL,
    fecha_inicio  DATE         NOT NULL,
    fecha_fin     DATE         NOT NULL,
    factor        NUMERIC(4,2) NOT NULL DEFAULT 1.00
);

CREATE TABLE servicio (
    id_servicio  SERIAL        PRIMARY KEY,
    nombre       VARCHAR(60)   NOT NULL UNIQUE,
    descripcion  VARCHAR(160),
    precio       NUMERIC(10,2) NOT NULL,
    modo_cobro   cobro_servicio NOT NULL DEFAULT 'POR_UNIDAD',
    activo       BOOLEAN       NOT NULL DEFAULT TRUE
);

-- ----------------------------------------------------------------------------
-- 4. OPERACION
-- ----------------------------------------------------------------------------
CREATE SEQUENCE seq_codigo_reserva START 1;

CREATE TABLE reserva (
    id_reserva      SERIAL        PRIMARY KEY,
    codigo          VARCHAR(20)   NOT NULL UNIQUE,
    id_cliente      INT           NOT NULL REFERENCES cliente(id_cliente),
    id_empleado     INT           REFERENCES empleado(id_empleado),  -- NULL = reserva web
    fecha_checkin   DATE          NOT NULL,
    fecha_checkout  DATE          NOT NULL,
    num_adultos     SMALLINT      NOT NULL DEFAULT 1,
    num_ninos       SMALLINT      NOT NULL DEFAULT 0,
    estado          estado_reserva NOT NULL DEFAULT 'PENDIENTE',
    total           NUMERIC(12,2) NOT NULL DEFAULT 0,
    observaciones   TEXT,
    creada_en       TIMESTAMPTZ   NOT NULL DEFAULT now()
);

-- La columna estadia es de tipo DATERANGE: permite que PostgreSQL detecte
-- por si mismo el cruce de fechas mediante la restriccion EXCLUDE (script 02).
CREATE TABLE reserva_habitacion (
    id_detalle     SERIAL        PRIMARY KEY,
    id_reserva     INT           NOT NULL REFERENCES reserva(id_reserva) ON DELETE CASCADE,
    id_habitacion  INT           NOT NULL REFERENCES habitacion(id_habitacion),
    estadia        DATERANGE     NOT NULL,        -- [checkin, checkout)
    subtotal       NUMERIC(12,2) NOT NULL,
    anulado        BOOLEAN       NOT NULL DEFAULT FALSE
);

CREATE TABLE reserva_servicio (
    id_rs            SERIAL        PRIMARY KEY,
    id_reserva       INT           NOT NULL REFERENCES reserva(id_reserva) ON DELETE CASCADE,
    id_servicio      INT           NOT NULL REFERENCES servicio(id_servicio),
    cantidad         SMALLINT      NOT NULL DEFAULT 1,
    precio_unitario  NUMERIC(10,2) NOT NULL   -- precio congelado el dia de la venta
);

CREATE TABLE pago (
    id_pago     SERIAL        PRIMARY KEY,
    id_reserva  INT           NOT NULL REFERENCES reserva(id_reserva),
    monto       NUMERIC(12,2) NOT NULL,
    metodo      metodo_pago   NOT NULL,
    referencia  VARCHAR(40),
    fecha       TIMESTAMPTZ   NOT NULL DEFAULT now()
);

-- ----------------------------------------------------------------------------
-- 5. AUDITORIA  (trazabilidad: quien cambio que y cuando)
-- ----------------------------------------------------------------------------
CREATE TABLE bitacora_habitacion (
    id_bitacora      BIGSERIAL   PRIMARY KEY,
    id_habitacion    INT         NOT NULL REFERENCES habitacion(id_habitacion),
    id_reserva       INT         REFERENCES reserva(id_reserva),
    estado_anterior  estado_habitacion,
    estado_nuevo     estado_habitacion NOT NULL,
    usuario_bd       NAME        NOT NULL DEFAULT current_user,
    ocurrido_en      TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- ----------------------------------------------------------------------------
-- 6. INDICES DE APOYO A LOS REPORTES
-- ----------------------------------------------------------------------------
CREATE INDEX idx_reserva_fechas    ON reserva (fecha_checkin, fecha_checkout);
CREATE INDEX idx_reserva_estado    ON reserva (estado);
CREATE INDEX idx_reserva_cliente   ON reserva (id_cliente);
CREATE INDEX idx_rh_habitacion     ON reserva_habitacion (id_habitacion);
CREATE INDEX idx_rh_estadia        ON reserva_habitacion USING gist (estadia);
CREATE INDEX idx_habitacion_tipo   ON habitacion (id_tipo);

-- ----------------------------------------------------------------------------
-- 7. COMENTARIOS (documentacion viva del modelo, visible en pgAdmin)
-- ----------------------------------------------------------------------------
COMMENT ON TABLE  reserva_habitacion IS
    'Tabla puente Reserva-Habitacion. Rompe la relacion N:M y permite reservar '
    'varias habitaciones en una sola reserva (1FN).';
COMMENT ON COLUMN reserva_habitacion.estadia IS
    'Rango de fechas [checkin, checkout). Base de la restriccion EXCLUDE que '
    'impide la sobreventa.';
COMMENT ON COLUMN reserva_habitacion.subtotal IS
    'Precio congelado al momento de la venta (desnormalizacion deliberada: '
    'una factura historica no debe cambiar si suben las tarifas).';

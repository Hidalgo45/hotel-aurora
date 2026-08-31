-- ============================================================================
--  HOTEL AURORA  ·  03_triggers.sql
--  Criterio 1.2: reglas que deben cumplirse SIEMPRE, entre por donde entren
--  los datos (aplicacion web, pgAdmin o un script externo).
-- ============================================================================

-- ============================================================================
-- TRIGGER 1  ·  El estado fisico de la habitacion sigue al estado de la reserva
-- ----------------------------------------------------------------------------
--  CONFIRMADA -> RESERVADA     CHECK_IN  -> OCUPADA
--  CHECK_OUT  -> LIMPIEZA      CANCELADA -> DISPONIBLE
--  Ademas deja constancia del cambio en bitacora_habitacion.
-- ============================================================================
CREATE OR REPLACE FUNCTION fn_sincronizar_estado_habitacion()
RETURNS TRIGGER
LANGUAGE plpgsql AS $$
DECLARE
    v_nuevo_estado estado_habitacion;
    v_hab          RECORD;
BEGIN
    v_nuevo_estado := CASE NEW.estado
        WHEN 'CONFIRMADA' THEN 'RESERVADA'::estado_habitacion
        WHEN 'CHECK_IN'   THEN 'OCUPADA'::estado_habitacion
        WHEN 'CHECK_OUT'  THEN 'LIMPIEZA'::estado_habitacion
        WHEN 'CANCELADA'  THEN 'DISPONIBLE'::estado_habitacion
        WHEN 'NO_SHOW'    THEN 'DISPONIBLE'::estado_habitacion
        ELSE NULL
    END;

    -- El estado PENDIENTE no mueve el inventario fisico
    IF v_nuevo_estado IS NULL THEN
        RETURN NEW;
    END IF;

    FOR v_hab IN
        SELECT h.id_habitacion, h.estado
          FROM reserva_habitacion rh
          JOIN habitacion h ON h.id_habitacion = rh.id_habitacion
         WHERE rh.id_reserva = NEW.id_reserva
           AND rh.anulado = FALSE
    LOOP
        -- Nunca pisar una habitacion que esta fuera de servicio
        CONTINUE WHEN v_hab.estado = 'MANTENIMIENTO';

        UPDATE habitacion
           SET estado = v_nuevo_estado
         WHERE id_habitacion = v_hab.id_habitacion;

        INSERT INTO bitacora_habitacion
               (id_habitacion, id_reserva, estado_anterior, estado_nuevo)
        VALUES (v_hab.id_habitacion, NEW.id_reserva, v_hab.estado, v_nuevo_estado);
    END LOOP;

    RETURN NEW;
END;
$$;

DROP TRIGGER IF EXISTS trg_reserva_estado ON reserva;
CREATE TRIGGER trg_reserva_estado
    AFTER UPDATE OF estado ON reserva
    FOR EACH ROW
    WHEN (OLD.estado IS DISTINCT FROM NEW.estado)
    EXECUTE FUNCTION fn_sincronizar_estado_habitacion();


-- ============================================================================
-- TRIGGER 2  ·  Calidad del dato de usuario  (criterio 1.5)
--   Normaliza el formato y bloquea contrasenas guardadas en texto plano.
-- ============================================================================
CREATE OR REPLACE FUNCTION fn_normalizar_usuario()
RETURNS TRIGGER
LANGUAGE plpgsql AS $$
BEGIN
    NEW.email     := lower(btrim(NEW.email));
    NEW.nombres   := initcap(btrim(NEW.nombres));
    NEW.apellidos := initcap(btrim(NEW.apellidos));
    NEW.cedula    := btrim(NEW.cedula);

    IF length(NEW.password_hash) < 20 THEN
        RAISE EXCEPTION
            'SEG-001: la contrasena debe almacenarse hasheada, nunca en texto plano';
    END IF;

    RETURN NEW;
END;
$$;

DROP TRIGGER IF EXISTS trg_usuario_normaliza ON usuario;
CREATE TRIGGER trg_usuario_normaliza
    BEFORE INSERT OR UPDATE ON usuario
    FOR EACH ROW
    EXECUTE FUNCTION fn_normalizar_usuario();


-- ============================================================================
-- TRIGGER 3  ·  La estadia del detalle debe coincidir con la reserva
--   Evita que alguien inserte un detalle con fechas distintas a la cabecera.
-- ============================================================================
CREATE OR REPLACE FUNCTION fn_validar_estadia_detalle()
RETURNS TRIGGER
LANGUAGE plpgsql AS $$
DECLARE r RECORD;
BEGIN
    SELECT fecha_checkin, fecha_checkout INTO r
      FROM reserva WHERE id_reserva = NEW.id_reserva;

    IF lower(NEW.estadia) <> r.fecha_checkin
       OR upper(NEW.estadia) <> r.fecha_checkout THEN
        RAISE EXCEPTION
            'RES-008: la estadia del detalle (% a %) no coincide con la reserva (% a %)',
            lower(NEW.estadia), upper(NEW.estadia), r.fecha_checkin, r.fecha_checkout;
    END IF;

    RETURN NEW;
END;
$$;

DROP TRIGGER IF EXISTS trg_detalle_estadia ON reserva_habitacion;
CREATE TRIGGER trg_detalle_estadia
    BEFORE INSERT ON reserva_habitacion
    FOR EACH ROW
    EXECUTE FUNCTION fn_validar_estadia_detalle();


-- ============================================================================
-- DEMOSTRACION EN VIVO (para la sustentacion)
-- ----------------------------------------------------------------------------
-- Pestana 1:  SELECT numero, estado FROM habitacion ORDER BY numero;
-- Pestana 2:  UPDATE reserva SET estado = 'CHECK_IN' WHERE codigo = 'RSV-...';
-- Refrescar la pestana 1: la habitacion paso a OCUPADA sin que nadie la tocara.
-- Verificar el rastro:
--   SELECT * FROM bitacora_habitacion ORDER BY ocurrido_en DESC LIMIT 5;
-- ============================================================================

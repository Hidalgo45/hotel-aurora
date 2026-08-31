# Restauración y política de respaldos

> Criterio 1.5 de la rúbrica: *«estrategias básicas de respaldo de la base de datos»*.
> Un respaldo que nunca se restauró no cuenta como respaldo. Esta prueba se hace **antes** de la sustentación y se registra al final de este archivo.

---

## 1. Política

| Aspecto | Decisión | Por qué |
|---|---|---|
| Frecuencia | Diaria, al cierre de operaciones | Una reserva perdida es un huésped sin habitación |
| Formato | `--format=custom --compress=9` | Comprimido y permite restaurar tablas por separado |
| Retención | 7 diarios · 4 semanales · 12 mensuales | Cubre desde un error de ayer hasta uno del año pasado |
| Regla 3-2-1 | 3 copias · 2 medios · 1 fuera del equipo | El disco del servidor también falla |
| Prueba de restauración | Mensual, sobre una base desechable | Es la única forma de saber que el respaldo sirve |

---

## 2. Cómo restaurar

### 2.1 Prueba sobre una base desechable (lo que se hace normalmente)

```bash
createdb -U postgres aurora_prueba
pg_restore -U postgres -d aurora_prueba respaldos/aurora_2026-08-30.dump
```

Luego se verifica que los datos estén completos:

```sql
SELECT 'habitaciones' AS tabla, COUNT(*) FROM habitacion
UNION ALL SELECT 'reservas', COUNT(*) FROM reserva
UNION ALL SELECT 'usuarios', COUNT(*) FROM usuario;
```

Y al terminar se elimina la base de prueba:

```bash
dropdb -U postgres aurora_prueba
```

### 2.2 Restauración real tras una pérdida

```bash
dropdb -U postgres hotel_aurora
createdb -U postgres hotel_aurora
pg_restore -U postgres -d hotel_aurora --clean respaldos/aurora_2026-08-30.dump
```

### 2.3 Restaurar una sola tabla

Ventaja del formato `custom`: si solo se corrompió una tabla, no hace falta tocar el resto.

```bash
pg_restore -U postgres -d hotel_aurora --table=reserva --data-only \
           respaldos/aurora_2026-08-30.dump
```

---

## 3. Bitácora de pruebas de restauración

Llenar cada vez que se haga la prueba. Esta tabla es la evidencia que se muestra al docente.

| Fecha | Archivo restaurado | Duración | Filas verificadas | Resultado | Responsable |
|---|---|---|---|---|---|
| 2026-08-31 | `aurora_2026-08-31.dump` (133.6 KB) | 0.8 s | 314 en 13 tablas | Íntegra | Mateo Hidalgo |

### Detalle de la prueba del 31/08/2026

**Respaldo.** `backup.ps1` sobre `hotel_aurora`, formato custom con compresión 9. Duración: **1.1 s**. Salida: `aurora_2026-08-31.dump` (133.6 KB) y `esquema_2026-08-31.sql` (94.8 KB).

**Restauración.** Sobre la base desechable `aurora_prueba`, con `pg_restore`. Duración: **0.8 s**, sin errores ni advertencias.

**Verificación de integridad.** Se compararon los conteos de la base original contra la restaurada:

| Objeto | Original | Restaurada |
|---|---|---|
| rol | 3 | 3 |
| usuario | 12 | 12 |
| cliente | 9 | 9 |
| empleado | 3 | 3 |
| tipo_habitacion | 3 | 3 |
| habitacion | 28 | 28 |
| temporada | 3 | 3 |
| servicio | 6 | 6 |
| reserva | 71 | 71 |
| reserva_habitacion | 71 | 71 |
| reserva_servicio | 34 | 34 |
| pago | 67 | 67 |
| bitacora_habitacion | 4 | 4 |
| Triggers | 4 | 4 |
| Restricciones CHECK | 26 | 26 |
| Restricciones EXCLUDE | 2 | 2 |
| Vistas de reportes | 4 | 4 |

**Verificación funcional.** No basta con que estén las filas: se comprobó que la base restaurada *opera*.

| Prueba | Resultado |
|---|---|
| `CALL sp_crear_reserva(...)` | Creó `RSV-20260831-0074`, total $180.00 |
| Trigger de estado | La habitación 101 pasó sola a `RESERVADA` al confirmar |
| Restricción anti-sobreventa | Rechazó fechas cruzadas con `RES-006` |
| Vista `v_reporte_ocupacion` | Devolvió 18 filas |

La transacción de prueba se revirtió con `ROLLBACK` y la base `aurora_prueba` se eliminó al terminar.

**Conclusión.** El respaldo es restaurable y la base reconstruida conserva datos, restricciones, triggers, procedimientos y vistas.

> Si un docente pregunta «¿y si les borro la base ahora mismo?», la respuesta no es «tenemos respaldos», sino **«tenemos respaldos y los probamos: aquí está la bitácora»**.

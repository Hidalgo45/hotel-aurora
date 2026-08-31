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
| | | | | | |
| | | | | | |
| | | | | | |

> Si un docente pregunta «¿y si les borro la base ahora mismo?», la respuesta no es «tenemos respaldos», sino **«tenemos respaldos y los probamos: aquí está la bitácora»**.

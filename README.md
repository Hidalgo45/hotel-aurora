# Hotel Aurora — Sistema de Reservas y Gestión Hotelera

Proyecto Integrador de segundo nivel · PUCE TEC
Asignaturas integradas: **Programación Orientada a Objetos**, **Base de Datos I** y **Desarrollo Web Front End (UX/UI)**.

---

## 1. El problema

El Hotel Aurora administra sus 28 habitaciones con un cuaderno y una hoja de cálculo compartida. Eso produce tres problemas medibles: **sobreventa** de habitaciones en feriados, imposibilidad de conocer la ocupación real del mes y tarifas de temporada aplicadas a criterio de cada recepcionista.

Aurora digitaliza el ciclo completo —consulta de disponibilidad, reserva, confirmación, check-in, check-out y reportes gerenciales— y hace la sobreventa **estructuralmente imposible**: la restricción `EXCLUDE USING gist` sobre un `daterange` impide que PostgreSQL acepte dos reservas cruzadas de la misma habitación, incluso si se piden en el mismo instante.

---

## 2. Requisitos previos

| Software | Versión mínima | Nota |
|---|---|---|
| Python | 3.11 | Se usa `python` desde el entorno virtual del proyecto |
| PostgreSQL | 14 | Con pgAdmin 4 instalado |
| Navegador | Chrome / Edge actual | Para las pruebas responsive con DevTools |

---

## 3. Instalación paso a paso

### 3.1 Configurar la contraseña de PostgreSQL

Abrir el archivo `.env` y escribir en `DB_PASSWORD` la misma contraseña con la que se entra a pgAdmin con el usuario `postgres`:

```
DB_PASSWORD=tu_contrasena_de_postgres
```

> El archivo `.env` está en `.gitignore` y **nunca** se sube al repositorio. Lo que se versiona es `.env.example`, sin credenciales.

### 3.2 Crear la base de datos y cargar los datos

```bash
.venv\Scripts\python.exe setup_db.py
```

El instalador crea la base `hotel_aurora` si no existe y ejecuta los siete scripts en orden. Se puede volver a correr las veces que haga falta: reconstruye todo desde cero.

### 3.3 Levantar la aplicación

```bash
.venv\Scripts\python.exe run.py
```

Abrir <http://127.0.0.1:5000>

### 3.4 Si el entorno virtual no existe todavía

```bash
python -m venv .venv
.venv\Scripts\python.exe -m pip install -r requirements.txt
```

---

## 4. Usuarios de demostración

Contraseña de todos: **`aurora123`**

| Correo | Rol | Qué puede hacer |
|---|---|---|
| `mateo@aurora.ec` | ADMIN | Acceso total, panel y reportes |
| `valeria@aurora.ec` | RECEPCION | Reservas, check-in y check-out |
| `isaac@aurora.ec` | RECEPCION | Reservas, check-in y check-out |

Los clientes de prueba se cargan en `database/07_datos_prueba.sql` y usan la misma contraseña.

---

## 5. Estructura del proyecto

```
hotel-aurora/
├── app/
│   ├── dominio/          POO puro: sin Flask, sin SQL. Se prueba con pytest.
│   │   ├── habitaciones.py   Habitacion(ABC) → Estandar / Suite / Familiar
│   │   ├── personas.py       Persona(ABC) → Usuario → Admin / Recepcion / Cliente
│   │   ├── servicios.py      Servicio(ABC) → PorNoche / PorUnidad
│   │   └── reserva.py        Composición + máquina de estados
│   ├── repositorios/     Puente dominio ↔ PostgreSQL (llaman a los procedimientos)
│   ├── blueprints/       Rutas Flask: publico, cuenta, admin
│   ├── templates/        Jinja2 + Bootstrap 5
│   └── static/           aurora.css (tokens de diseño) · validaciones.js
├── database/
│   ├── 01_schema.sql         Tablas, tipos ENUM, PK y FK
│   ├── 02_constraints.sql    CHECK, UNIQUE, DEFAULT, EXCLUDE
│   ├── 03_triggers.sql       Sincronización de estado + calidad de datos
│   ├── 04_procedures.sql     sp_crear_reserva · sp_cancelar_reserva
│   ├── 05_reportes.sql       Los dos reportes con consultas complejas
│   ├── 06_seguridad.sql      Roles, GRANT, RLS y consultas de calidad
│   ├── 07_datos_prueba.sql   28 habitaciones y reservas de demostración
│   └── backup/               backup.ps1 · backup.sh · restore.md
├── docs/                 Diagramas, bitácora de Git y evidencias UX
├── tests/                Pruebas del dominio (no requieren base de datos)
├── setup_db.py           Instalador de la base
└── run.py                Punto de entrada
```

---

## 6. Comandos frecuentes

| Acción | Comando |
|---|---|
| Correr las pruebas | `.venv\Scripts\python.exe -m pytest -q` |
| Reconstruir la base | `.venv\Scripts\python.exe setup_db.py` |
| Levantar el servidor | `.venv\Scripts\python.exe run.py` |
| Respaldar la base | `powershell -File database\backup\backup.ps1` |
| Ver reparto de commits | `git shortlog -sn --all` |

---

## 7. Cómo el proyecto responde a la rúbrica

| Criterio | Puntos | Dónde está la evidencia |
|---|---|---|
| 1.1 Modelo E-R y normalización | 3 | `docs/modelo_datos.pdf` · `database/01_schema.sql` |
| 1.2 Restricciones, triggers y procedimientos | 3 | `database/02_constraints.sql`, `03_triggers.sql`, `04_procedures.sql` |
| 1.4 Dos reportes complejos | 2 | `database/05_reportes.sql` · vista `/admin/reportes` |
| 1.5 Seguridad, calidad y respaldos | 2 | `database/06_seguridad.sql` · `database/backup/` |
| 2.1 Responsive y mensajes de error | 4 | `app/static/css/aurora.css` · `docs/evidencias_ux/` |
| 2.3 Funcionalidades completas | 3 | Este README + prototipo funcionando |
| 2.4 Git colaborativo | 3 | Ramas, Pull Requests y `docs/bitacora_git.md` |
| 3.1 Diagrama de clases | 3 | `docs/diagrama_clases.png` |
| 3.2 Clases que representan el dominio | 2 | `app/dominio/` + `tests/` en verde |
| 3.3 Encapsulamiento, herencia, polimorfismo | 3 | `app/dominio/habitaciones.py` |
| 3.4 Organización y documentación | 2 | Docstrings, type hints y este README |

---

## 8. Las tres capas de validación

Cada regla de negocio se implementa **tres veces**, y eso es deliberado:

| Regla | Navegador | Python (POO) | PostgreSQL |
|---|---|---|---|
| Salida posterior a entrada | `min` dinámico en el `input date` | `Reserva.__init__` | `ck_reserva_fechas` |
| No reservar en el pasado | `min="hoy"` | Constructor de `Reserva` | `RES-001` en el procedimiento |
| Huéspedes ≤ capacidad | Máximo del `select` | `Reserva.confirmar()` | `RES-004` en el procedimiento |
| Sin solapamiento de fechas | Calendario con días ocupados | Consulta previa de disponibilidad | `EXCLUDE ex_habitacion_ocupada` |
| Cédula de 10 dígitos | `pattern="[0-9]{10}"` | Validador del formulario | `ck_usuario_cedula` |
| Contraseña nunca en texto plano | Solo se envía por el formulario | Hash antes de guardar | `SEG-001` en `trg_usuario_normaliza` |

La capa 1 da respuesta inmediata pero se puede saltar. La capa 2 concentra la regla y produce el mensaje que lee la persona. La capa 3 es la única que resiste un acceso directo por pgAdmin o dos usuarios simultáneos.

---

## 9. Equipo

| Integrante | Lidera | Aporta también en |
|---|---|---|
| *(nombre)* | Base de Datos | Repositorios Python y vista de reportes |
| *(nombre)* | Programación Orientada a Objetos | Blueprints y datos de prueba |
| *(nombre)* | Desarrollo Web Front End (UX/UI) | Plantillas Jinja y documentación |

Cada integrante lidera una asignatura pero aporta commits en las tres áreas: cualquiera del equipo debe poder responder sobre cualquier parte del proyecto.

---

## 10. Solución de problemas

**`No se pudo conectar a PostgreSQL`**
Verificar que el servicio de PostgreSQL esté corriendo y que `DB_PASSWORD` en `.env` sea correcta. Probar la misma contraseña en pgAdmin.

**`no password supplied`**
El archivo `.env` tiene `DB_PASSWORD` vacío. Completarlo y volver a correr `setup_db.py`.

**`extension "btree_gist" is not available`**
Falta el paquete `postgresql-contrib`. En Windows viene incluido con el instalador oficial de PostgreSQL.

**Las pruebas fallan pero la app funciona**
Las pruebas del dominio no usan la base de datos. Si fallan, el problema está en `app/dominio/`, no en PostgreSQL.

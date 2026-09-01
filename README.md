# Hotel Aurora — Sistema de Reservas y Gestión Hotelera

Proyecto Integrador de segundo nivel · PUCE TEC
Mateo Hidalgo · Isaac Carrión · Valeria Tobar

Este proyecto junta lo que vimos en tres materias: Programación Orientada a
Objetos, Base de Datos I y Desarrollo Web Front End.

---

## 1. El problema

El Hotel Aurora tiene 28 habitaciones y las maneja con un cuaderno y una hoja
de cálculo compartida. Eso les trae tres problemas: a veces venden la misma
habitación dos veces, no saben cuántas noches llenaron realmente en el mes, y
el precio de temporada alta lo aplica cada recepcionista como le parece.

Nuestro sistema cubre todo el recorrido: consultar disponibilidad, reservar,
confirmar, registrar la entrada y la salida, y sacar reportes para la gerencia.

Lo que más nos interesaba resolver era la doble venta. No quisimos que fuera
una validación más del programa, porque esas se pueden saltar. Lo pusimos en
la base de datos: cada habitación guarda el rango de fechas que tiene ocupado,
y PostgreSQL rechaza cualquier reserva que se cruce con otra. Aunque dos
personas la pidan en el mismo segundo, solo una pasa.

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

> El archivo `.env` guarda la contraseña, así que no se sube al repositorio.
> Lo que sí se sube es `.env.example`, que tiene los mismos campos pero vacíos
> para que cada uno ponga los suyos.

### 3.2 Crear la base de datos y cargar los datos

```bash
.venv\Scripts\python.exe setup_db.py
```

Ese comando crea la base `hotel_aurora` y corre los siete scripts en orden. Se
puede repetir cuantas veces haga falta, porque reconstruye todo desde cero.

### 3.3 Levantar la aplicación

```bash
.venv\Scripts\python.exe run.py
```

Abrir <http://127.0.0.1:5000>

### 3.4 Si todavía no existe el entorno virtual

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
├── docs/
│   ├── modelo_entidad_relacion.svg   Diagrama E-R (criterio 1.1)
│   ├── diagrama_clases.svg           Diagrama UML de clases (criterio 3.1)
│   ├── _diagramas.html               Fuente Mermaid para regenerar ambos
│   ├── _servidor_diagramas.py        Servidor temporal que los exporta a SVG
│   ├── manual_usuario.md             Cómo se usa el sistema, por tipo de usuario
│   ├── Manual_de_Uso_Aurora_ilustrado.pdf   El mismo manual con capturas paso a paso
│   ├── bitacora_git.md               Cómo nos repartimos el trabajo
│   ├── encuesta_usabilidad.md        La encuesta y sus resultados
│   └── evidencias_ux/                Capturas, respuestas e informe de usabilidad
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

### Regenerar los diagramas

Los diagramas se escriben en Mermaid dentro de `docs/_diagramas.html` y se exportan a SVG desde el navegador. Si cambian el modelo o las clases, hay que regenerarlos:

```powershell
.\.venv\Scripts\python.exe docs\_servidor_diagramas.py
```

Abrir <http://127.0.0.1:8899/docs/_diagramas.html>, esperar a que la consola del servidor confirme los dos `[OK]`, y cerrar con `Ctrl + C`. Los SVG quedan actualizados en `docs/`.

> Word e Illustrator importan SVG directamente y sin pérdida de calidad. Si necesitan PNG, abran el SVG en el navegador y usen clic derecho → *Guardar imagen como*.

---

## 7. Cómo el proyecto responde a la rúbrica

| Criterio | Puntos | Dónde está la evidencia |
|---|---|---|
| 1.1 Modelo E-R y normalización | 3 | `docs/modelo_entidad_relacion.svg` · `database/01_schema.sql` |
| 1.2 Restricciones, triggers y procedimientos | 3 | `database/02_constraints.sql`, `03_triggers.sql`, `04_procedures.sql` |
| 1.4 Dos reportes complejos | 2 | `database/05_reportes.sql` · vista `/admin/reportes` |
| 1.5 Seguridad, calidad y respaldos | 2 | `database/06_seguridad.sql` · `database/backup/` |
| 2.1 Responsive y mensajes de error | 4 | `docs/evidencias_ux/` (capturas, encuesta e informe) |
| 2.3 Funcionalidades completas | 3 | Este README + prototipo funcionando |
| 2.4 Git colaborativo | 3 | Ramas, Pull Requests y `docs/bitacora_git.md` |
| 3.1 Diagrama de clases | 3 | `docs/diagrama_clases.svg` |
| 3.2 Clases que representan el dominio | 2 | `app/dominio/` + `tests/` en verde |
| 3.3 Encapsulamiento, herencia, polimorfismo | 3 | `app/dominio/habitaciones.py` |
| 3.4 Organización y documentación | 2 | Docstrings, este README y `docs/manual_usuario.md` |

---

## 8. Las tres capas de validación

Cada regla de negocio se implementa **tres veces**, y eso es deliberado:

| Regla | Navegador | Python (POO) | PostgreSQL |
|---|---|---|---|
| Salida posterior a entrada | `min` dinámico en el `input date` | `Reserva.__init__` | `ck_reserva_fechas` |
| No reservar en el pasado | `min="hoy"` | `Reserva.validar_fecha_inicio()` | `RES-001` en el procedimiento |
| Huéspedes ≤ capacidad | Máximo del `select` | `Reserva.confirmar()` | `RES-004` en el procedimiento |
| Sin solapamiento de fechas | Calendario con días ocupados | Consulta previa de disponibilidad | `EXCLUDE ex_habitacion_ocupada` |
| Cédula de 10 dígitos | `pattern="[0-9]{10}"` | Validador del formulario | `ck_usuario_cedula` |
| Contraseña nunca en texto plano | Solo se envía por el formulario | Hash antes de guardar | `SEG-001` en `trg_usuario_normaliza` |

Lo hicimos así porque cada capa cubre algo distinto. La del navegador avisa al
instante mientras la persona escribe, pero se puede desactivar. La de Python es
donde vive la regla de verdad y de donde sale el mensaje que se lee en pantalla.
Y la de la base es la única que aguanta si alguien entra directo por pgAdmin o
si dos personas hacen lo mismo al mismo tiempo.

---

## 9. Equipo

| Integrante | Lidera | Aporta también en |
|---|---|---|
| Mateo Hidalgo | Base de Datos | Repositorios Python y vista de reportes |
| Isaac Carreon | Programación Orientada a Objetos | Blueprints y datos de prueba |
| Valeria Tobar | Desarrollo Web Front End (UX/UI) | Plantillas Jinja y documentación |

Cada uno se hizo cargo de una materia, pero los tres trabajamos en las tres
partes. La idea era que cualquiera pudiera explicar cualquier pedazo del
proyecto, no solo el suyo.

En `docs/bitacora_git.md` está el detalle de cómo nos repartimos el trabajo y
por qué el conteo de commits no quedó parejo.

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

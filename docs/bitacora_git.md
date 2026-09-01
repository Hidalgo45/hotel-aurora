# Bitácora de trabajo colaborativo con Git

> Criterio 2.4 de la rúbrica (3 puntos): *«trabajo colaborativo en ramas, distribución equitativa del trabajo, organización del repositorio y claridad en el manejo de versiones»*.

---

## 1. Estrategia de ramas

| Rama | Nace de | Se fusiona en | Propósito |
|---|---|---|---|
| `main` | — | — | Solo versiones estables. Se etiqueta `v1.0-sustentacion` el día de la defensa |
| `develop` | `main` | `main` | Integración diaria. Siempre debe arrancar sin errores |
| `feature/<area>-<tema>` | `develop` | `develop` | Trabajo nuevo. Ej: `feature/bd-triggers`, `feature/ux-catalogo` |
| `fix/<tema>` | `develop` | `develop` | Corrección de un bug detectado en integración |
| `release/v1.0` | `develop` | `main` y `develop` | Congelamiento previo a la sustentación |

**Reglas del equipo:**

1. El trabajo entra por una rama y un Pull Request, no directo a `main` ni a `develop`. La única excepción fueron las correcciones del último día, que explicamos más abajo.
2. Todo entra por Pull Request con **un revisor obligatorio distinto del autor**.
3. Antes de abrir el PR: `pytest -q` en verde.
4. El PR describe *qué* cambia y *por qué*, no solo qué archivos se tocaron.

---

## 2. Convención de commits

Formato: `tipo(área): descripción en imperativo`

- **Tipos:** `feat`, `fix`, `docs`, `style`, `refactor`, `test`, `chore`
- **Áreas:** `bd`, `poo`, `ux`, `infra`

Ejemplos:

```
feat(bd): agrega restriccion EXCLUDE que impide solapar reservas
feat(poo): implementa calcular_tarifa polimorfico en Suite y Familiar
fix(ux): corrige contraste del boton primario a 4.6:1 en modo claro
docs(bd): documenta politica de respaldo con pg_dump
test(poo): cubre penalizacion de cancelacion con menos de 48 horas
```

---

## 3. Reparto del trabajo

Cada integrante **lidera** una asignatura pero **aporta commits en las tres áreas**. El error que cuesta puntos es que cada uno toque solo su materia: si un docente pregunta a quien hizo el frontend sobre los triggers y no sabe responder, se pierde el criterio 4.4.

| Integrante | Lidera | Aporta también en | Revisa PRs de |
|---|---|---|---|
| Mateo Hidalgo | Base de Datos: DDL, constraints, triggers, procedimientos, reportes, respaldos | Repositorios Python, vista `/admin/reportes` | Valeria Tobar |
| Isaac Carreon | POO: dominio, herencia, polimorfismo, tests, diagrama de clases | Blueprints y formularios, datos de prueba | Mateo Hidalgo |
| Valeria Tobar | UX/UI: sistema de diseño, responsive, mensajes, encuesta | Plantillas Jinja, clase `Servicio`, documentación | Isaac Carreon |

---

## 4. Cómo quedó repartido el trabajo

Esta es la salida real del historial al cierre del proyecto:

```
git shortlog -sn --all

    26  Mateo Hidalgo
     4  Isaac Carrion
     3  Valeria Tobar
```

En total, 33 commits entre el 30 de agosto y el 1 de septiembre de 2026. El detalle
completo, commit por commit, está en `docs/historial_commits.csv`.

### Por qué el reparto no es parejo

El número de commits no muestra bien cuánto puso cada uno, y preferimos
explicarlo antes que dejarlo pasar.

Trabajamos casi todo el tiempo en una sola computadora. A Isaac se le dañó
la suya durante el fin de semana, y buena parte del proyecto salió de
sesiones en las que estábamos juntos frente a la misma pantalla, unas veces
en persona y otras conectados por escritorio remoto. En esas sesiones la
cuenta que quedaba guardada en Git era la del dueño del equipo, no siempre
la de quien estaba resolviendo el problema.

Donde sí pudimos separarlo, lo separamos. Las capturas de pantalla se
subieron desde la computadora de Valeria con su propia cuenta, y las pruebas
del dominio con la de Isaac.

También pasó que el nombre configurado en Git cambió entre sesiones, así que
Valeria aparecía con tres nombres distintos aunque siempre fuera el mismo
correo. Lo arreglamos con un archivo `.mailmap`, que le dice a Git que esas
etiquetas son la misma persona sin tocar los commits.

### Quién se encargó de qué

| Integrante | De qué se hizo cargo |
|---|---|
| Mateo Hidalgo | La base de datos completa: el modelo, las restricciones, los disparadores, los procedimientos, los reportes, los respaldos y el envío de correos |
| Isaac Carrión | La parte de objetos: las clases del dominio, la herencia, el polimorfismo y las pruebas |
| Valeria Tobar | El diseño de la interfaz, que funcione en celular, los mensajes de error y las pruebas con usuarios |

Cada uno lideró su materia, pero los tres podemos responder por cualquier
parte del proyecto.


**Las excepciones del último día.** Los tres últimos commits entraron
directamente a `develop`: la unificación de identidades con `.mailmap`, el
cierre de la documentación y una corrección de la capacidad de las
habitaciones familiares. Fueron correcciones puntuales hechas la tarde
anterior a la sustentación, cuando ya trabajábamos sobre el mismo equipo y
abrir un Pull Request para revisarse uno mismo no aportaba nada. Lo
anotamos aquí en lugar de disimularlo.

---

## 5. Los cambios que entraron por Pull Request

Casi todo el trabajo pasó por una rama aparte y un Pull Request, que es
donde queda registrado qué se cambió y por qué.

| # | Rama | Entró en | Qué aportó |
|---|---|---|---|
| 1 | `feature/ux-ajustes-visuales` | `main` | Arregla las etiquetas del buscador, que salían en blanco sobre fondo blanco |
| 2 | `feature/ux-capturas` | `develop` | Las capturas de la página en celular, tablet y computador |
| 3 | `fix/ux-nombres-y-navegacion` | `develop` | Ordena los nombres de las capturas |
| 4 | `fix/ux-nombres-y-navegacion` | `develop` | Corrige un enlace repetido en el menú y documenta la prueba de respaldo |
| 5 | `feature/correo-comprobante` | `develop` | El envío del comprobante por correo |
| 6 | `feature/correo-comprobante` | `develop` | Quita las credenciales que se veían en la pantalla de acceso y corrige la ortografía |
| 7 | `feature/poo-pruebas` | `develop` | Pruebas de los servicios incluidos y del check-out |
| 8 | `feature/poo-cobertura` | `develop` | Más pruebas: fechas, servicios y estado de las habitaciones |
| 9 | `feature/ux-resultados-encuesta` | `develop` | Los resultados de la encuesta y las dos mejoras que salieron de ahí |

Los nueve quedaron fusionados y no dejamos ninguna rama abierta.

**Una equivocación que vale la pena contar:** el primer Pull Request lo
mandamos a `main` en vez de a `develop`, porque GitHub propone `main` por
defecto. Lo notamos cuando los cambios no le llegaban a los demás. Después
de eso cambiamos la rama predeterminada del repositorio a `develop` y no
volvió a pasar.

---

## 6. Comandos de referencia

```bash
# Iniciar el repositorio (una sola vez, quien lo cree)
git init
git add .
git commit -m "chore(infra): estructura inicial del proyecto"
git branch -M main
git remote add origin <url-del-repositorio>
git push -u origin main
git checkout -b develop
git push -u origin develop

# Trabajo diario de cada integrante
git checkout develop
git pull
git checkout -b feature/bd-triggers
# ... trabajar y commitear ...
git push -u origin feature/bd-triggers
# abrir el Pull Request hacia develop desde la web

# Congelar para la sustentación
git checkout -b release/v1.0 develop
git checkout main
git merge release/v1.0
git tag -a v1.0-sustentacion -m "Version presentada en la sustentacion"
git push origin main --tags
```

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

1. Nadie hace `push` directo a `main` ni a `develop`.
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

## 4. Evidencia de distribución equitativa

Ejecutar la semana previa a la entrega y **pegar la salida aquí abajo**:

```bash
git shortlog -sn --all
git log --pretty=format:"%h|%an|%ad|%s" --date=short --all > docs/historial_commits.csv
```

**Meta: ningún integrante por debajo del 25 % de los commits.** Si alguien va bajo, se le reasignan tareas *antes* de la entrega, no después.

### Salida del `git shortlog -sn` (pegar aquí)

```
(pendiente — ejecutar antes de la entrega)
```

---

## 5. Registro de Pull Requests

| # | Rama | Autor | Revisor | Qué aporta | Fecha |
|---|---|---|---|---|---|
| | | | | | |
| | | | | | |
| | | | | | |

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

# Encuesta de usabilidad y diseño responsive

> Criterio 2.1 de la rúbrica (4 puntos): *«el producto es capaz de adaptarse a diferentes dispositivos, aplicando buenas prácticas de responsive design, y el manejo de mensajes de error claros»*.

**Muestra:** 10 personas ajenas al equipo — 4 en móvil, 3 en tablet, 3 en escritorio.
**Duración por persona:** 10–12 minutos.
**Orden:** primero las tareas (Parte A), después el cuestionario (Partes B y C).

---

## Parte A — Tareas cronometradas

El participante trabaja solo. El observador **no ayuda**: solo anota. Si la persona se traba más de 90 segundos, se registra como tarea fallida y se pasa a la siguiente.

| # | Tarea | Éxito esperado | Qué se registra |
|---|---|---|---|
| 1 | Encontrar una suite libre del 10 al 14 de septiembre | < 45 s | Tiempo, número de clics, si pidió ayuda |
| 2 | Completar una reserva para 2 adultos y 1 niño | < 2 min | Errores cometidos, en qué punto dudó |
| 3 | Provocar un error a propósito: poner la salida antes que la entrada | Entiende el mensaje sin ayuda | ¿Supo qué corregir? |
| 4 | Encontrar el código de su reserva | < 30 s | Ruta que siguió |
| 5 | Cancelar la reserva | Encuentra el aviso de penalidad | ¿Notó el cargo antes de confirmar? |

### Hoja de registro del observador

| Participante | Dispositivo | T1 | T2 | T3 | T4 | T5 | Tareas completadas | Observaciones |
|---|---|---|---|---|---|---|---|---|
| P01 | | | | | | | /5 | |
| P02 | | | | | | | /5 | |
| P03 | | | | | | | /5 | |
| P04 | | | | | | | /5 | |
| P05 | | | | | | | /5 | |
| P06 | | | | | | | /5 | |
| P07 | | | | | | | /5 | |
| P08 | | | | | | | /5 | |
| P09 | | | | | | | /5 | |
| P10 | | | | | | | /5 | |

---

## Cómo crear el formulario en Google Forms

En vez de copiar las 17 preguntas a mano, usa el script `crear_formulario_encuesta.gs` que está en esta misma carpeta:

1. Entra a <https://script.google.com> con tu cuenta de Google
2. **Nuevo proyecto**
3. Borra lo que aparezca y pega el contenido completo del archivo `.gs`
4. Guarda con `Ctrl + S` y presiona **Ejecutar**
5. La primera vez Google pide permisos: *Revisar permisos* → tu cuenta → *Configuración avanzada* → *Ir a (nombre del proyecto)* → **Permitir**
6. Abre **Ver → Registro de ejecución**. Ahí salen los dos enlaces: el de edición y el que se comparte con los participantes

El formulario queda con tres secciones, barra de progreso y las diez afirmaciones del SUS en escala de 1 a 5, en el orden correcto.

### Vincular la hoja de respuestas

En el formulario, pestaña **Respuestas** → ícono verde de hoja de cálculo. Las respuestas caen ahí automáticamente.

### Calcular el puntaje SUS

Con el orden de preguntas que genera el script, las diez afirmaciones quedan en las columnas **E** a **N**. En la columna **S** de la primera fila de respuestas, pega esta fórmula y arrástrala hacia abajo:

```
=((E2-1)+(5-F2)+(G2-1)+(5-H2)+(I2-1)+(5-J2)+(K2-1)+(5-L2)+(M2-1)+(5-N2))*2.5
```

El promedio del grupo sale con `=PROMEDIO(S2:S11)`.

> Verifica que la columna E sea realmente la afirmación 1 antes de arrastrar. Si agregaste o quitaste alguna pregunta, las letras se corren.

---

## Parte B — Cuestionario SUS adaptado

Escala: **1 = muy en desacuerdo · 5 = muy de acuerdo**

| # | Afirmación | 1 | 2 | 3 | 4 | 5 |
|---|---|---|---|---|---|---|
| 1 | Me resultó fácil reservar una habitación en este dispositivo | | | | | |
| 2 | El sistema me pareció innecesariamente complejo | | | | | |
| 3 | Los textos y botones se leían bien sin necesidad de hacer zoom | | | | | |
| 4 | Necesité ayuda de alguien para completar la reserva | | | | | |
| 5 | Las secciones del sitio se comportan de forma coherente entre sí | | | | | |
| 6 | Encontré incoherencias o elementos fuera de lugar en la pantalla | | | | | |
| 7 | Creo que cualquier persona aprendería a usarlo rápidamente | | | | | |
| 8 | Me sentí inseguro/a al confirmar la reserva | | | | | |
| 9 | Los mensajes de error me dijeron con claridad cómo corregir el problema | | | | | |
| 10 | Tuve que desplazarme horizontalmente o buscar contenido cortado | | | | | |

### Cómo se calcula el puntaje SUS

1. Preguntas **impares** (1, 3, 5, 7, 9): `respuesta − 1`
2. Preguntas **pares** (2, 4, 6, 8, 10): `5 − respuesta`
3. Sumar los diez valores y **multiplicar por 2.5** → puntaje sobre 100

**Referencia:** 68 es el promedio de la industria. Por encima de 80 se considera excelente.

---

## Parte C — Preguntas específicas de responsive

1. ¿En qué dispositivo y navegador realizaste la prueba? (marca y tamaño de pantalla)
2. ¿Hubo algún botón difícil de presionar con el dedo? ¿Cuál?
3. ¿Alguna imagen o tabla se salió de la pantalla?
4. Del 1 al 10, ¿qué tan probable es que recomiendes este sitio?
5. Si pudieras cambiar una sola cosa, ¿cuál sería? *(respuesta abierta)*

---

## Consolidado de resultados

| Dispositivo | Participantes | SUS promedio | Tareas completadas | Tiempo medio T2 |
|---|---|---|---|---|
| Móvil (375 px) | 4 | | | |
| Tablet (768 px) | 3 | | | |
| Escritorio (1440 px) | 3 | | | |
| **General** | **10** | | | |

---

## Resultados obtenidos — 31 de agosto de 2026

**33 respuestas** recogidas mediante formulario de Google. El análisis se
reproduce con `docs/evidencias_ux/analizar_encuesta.py` sobre el archivo
`formulario_hotel.csv`.

### El puntaje SUS no resultó utilizable, y esa es una conclusión válida

| Medida | Valor |
|---|---|
| SUS promedio | 57.5 / 100 |
| Mediana | 52.5 |
| Rango | 47.5 – 100 |

Antes de reportar ese número revisamos la consistencia interna de las respuestas:

- El **77 %** marcó a la vez «me resultó fácil reservar» (4-5) y «el sistema me
  pareció innecesariamente complejo» (4-5). Son afirmaciones opuestas: no pueden
  ser ciertas las dos.
- El **39 %** marcó exactamente el mismo número en las diez afirmaciones.

Quien responde 5 en todas obtiene exactamente 50 puntos de SUS, y la mediana de
52.5 confirma que la mayoría hizo eso. El puntaje refleja que buena parte
respondió sin leer, no la usabilidad del sistema.

**Esa detección es justamente para lo que sirve el diseño del SUS.** Las
afirmaciones alternan sentido positivo y negativo para que una respuesta
automática se delate. El instrumento funcionó; lo que no sirve es usar ese
promedio como medida de usabilidad. Por eso lo descartamos y nos apoyamos en el
dato conductual.

### Tareas completadas sin ayuda — el dato que sí mide

Esta pregunta no depende de interpretar una escala: la persona marca lo que
efectivamente logró hacer.

| Tarea | Lo lograron | % |
|---|---|---|
| Buscar habitaciones libres | 27 / 33 | 81.8 % |
| Completar una reserva | 24 / 33 | 72.7 % |
| Entender el mensaje de error | 24 / 33 | 72.7 % |
| **Volver a encontrar el código de la reserva** | 19 / 33 | **57.6 %** |
| **Cancelar la reserva** | 14 / 33 | **42.4 %** |

Las dos últimas filas motivaron los cambios de la sección siguiente.

### Participantes por dispositivo

| Dispositivo | Participantes |
|---|---|
| Celular | 16 |
| Computador | 7 |
| Tablet | 6 |

---

## Las dos mejoras que aplicamos

Esta es la parte que convierte la encuesta en **evidencia de diseño centrado en
el usuario** y no en un trámite.

### Mejora 1 — El botón de cancelar no tenía nombre en móvil

- **Hallazgo:** solo el **42.4 %** (14 de 33) logró cancelar su reserva.
- **Causa encontrada:** en `mis_reservas.html` la acción vivía en la última
  columna de la tabla, sin encabezado (`<th></th>`) y con `data-etiqueta=""`.
  En móvil, donde la tabla se convierte en tarjetas, el botón aparecía suelto
  al final sin ninguna etiqueta que dijera para qué servía. Como 16 de los 33
  participantes usaron celular, ahí estaba el grueso del problema.
- **Qué cambiamos:** la columna pasa a llamarse «Acciones» y la celda lleva
  `data-etiqueta="Acciones"`, de modo que en móvil el botón sale bajo un rótulo
  visible. El texto pasa de «Cancelar» a «Cancelar reserva».
- **Archivos:** `app/templates/cuenta/mis_reservas.html`
- **Verificación:** a 375 px el botón mide 44 px de alto, muestra la etiqueta
  «Acciones» encima y no genera desplazamiento horizontal.

### Mejora 2 — No había camino de vuelta al código de la reserva

- **Hallazgo:** solo el **57.6 %** (19 de 33) volvió a encontrar su código.
- **Causa encontrada:** desde la página de confirmación no existía ningún enlace
  hacia «Mis reservas». La única vía era el menú de navegación, que en móvil
  está plegado dentro del botón de hamburguesa.
- **Qué cambiamos:** se agrega el botón **«Ver todas mis reservas»** entre las
  acciones de la confirmación, y una línea al pie que dice dónde recuperar el
  código si se pierde.
- **Archivos:** `app/templates/publico/confirmacion.html`

### Corrección adicional detectada al verificar

Al revisar la página de confirmación encontramos que **«Total de la reserva»
mostraba solo el alojamiento**, sin los servicios contratados, mientras que el
comprobante enviado por correo sí los sumaba. La misma reserva mostraba $90.00
en pantalla y $152.00 en el correo, y el saldo pendiente salía mal en
consecuencia.

Se corrigió desglosando alojamiento y servicios por separado antes del total.
**Archivos:** `app/blueprints/publico.py`, `app/templates/publico/confirmacion.html`

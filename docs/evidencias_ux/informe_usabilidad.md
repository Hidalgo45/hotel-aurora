# Informe de usabilidad — Hotel Aurora

**Proyecto Integrador · PUCE TEC · 31 de agosto de 2026**
Mateo Hidalgo · Isaac Carrión · Valeria Tobar

---

## Qué queríamos averiguar

Nosotros hicimos la página, así que ya sabemos dónde está todo. Eso es
justamente el problema: no podemos juzgar si es fácil de usar, porque para
nosotros siempre lo va a ser.

Por eso la pusimos a prueba con gente que no la había visto nunca, y les
pedimos que hicieran cinco cosas sin que nadie les ayudara:

1. Buscar habitaciones libres para unas fechas
2. Completar una reserva y quedarse con el código
3. Poner más huéspedes de los que caben, a propósito, para ver si entendían
   el mensaje de error
4. Volver a encontrar el código de su reserva
5. Cancelar la reserva

Después les pasamos un cuestionario.

---

## A quiénes se lo aplicamos

Respondieron **33 personas**, todas ajenas al equipo.

| Dispositivo | Personas |
|---|---|
| Celular | 16 |
| Computador | 7 |
| Tablet | 6 |

Que la mitad lo probara desde el celular terminó siendo importante, porque
ahí es donde encontramos el problema más grande.

---

## El cuestionario que usamos

Usamos el **SUS (System Usability Scale)**, que son diez afirmaciones que la
persona califica del 1 al 5. Es un cuestionario estándar que se usa desde los
años ochenta, y su gracia es que da un número del 0 al 100 comparable con
otros sistemas. El promedio de la industria está en 68.

Una particularidad: las afirmaciones van alternando entre positivas y
negativas. La primera dice «me resultó fácil reservar» y la segunda dice «el
sistema me pareció innecesariamente complejo». Eso no es un descuido de
redacción, está hecho a propósito, y más adelante se va a ver para qué sirve.

---

## Lo que salió, y por qué no lo usamos

El puntaje promedio dio **57.5 sobre 100**, con una mediana de 52.5.

Antes de reportar ese número revisamos si las respuestas tenían sentido entre
sí, y encontramos esto:

- **El 77 % dijo al mismo tiempo** que reservar le resultó fácil (4 o 5) **y**
  que el sistema le pareció innecesariamente complejo (4 o 5). Las dos cosas
  no pueden ser ciertas a la vez.
- **El 39 % marcó exactamente el mismo número** en las diez afirmaciones.

Hay un detalle que lo explica todo: quien marca 5 en las diez preguntas
obtiene exactamente 50 puntos de SUS. Y nuestra mediana fue 52.5. O sea que
la mayoría marcó todo alto pensando que «más alto es mejor», sin leer que la
mitad de las frases estaban escritas al revés.

**Ese 57.5 no mide qué tan usable es nuestra página. Mide que la gente
respondió rápido.**

Para eso servía que las afirmaciones alternaran. El cuestionario hizo su
trabajo: nos avisó de que no podíamos confiar en ese número. Así que lo
descartamos y nos fuimos al otro dato.

---

## El dato que sí sirvió

La otra pregunta no pedía opinión, pedía marcar qué habían logrado hacer.
Eso no depende de cómo se interprete una escala.

| Lo que había que hacer | Lo lograron | Porcentaje |
|---|---|---|
| Buscar habitaciones libres | 27 de 33 | 82 % |
| Completar una reserva | 24 de 33 | 73 % |
| Entender el mensaje de error | 24 de 33 | 73 % |
| Volver a encontrar el código | 19 de 33 | **58 %** |
| Cancelar la reserva | 14 de 33 | **42 %** |

Las tres primeras están bien. Las dos últimas no.

**Menos de la mitad pudo cancelar su propia reserva.** Ese fue el hallazgo que
más nos sorprendió, porque el botón existía y nosotros lo veíamos sin
problema.

---

## Qué encontramos al buscar la causa

### Problema 1: el botón de cancelar no tenía nombre en el celular

Fuimos a ver el código y encontramos por qué. La lista de reservas es una
tabla, y en el celular esa tabla se transforma en tarjetas, poniendo el
nombre de cada columna al lado de su dato.

El botón de cancelar estaba en la última columna, y esa columna no tenía
nombre. Así que en el celular aparecía un botón suelto al final de la tarjeta,
sin nada que dijera para qué era. En el computador se entendía por el
contexto; en el celular no.

Como 16 de las 33 personas lo probaron desde el celular, ahí estaba la mayor
parte del 58 % que no lo logró.

### Problema 2: no había manera de volver

Después de reservar, uno queda en la página de confirmación con su código.
Pero desde ahí no había ningún enlace para volver a ver sus reservas. La
única forma era el menú de arriba, que en el celular está escondido dentro
del botón de las tres rayas.

Quien cerraba esa página perdía el código de vista y no sabía cómo volver.

---

## Qué cambiamos

**Para el problema 1.** Le pusimos nombre a la columna: ahora se llama
«Acciones», y el botón dice «Cancelar reserva» completo en vez de solo
«Cancelar». En el celular el botón aparece debajo de un rótulo que se lee.

Lo verificamos a 375 píxeles de ancho: el botón mide 44 píxeles de alto, que
es el mínimo recomendado para que se pueda tocar bien con el dedo, y la
página no se desplaza hacia los lados.

**Para el problema 2.** Agregamos el botón «Ver todas mis reservas» en la
página de confirmación, y una línea al pie que dice dónde encontrar el código
si se pierde.

---

## Algo más que apareció de camino

Mientras verificábamos los cambios notamos que la página de confirmación
mostraba «Total de la reserva: $90.00», pero esa misma reserva tenía $62.00 en
servicios adicionales que no se estaban sumando. El comprobante que llega por
correo sí los sumaba, así que la misma reserva decía $90.00 en la pantalla y
$152.00 en el correo. El saldo pendiente también salía mal.

Lo corregimos: ahora la página separa el alojamiento de los servicios y suma
los dos antes de mostrar el total. Los dos lugares dicen lo mismo.

No lo buscábamos, pero apareció por ir a revisar el código con una pregunta
concreta en la mano.

---

## Qué aprendimos

**Una encuesta puede salir mal y aun así servir.** El puntaje no nos dijo nada
sobre la página, pero el diseño del cuestionario nos permitió darnos cuenta a
tiempo. Si lo hubiéramos reportado sin revisar, habríamos presentado un número
inventado sin saberlo.

**Preguntar qué hizo la gente funciona mejor que preguntar qué opina.** Las
opiniones se contradijeron entre sí. La pregunta de qué tareas habían logrado
completar nos dio directamente los dos problemas.

**Lo que a nosotros nos parece obvio, no lo es.** El botón de cancelar estuvo
ahí todo el tiempo y nosotros lo encontrábamos siempre. Hizo falta que 19
personas no lo encontraran para que fuéramos a mirar el código.

---

## Cómo comprobar estos números

Los datos crudos están en `formulario_hotel.csv`, en esta misma carpeta, sin
ningún dato personal de los participantes.

El cálculo se puede repetir con:

```
.venv\Scripts\python.exe docs\evidencias_ux\analizar_encuesta.py
```

Ese script vuelve a leer las respuestas y saca el puntaje, el desglose por
dispositivo y el conteo de tareas completadas.

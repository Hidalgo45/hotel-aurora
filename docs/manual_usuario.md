# Manual de usuario — Hotel Aurora

Este manual explica cómo usar el sistema. Está dividido por tipo de usuario,
porque no todos ven ni pueden hacer lo mismo.

---

## Los tres tipos de usuario

**Huésped.** La persona que quiere alojarse. Es el único tipo de cuenta que
uno mismo puede crear desde la página, con el botón *Crear cuenta*. Reserva
para sí misma y solo ve sus propias reservas.

**Recepcionista.** El personal del mostrador. Ve todas las reservas del hotel
y se encarga del día a día: confirmar, registrar entradas y salidas, marcar
a quien no se presentó. Puede consultar el estado de las habitaciones pero no
cambiarlo a mano.

**Administrador.** La gerencia. Hace todo lo del recepcionista y además puede
cambiar el estado de una habitación manualmente y entrar a los reportes.

### Qué puede hacer cada uno

| | Huésped | Recepción | Administrador |
|---|---|---|---|
| Ver las habitaciones y consultar disponibilidad | Sí | Sí | Sí |
| Reservar desde la página | Sí | No | No |
| Ver sus propias reservas | Sí | — | — |
| Ver todas las reservas del hotel | No | Sí | Sí |
| Confirmar, registrar entrada y salida | No | Sí | Sí |
| Cancelar una reserva | Solo las suyas | Cualquiera | Cualquiera |
| Reenviar el comprobante por correo | Solo las suyas | Cualquiera | Cualquiera |
| Entrar al tablero de gestión | No | Sí | Sí |
| Cambiar el estado de una habitación a mano | No | No | Sí |
| Ver los reportes y descargarlos | No | No | Sí |

El personal del hotel no puede reservar desde la parte pública. Si lo intenta,
el sistema lo manda al panel de gestión con un aviso. Lo hicimos así para
separar lo que hace un huésped por su cuenta de lo que hace el hotel por
dentro.

---

## Guía para el huésped

### Buscar una habitación

Al entrar a la página, lo primero que aparece es el buscador, con el título
*¿Qué días piensa viajar?*

1. Elige la fecha de entrada y la de salida. No deja escoger días que ya
   pasaron ni una salida anterior a la entrada.
2. Indica cuántas personas van a ser.
3. Presiona **Buscar habitaciones**.

Solo aparecen las habitaciones libres en esas fechas. Cada tarjeta muestra el
tipo, cuánta gente admite, el precio por noche y cuántas quedan de ese tipo.

Hay tres tipos:

| Tipo | Personas | Precio por noche | Cómo se cobra |
|---|---|---|---|
| Estándar | 2 | $45.00 | El precio por cada noche |
| Familiar | 5 | $65.00 | El precio más un cargo por cada cama extra |
| Suite | 3 | $85.00 | 25 % más cara, con 10 % de descuento si te quedas 5 noches o más |

Las tres incluyen Wi-Fi, televisión y parqueadero sin costo.

### Crear una cuenta

Se puede mirar el catálogo sin cuenta, pero para reservar hace falta una.
Se piden cédula, nombres, apellidos, correo, teléfono, fecha de nacimiento y
una contraseña.

El sistema no acepta cédulas que no tengan diez dígitos, correos mal escritos
o ya registrados, ni personas menores de dieciocho años.

### Reservar

1. En la habitación que elegiste, presiona **Ver disponibilidad**.
2. Ajusta las fechas y cuántos adultos y niños van. El precio se recalcula
   solo mientras cambias.
3. Si quieres, marca los servicios adicionales. Algunos se cobran por cada
   noche y otros una sola vez.
4. Presiona **Confirmar reserva**.

Aparece una página con tu código, que se ve así: `RSV-20260831-0057`. **Ese
código es lo que hay que guardar**, porque te lo van a pedir al llegar.

Al mismo tiempo te llega un correo con el comprobante: las fechas, el detalle
de lo que vas a pagar y las condiciones para cancelar.

Si el correo no llega, tu reserva igual quedó hecha. En la misma página hay un
botón para volver a enviártelo.

### Ver tus reservas y cancelar

En el menú, la opción **Mis reservas** muestra todas las tuyas con su estado.
Desde ahí puedes cancelar, o desde la página de la reserva.

**Sobre las cancelaciones:** no se cobra nada si cancelas con más de 48 horas
de anticipación. Si cancelas después, se aplica un cargo del 20 % del total.
El sistema te muestra el monto exacto antes de que confirmes, nunca después.

Una reserva a la que ya se le registró la entrada no se puede cancelar.

---

## Guía para recepción

Al iniciar sesión con una cuenta de recepción o de administrador, el menú
cambia y aparece la opción **Tablero**.

### El tablero

Muestra cuatro números del día: cuántas habitaciones están ocupadas, cuántas
personas llegan hoy, cuántas se van y cuánto se ha facturado en el mes.

Debajo están las llegadas de los próximos siete días, con un botón para
registrar la entrada directamente. Más abajo, cuántas habitaciones quedan
libres de cada tipo y un registro de los últimos movimientos.

### Gestionar las reservas

En **Reservas** está la lista completa. Se puede buscar por código o por
nombre del huésped, y filtrar por estado.

Cada reserva pasa por estas etapas:

| Estado | Qué significa | Qué se puede hacer |
|---|---|---|
| Pendiente | El huésped la hizo pero aún no se confirma | Confirmar o cancelar |
| Confirmada | El hotel la aceptó y apartó la habitación | Registrar entrada o cancelar |
| Check In | El huésped ya está alojado | Registrar salida |
| Check Out | Ya se fue | Nada |
| Cancelada | Se anuló | Nada |
| No Show | No se presentó | Nada |

**Algo que pasa solo:** cada vez que cambias el estado de una reserva, la
habitación se actualiza sin que nadie la toque. Al confirmar queda *reservada*,
al registrar la entrada queda *ocupada*, y al registrar la salida pasa a
*limpieza*. Todo eso queda anotado con la hora en el registro del tablero.

### Ver las habitaciones

En **Inventario** aparece cada habitación con su piso, su tipo y cómo está.
Recepción puede mirarlo pero no cambiarlo: el estado se mueve solo cuando
avanza una reserva.

---

## Guía para el administrador

Puede hacer todo lo anterior y dos cosas más.

### Cambiar el estado de una habitación

Solo el administrador puede hacerlo, y únicamente entre tres opciones:

- **Disponible**, lista para vender
- **Limpieza**, ocupada por el personal de aseo
- **Mantenimiento**, fuera de servicio y sin aparecer en el catálogo

No se puede marcar una habitación como *ocupada* o *reservada* a mano. Esos
dos estados solo aparecen cuando una reserva avanza. Lo hicimos así para que
el inventario nunca diga algo distinto a lo que dicen las reservas.

### Los reportes

En **Reportes** hay dos, y los dos se pueden descargar en formato de hoja de
cálculo.

**Ocupación e ingresos.** Responde qué tipo de habitación deja más dinero y en
qué mes. Muestra cuántas noches se vendieron de cada tipo, cuántas había
disponibles, el porcentaje de ocupación, lo facturado y el precio promedio
por noche.

Lo interesante no es el porcentaje solo, sino cruzarlo con el precio promedio:
un tipo de habitación puede llenarse menos y aun así dejar más plata por noche.

**Ranking de clientes.** Muestra quiénes son los huéspedes que más han gastado,
cuántas veces han venido, cuántas noches se han quedado, cuánto gastaron en
servicios aparte y si quedaron debiendo algo.

---

## Problemas comunes

| Lo que ves | Por qué pasa | Qué hacer |
|---|---|---|
| «Inicia sesión para continuar con tu reserva» | Intentaste reservar sin tener cuenta | Crea una o entra; el sistema te devuelve a la misma habitación |
| «Tu cuenta no tiene permiso para entrar a esa sección» | Un huésped intentó entrar al panel | Es normal, esa parte es solo para el personal |
| «El personal del hotel crea reservas desde el panel de gestión» | Recepción intentó reservar desde la parte pública | Hay que usar el panel |
| «Seleccionaste 7 huéspedes y esta habitación admite 2» | Se pasó de la capacidad | Bajar el número de personas o elegir otro tipo |
| «Ya está reservada en esas fechas» | Alguien más la tomó primero | Cambiar fechas o elegir otra habitación |
| El catálogo sale vacío | No hay nada libre en ese rango | Ampliar las fechas o pedir menos personas |
| No llega el comprobante | Es problema del correo, no de la reserva | Usar el botón para reenviarlo |

---

## Cuentas para probar

Todas usan la contraseña `aurora123`.

| Correo | Tipo de usuario |
|---|---|
| `mateo@aurora.ec` | Administrador |
| `valeria@aurora.ec` | Recepción |
| `isaac@aurora.ec` | Recepción |

Estas credenciales están aquí, en la documentación del proyecto, y no se
muestran en la página. Al principio las teníamos visibles en la pantalla de
acceso y nos dimos cuenta de que cualquiera podía entrar como administrador,
así que las quitamos.

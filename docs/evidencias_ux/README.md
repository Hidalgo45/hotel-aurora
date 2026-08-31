# Evidencias de diseño responsive

Capturas de la interfaz en los tres tamaños de pantalla que exige el criterio 2.1 de la rúbrica.

## Archivos

| Archivo | Vista | Ancho real de la captura | Comportamiento que evidencia |
|---|---|---|---|
| `01_home_movil.png` | Inicio | 470 px | Buscador apilado, una columna |
| `01_home_tablet.png` | Inicio | 952 px | Buscador en dos columnas |
| `01_home_escritorio.png` | Inicio | 1170 px | Hero y buscador lado a lado |
| `02_catalogo_movil.png` | Catálogo | 470 px | Tarjetas en una columna |
| `02_catalogo_tablet.png` | Catálogo | 947 px | Tarjetas en dos columnas |
| `02_catalogo_escritorio.png` | Catálogo | 1172 px | Tarjetas en tres columnas |
| `03_reserva_movil.png` | Formulario de reserva | 502 px | Campos a ancho completo |
| `03_reserva_tablet.png` | Formulario de reserva | 947 px | Dos campos por fila |
| `03_reserva_escritorio.png` | Formulario de reserva | 1157 px | Formulario y resumen lado a lado |
| `04_error_capacidad_movil.png` | Error de capacidad | 485 px | **Mensaje de error accionable** |
| `05_confirmacion_movil.png` | Confirmación | 472 px | Código de reserva y resumen |
| `06_admin_reportes_escritorio.png` | Reportes | 1167 px | Tabla con desplazamiento propio |
| `07_admin_tablero_tablet.png` | Tablero admin | 950 px | Indicadores reorganizados |
| `informe_capturas.pdf` | — | — | Informe agrupado por tamaño |

## Por qué los nombres dicen «movil / tablet / escritorio» y no «375 / 768 / 1440»

Las capturas se tomaron a anchos aproximados (entre 470 y 502 px para móvil, alrededor de 950 para tablet y de 1170 para escritorio), no a los valores exactos de la guía. Los **puntos de quiebre igual se cruzan correctamente** —por debajo de 576 px se activa el diseño de una columna, por encima de 992 px el de escritorio—, así que las capturas sí demuestran la adaptación.

Nombrar los archivos con un ancho que no corresponde al de la imagen sería declarar algo que la evidencia no respalda. Por eso se usa la categoría de dispositivo, que sí es exacta.

## Verificación aplicada a cada captura

- [x] Sin desplazamiento horizontal
- [x] Sin texto cortado ni encimado
- [x] Los mensajes de error se ven completos
- [ ] Capturas de página completa incluyendo la barra de navegación *(pendiente en las de móvil)*

## Mejoras aplicadas tras revisar las capturas

### Barra de navegación con dos enlaces llamados igual

**Hallazgo.** En `01_home_escritorio.png` se ve que, con sesión de personal iniciada, la barra mostraba: *Habitaciones · Tablero · Reservas · Habitaciones · Reportes*. El mismo texto llevaba a dos sitios distintos: el catálogo público y la gestión interna. Además, la pantalla de destino del segundo ya se titulaba «Inventario de habitaciones», así que la barra contradecía a la propia página.

**Cambio.** El enlace de gestión pasa a llamarse **Inventario**, que coincide con el título de su pantalla, y se agrega un separador visual entre el catálogo público y el bloque de gestión.

**Dónde.** `app/templates/base.html` y `app/static/css/aurora.css`.

## Pendientes

1. **Rehacer `04_error_capacidad_movil.png`**: fue tomada con una versión antigua de la hoja de estilos en caché, por lo que el botón «Confirmar reserva» aparece en azul de Bootstrap y no en el color de la marca. El código actual es correcto; solo hay que recapturar forzando la recarga con `Ctrl + Shift + R`.
2. **Rehacer las capturas de móvil como página completa**: las actuales están recortadas y no incluyen la barra de navegación superior.

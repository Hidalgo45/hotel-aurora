# Evidencias de diseño responsive

Capturas requeridas por el criterio 2.1 de la rúbrica. Se toman con **Chrome DevTools → Toggle device toolbar (Ctrl + Shift + M)**.

## Los tres anchos obligatorios

| Ancho | Perfil de DevTools | Nombre del archivo |
|---|---|---|
| 375 px | iPhone SE | `..._375.png` |
| 768 px | iPad Mini | `..._768.png` |
| 1440 px | Responsive, ancho manual | `..._1440.png` |

## Archivos que deben quedar en esta carpeta

```
01_home_375.png            01_home_768.png            01_home_1440.png
02_catalogo_375.png        02_catalogo_768.png        02_catalogo_1440.png
03_reserva_375.png         03_reserva_768.png         03_reserva_1440.png
04_error_capacidad_375.png     <- mensaje de error visible en pantalla
05_confirmacion_375.png
06_admin_reportes_1440.png
07_admin_dashboard_768.png
resultados_encuesta.xlsx       <- 10 respuestas + cálculo SUS
informe_usabilidad.pdf         <- hallazgos + las 2 mejoras aplicadas
```

## Qué revisar antes de dar por buena una captura

- [ ] No hay desplazamiento **horizontal** en ningún ancho
- [ ] Ningún texto queda cortado ni encimado
- [ ] Los botones tienen al menos 44 × 44 px en móvil
- [ ] Las tablas anchas hacen scroll dentro de su propio contenedor, no arrastran la página
- [ ] El menú hamburguesa abre y cierra correctamente
- [ ] Los mensajes de error se ven completos sin hacer scroll

> Consejo para la sustentación: dejen abierta una pestaña con DevTools ya en 375 px. Cambiar de ancho en vivo delante del docente vale más que cualquier captura.

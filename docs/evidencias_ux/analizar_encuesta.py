"""Calcula el puntaje SUS y el desglose de la encuesta de usabilidad.

    .venv\\Scripts\\python.exe docs\\evidencias_ux\\analizar_encuesta.py

Lee la exportacion de Google Forms (funciona con el .csv suelto o con el
zip que descarga Google cuando la hoja tiene varias pestanas).

El SUS se puntua por AFIRMACION, no por posicion en el formulario: a las
positivas se les resta 1, las negativas se restan de 5, se suma todo y se
multiplica por 2.5. Por eso el orden en que quedaron las preguntas no
afecta el resultado.
"""
from __future__ import annotations

import csv
import io
import zipfile
from collections import Counter
from pathlib import Path

RUTA = Path(__file__).parent / "formulario_hotel.csv"

# Fragmento identificador de cada afirmacion -> (numero SUS, es_positiva)
AFIRMACIONES = {
    "facil reservar":            (1, True),
    "innecesariamente complejo": (2, False),
    "textos y botones":          (3, True),
    "ayuda de alguien":          (4, False),
    "coherente entre":           (5, True),
    "incoherencias":             (6, False),
    "aprenderia a usarlo":       (7, True),
    "inseguro o insegura":       (8, False),
    "mensajes de error":         (9, True),
    "desplazarme horizontalmente": (10, False),
}

TAREAS = [
    "Buscar habitaciones libres",
    "Completar una reserva",
    "Entender el mensaje",
    "Volver a encontrar el codigo",
    "Cancelar la reserva",
]


def sin_tildes(texto: str) -> str:
    tabla = str.maketrans("áéíóúÁÉÍÓÚñÑ", "aeiouAEIOUnN")
    return texto.translate(tabla).lower()


def leer_filas() -> list[list[str]]:
    if zipfile.is_zipfile(RUTA):
        with zipfile.ZipFile(RUTA) as z:
            crudo = z.read(z.namelist()[0]).decode("utf-8-sig")
    else:
        crudo = RUTA.read_text(encoding="utf-8-sig")
    return list(csv.reader(io.StringIO(crudo)))


def main() -> None:
    filas = leer_filas()
    cabecera, respuestas = filas[0], filas[1:]

    # Localiza la columna de cada afirmacion y la del dispositivo
    columnas: dict[int, tuple[int, bool]] = {}
    col_dispositivo = col_tareas = None

    for i, titulo in enumerate(cabecera):
        t = sin_tildes(titulo)
        if "[puntuacion]" in t or "[comentarios]" in t:
            continue                      # columnas que agrega el modo examen
        if "en que dispositivo" in t and col_dispositivo is None:
            col_dispositivo = i
        if "lograste completar" in t and col_tareas is None:
            col_tareas = i
        for clave, (num, positiva) in AFIRMACIONES.items():
            if sin_tildes(clave) in t:
                columnas[i] = (num, positiva)
                break

    faltan = set(range(1, 11)) - {n for n, _ in columnas.values()}
    if faltan:
        print(f"  AVISO: no se encontraron las afirmaciones {sorted(faltan)}\n")

    # ---- Puntaje por persona ----
    puntajes: list[float] = []
    por_dispositivo: dict[str, list[float]] = {}
    por_afirmacion: dict[int, list[int]] = {n: [] for n in range(1, 11)}

    for fila in respuestas:
        suma = 0
        completas = True
        for i, (num, positiva) in columnas.items():
            try:
                v = int(fila[i])
            except (ValueError, IndexError):
                completas = False
                break
            por_afirmacion[num].append(v)
            suma += (v - 1) if positiva else (5 - v)
        if not completas:
            continue

        sus = suma * 2.5
        puntajes.append(sus)
        disp = fila[col_dispositivo].strip() if col_dispositivo is not None else "?"
        por_dispositivo.setdefault(disp, []).append(sus)

    # ---- Tareas completadas ----
    conteo_tareas: Counter[str] = Counter()
    total_marcas = 0
    if col_tareas is not None:
        for fila in respuestas:
            marcadas = [m.strip() for m in fila[col_tareas].split(";") if m.strip()]
            total_marcas += 1
            for tarea in TAREAS:
                if any(sin_tildes(tarea) in sin_tildes(m) for m in marcadas):
                    conteo_tareas[tarea] += 1

    # ================== Informe ==================
    n = len(puntajes)
    print("=" * 60)
    print("  ENCUESTA DE USABILIDAD - HOTEL AURORA")
    print("=" * 60)
    print(f"  Respuestas validas: {n} de {len(respuestas)}")
    print()

    if not n:
        print("  Sin respuestas completas que puntuar.")
        return

    promedio = sum(puntajes) / n
    ordenados = sorted(puntajes)
    mediana = (ordenados[n // 2] if n % 2
               else (ordenados[n // 2 - 1] + ordenados[n // 2]) / 2)

    print(f"  PUNTAJE SUS PROMEDIO: {promedio:.1f} / 100")
    print(f"  Mediana: {mediana:.1f}   Minimo: {min(puntajes):.1f}   "
          f"Maximo: {max(puntajes):.1f}")
    print()
    if promedio >= 80:
        lectura = "excelente"
    elif promedio >= 68:
        lectura = "por encima del promedio de la industria (68)"
    else:
        lectura = "por debajo del promedio de la industria (68)"
    print(f"  Interpretacion: {lectura}")
    print()

    print("-" * 60)
    print("  POR DISPOSITIVO")
    print("-" * 60)
    for disp, lista in sorted(por_dispositivo.items(),
                              key=lambda x: -len(x[1])):
        print(f"  {disp:<28} n={len(lista):<3} SUS {sum(lista)/len(lista):.1f}")
    print()

    print("-" * 60)
    print("  PROMEDIO POR AFIRMACION (1 a 5)")
    print("-" * 60)
    etiquetas = {n: k for k, (n, _) in AFIRMACIONES.items()}
    signo = {n: p for _, (n, p) in
             [(k, v) for k, v in AFIRMACIONES.items()]}
    for num in range(1, 11):
        vals = por_afirmacion[num]
        if not vals:
            continue
        media = sum(vals) / len(vals)
        pos = [p for _, (nn, p) in AFIRMACIONES.items() if nn == num][0]
        # En las negativas, un promedio ALTO es malo
        alerta = "  <-- revisar" if (pos and media < 3.5) or \
                                    (not pos and media > 2.5) else ""
        tipo = "+" if pos else "-"
        print(f"  {num:>2}{tipo} {etiquetas[num][:34]:<36} {media:.2f}{alerta}")
    print()

    if conteo_tareas:
        print("-" * 60)
        print("  TAREAS COMPLETADAS SIN AYUDA")
        print("-" * 60)
        for tarea in TAREAS:
            c = conteo_tareas[tarea]
            pct = 100 * c / total_marcas if total_marcas else 0
            barra = "#" * int(pct / 5)
            print(f"  {tarea:<32} {c:>2}/{total_marcas}  {pct:5.1f}% {barra}")
    print()
    print("=" * 60)


if __name__ == "__main__":
    main()

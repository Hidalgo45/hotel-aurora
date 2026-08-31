"""Servidor temporal para generar los diagramas del proyecto.

Sirve la carpeta del proyecto y acepta POST /guardar?nombre=archivo.svg
para escribir en docs/ el SVG que Mermaid genera en el navegador.

Se usa una sola vez para producir los diagramas y despues se puede borrar.

    .venv\\Scripts\\python.exe docs\\_servidor_diagramas.py
"""
from __future__ import annotations

from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse, parse_qs

RAIZ = Path(__file__).resolve().parent.parent
DOCS = RAIZ / "docs"
PUERTO = 8899

NOMBRES_PERMITIDOS = {
    "modelo_entidad_relacion.svg",
    "diagrama_clases.svg",
}


class Manejador(SimpleHTTPRequestHandler):
    """Sirve archivos y acepta la escritura de los dos SVG esperados."""

    def do_POST(self) -> None:  # noqa: N802  (nombre impuesto por la clase base)
        ruta = urlparse(self.path)
        if ruta.path != "/guardar":
            self.send_error(404, "Ruta no soportada")
            return

        nombre = (parse_qs(ruta.query).get("nombre") or [""])[0]
        if nombre not in NOMBRES_PERMITIDOS:
            self.send_error(400, f"Nombre no permitido: {nombre}")
            return

        largo = int(self.headers.get("Content-Length", 0))
        contenido = self.rfile.read(largo).decode("utf-8")

        destino = DOCS / nombre
        destino.write_text(contenido, encoding="utf-8")

        print(f"  [OK] {nombre}  ({len(contenido):,} bytes)")

        self.send_response(200)
        self.send_header("Content-Type", "text/plain; charset=utf-8")
        self.end_headers()
        self.wfile.write(f"guardado {nombre}".encode("utf-8"))

    def log_message(self, formato, *args):
        """Silencia el log de cada GET: solo interesa el resultado del guardado."""
        return


if __name__ == "__main__":
    manejador = partial(Manejador, directory=str(RAIZ))
    print(f"\n  Generador de diagramas en http://127.0.0.1:{PUERTO}")
    print("  Abrir  /docs/_diagramas.html  y esperar a que se guarden los SVG.")
    print("  Ctrl+C para detener.\n")
    ThreadingHTTPServer(("127.0.0.1", PUERTO), manejador).serve_forever()

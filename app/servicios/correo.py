"""Envio del comprobante de reserva por correo electronico.

El servicio tiene dos backends intercambiables:

* ``archivo``  guarda el mensaje completo en ``correos_enviados/`` sin salir a
  la red. Es el valor por defecto: permite trabajar y demostrar el flujo sin
  conexion, que es justo lo que hace falta el dia de la sustentacion.
* ``smtp``     envia de verdad a traves de un servidor SMTP.

La eleccion se hace en el archivo ``.env`` con ``CORREO_BACKEND``. El resto de
la aplicacion llama siempre al mismo metodo y no sabe cual esta activo: esa es
la razon de que el backend sea un detalle de configuracion y no un ``if``
repartido por las vistas.
"""
from __future__ import annotations

import smtplib
import ssl
from datetime import datetime
from email.message import EmailMessage
from email.utils import formataddr, formatdate, make_msgid
from pathlib import Path


class ErrorCorreo(Exception):
    """El comprobante no se pudo entregar. Nunca invalida la reserva."""


class ServicioCorreo:
    """Construye y entrega el comprobante de una reserva."""

    def __init__(self, config) -> None:
        self._cfg = config

    # ------------------------------------------------------------------
    # API publica
    # ------------------------------------------------------------------
    def enviar_comprobante(self, reserva: dict, cuerpo_html: str,
                           cuerpo_texto: str) -> str:
        """Entrega el comprobante y devuelve una descripcion de lo ocurrido.

        Lanza ``ErrorCorreo`` si la entrega falla. Quien llama debe tratar ese
        fallo como un aviso, no como un error de la reserva: la reserva ya
        existe en la base de datos y no depende del correo.
        """
        destino = (reserva.get("email") or "").strip()
        if not destino:
            raise ErrorCorreo("El cliente no tiene un correo registrado.")

        mensaje = self._construir(reserva, destino, cuerpo_html, cuerpo_texto)

        if self._cfg.CORREO_BACKEND == "smtp":
            return self._enviar_por_smtp(mensaje, destino)
        return self._guardar_en_archivo(mensaje, reserva)

    # ------------------------------------------------------------------
    # Construccion del mensaje
    # ------------------------------------------------------------------
    def _construir(self, reserva: dict, destino: str,
                   cuerpo_html: str, cuerpo_texto: str) -> EmailMessage:
        mensaje = EmailMessage()
        mensaje["Subject"] = (f"Comprobante de tu reserva {reserva['codigo']} "
                              f"- {self._cfg.HOTEL_NOMBRE}")
        mensaje["From"] = formataddr(
            (self._cfg.HOTEL_NOMBRE, self._cfg.SMTP_REMITENTE))
        mensaje["To"] = formataddr((reserva.get("cliente", ""), destino))
        mensaje["Date"] = formatdate(localtime=True)
        mensaje["Message-ID"] = make_msgid(domain="hotelaurora.ec")

        # Se envian las dos versiones: el cliente de correo elige. El texto
        # plano es el respaldo para lectores que no muestran HTML.
        mensaje.set_content(cuerpo_texto)
        mensaje.add_alternative(cuerpo_html, subtype="html")
        return mensaje

    # ------------------------------------------------------------------
    # Backends
    # ------------------------------------------------------------------
    def _enviar_por_smtp(self, mensaje: EmailMessage, destino: str) -> str:
        if not self._cfg.SMTP_USUARIO or not self._cfg.SMTP_CLAVE:
            raise ErrorCorreo(
                "Faltan SMTP_USUARIO y SMTP_CLAVE en el archivo .env.")
        try:
            contexto = ssl.create_default_context()
            with smtplib.SMTP(self._cfg.SMTP_HOST, self._cfg.SMTP_PORT,
                              timeout=self._cfg.SMTP_TIEMPO_LIMITE) as servidor:
                servidor.starttls(context=contexto)
                servidor.login(self._cfg.SMTP_USUARIO, self._cfg.SMTP_CLAVE)
                servidor.send_message(mensaje)
        except smtplib.SMTPAuthenticationError:
            raise ErrorCorreo(
                "El servidor rechazo las credenciales. Si usas Gmail, la clave "
                "debe ser una contrasena de aplicacion, no la de tu cuenta.")
        except (smtplib.SMTPException, OSError) as e:
            raise ErrorCorreo(f"No se pudo contactar al servidor de correo: {e}")
        return f"enviado a {destino}"

    def _guardar_en_archivo(self, mensaje: EmailMessage, reserva: dict) -> str:
        carpeta: Path = self._cfg.CARPETA_CORREOS
        try:
            carpeta.mkdir(parents=True, exist_ok=True)
            marca = datetime.now().strftime("%Y%m%d_%H%M%S")
            archivo = carpeta / f"{marca}_{reserva['codigo']}.eml"
            archivo.write_bytes(mensaje.as_bytes())

            # Copia en HTML suelto: se abre con doble clic en el navegador,
            # que es lo comodo para mostrarlo en vivo. Se envuelve en un
            # documento completo con <meta charset>: sin esa etiqueta el
            # navegador asume latin-1 y los acentos salen partidos.
            vista = carpeta / f"{marca}_{reserva['codigo']}.html"
            cuerpo = mensaje.get_body(preferencelist=("html",))
            if cuerpo is not None:
                vista.write_text(
                    '<!doctype html>\n<html lang="es">\n<head>\n'
                    '<meta charset="utf-8">\n'
                    f"<title>Comprobante {reserva['codigo']}</title>\n"
                    "</head>\n<body style=\"margin:0\">\n"
                    f"{cuerpo.get_content()}\n</body>\n</html>\n",
                    encoding="utf-8")
        except OSError as e:
            raise ErrorCorreo(f"No se pudo guardar el comprobante: {e}")
        return f"guardado en correos_enviados/{archivo.name}"


def servicio_correo(config) -> ServicioCorreo:
    """Fabrica el servicio a partir de la configuracion de la aplicacion."""
    return ServicioCorreo(config)

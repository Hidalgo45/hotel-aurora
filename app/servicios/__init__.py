"""Capa de servicios: casos de uso que coordinan dominio, datos e infraestructura."""
from .correo import ErrorCorreo, ServicioCorreo, servicio_correo

__all__ = ["ErrorCorreo", "ServicioCorreo", "servicio_correo"]

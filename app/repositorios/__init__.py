"""Capa de acceso a datos: puente entre el dominio y PostgreSQL."""
from .habitaciones_pg import HabitacionRepositorioPG
from .reportes_pg import ReporteRepositorioPG
from .reservas_pg import ReservaRepositorioPG
from .usuarios_pg import UsuarioRepositorioPG

__all__ = ["HabitacionRepositorioPG", "ReservaRepositorioPG",
           "UsuarioRepositorioPG", "ReporteRepositorioPG"]

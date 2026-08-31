"""Dominio del Hotel Aurora.

Este paquete NO importa Flask ni psycopg: contiene unicamente las reglas de
negocio, por lo que puede probarse con pytest sin levantar servidor ni base
de datos.
"""
from .excepciones import (ErrorDominio, ReglaNegocioError,
                          TransicionInvalidaError, ValorInvalidoError)
from .habitaciones import (EstadoHabitacion, FabricaHabitaciones, Habitacion,
                           HabitacionEstandar, HabitacionFamiliar, HabitacionSuite)
from .personas import (Administrador, Cliente, FabricaUsuarios, Persona,
                       Recepcionista, Usuario)
from .reserva import EstadoReserva, Reserva
from .servicios import (FabricaServicios, Servicio, ServicioPorNoche,
                        ServicioPorUnidad)

__all__ = [
    "ErrorDominio", "ReglaNegocioError", "TransicionInvalidaError",
    "ValorInvalidoError", "EstadoHabitacion", "Habitacion", "HabitacionEstandar",
    "HabitacionFamiliar", "HabitacionSuite", "FabricaHabitaciones",
    "Persona", "Usuario", "Administrador", "Recepcionista", "Cliente",
    "FabricaUsuarios", "Reserva", "EstadoReserva", "Servicio",
    "ServicioPorNoche", "ServicioPorUnidad", "FabricaServicios",
]

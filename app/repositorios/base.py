"""QUE HACE: define lo que cualquier repositorio tiene que saber hacer,
sin decir como lo hace.

SI PREGUNTAN POR ESTE ARCHIVO:
"Es como un contrato. Dice: quien quiera encargarse de guardar reservas
tiene que saber crearlas, buscarlas y cancelarlas. Como lo consiga es asunto
suyo. Gracias a eso, las clases del dominio no saben que detras hay
PostgreSQL, y por eso se pueden probar sin base de datos."
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import date
from decimal import Decimal


class RepositorioHabitaciones(ABC):

    @abstractmethod
    def listar_tipos(self) -> list[dict]: ...

    @abstractmethod
    def buscar_disponibles(self, checkin: date, checkout: date,
                           huespedes: int) -> list[dict]: ...

    @abstractmethod
    def obtener(self, id_habitacion: int) -> dict | None: ...


class RepositorioReservas(ABC):

    @abstractmethod
    def crear(self, id_cliente: int, habitaciones: list[int], checkin: date,
              checkout: date, adultos: int, ninos: int) -> tuple[str, Decimal]: ...

    @abstractmethod
    def cancelar(self, codigo: str, motivo: str) -> Decimal: ...

    @abstractmethod
    def buscar_por_codigo(self, codigo: str) -> dict | None: ...


class RepositorioUsuarios(ABC):

    @abstractmethod
    def buscar_por_email(self, email: str) -> dict | None: ...

    @abstractmethod
    def registrar_cliente(self, datos: dict) -> int: ...

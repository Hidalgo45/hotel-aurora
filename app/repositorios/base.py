"""Contratos de acceso a datos.

El dominio depende de estas interfaces abstractas, no de PostgreSQL. Si manana
la persistencia cambiara, bastaria escribir otra implementacion sin tocar las
reglas de negocio.
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

"""QUE HACE: define los extras que se pueden contratar con la reserva.

Hay dos formas de cobrar y cada una es una clase: por noche, que multiplica
por los dias de estadia, y por unidad, que se cobra una sola vez.

SI PREGUNTAN POR ESTE ARCHIVO:
"El desayuno se cobra por cada noche; el traslado al aeropuerto, una sola
vez. La reserva no necesita saber cual es cual: le pide el costo a cada
servicio y cada uno responde segun su forma de cobrar."
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from decimal import Decimal, ROUND_HALF_UP

from .excepciones import ValorInvalidoError


class Servicio(ABC):
    """Servicio que se puede agregar a una reserva."""

    def __init__(self, nombre: str, precio: Decimal,
                 id_servicio: int | None = None,
                 descripcion: str = "") -> None:
        if Decimal(precio) < 0:
            raise ValorInvalidoError("El precio de un servicio no puede ser negativo.")
        self.id_servicio = id_servicio
        self._nombre = nombre
        self._precio = Decimal(precio)
        self._descripcion = descripcion

    @property
    def nombre(self) -> str:
        return self._nombre

    @property
    def precio(self) -> Decimal:
        return self._precio

    @property
    def descripcion(self) -> str:
        return self._descripcion

    @abstractmethod
    def costo(self, noches: int, cantidad: int = 1) -> Decimal:
        """Cuanto se cobra por este servicio en una estadia concreta."""

    @abstractmethod
    def etiqueta_cobro(self) -> str:
        """Texto que ve el usuario junto al precio."""

    @staticmethod
    def _redondear(valor: Decimal) -> Decimal:
        return Decimal(valor).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

    def __str__(self) -> str:
        return f"{self._nombre} - ${self._precio} {self.etiqueta_cobro()}"


class ServicioPorNoche(Servicio):
    """Se cobra una vez por cada noche de la estadia (desayuno, parqueadero)."""

    def costo(self, noches: int, cantidad: int = 1) -> Decimal:
        return self._redondear(self._precio * noches)

    def etiqueta_cobro(self) -> str:
        return "por noche"


class ServicioPorUnidad(Servicio):
    """Se cobra por vez contratada (traslado, tour, cena)."""

    def costo(self, noches: int, cantidad: int = 1) -> Decimal:
        return self._redondear(self._precio * cantidad)

    def etiqueta_cobro(self) -> str:
        return "por unidad"


class FabricaServicios:
    _MAPA: dict[str, type[Servicio]] = {
        "POR_NOCHE": ServicioPorNoche,
        "POR_UNIDAD": ServicioPorUnidad,
    }

    @classmethod
    def desde_fila(cls, fila: dict) -> Servicio:
        clase = cls._MAPA.get(fila["modo_cobro"], ServicioPorUnidad)
        return clase(
            nombre=fila["nombre"],
            precio=fila["precio"],
            id_servicio=fila["id_servicio"],
            descripcion=fila.get("descripcion", ""),
        )

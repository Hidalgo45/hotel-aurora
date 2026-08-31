"""Jerarquia de habitaciones del Hotel Aurora.

Demuestra los cuatro pilares de la POO:

  Abstraccion     Habitacion es una clase abstracta (ABC): no se puede
                  instanciar una "habitacion generica".
  Encapsulamiento El estado es un atributo privado (__estado) que solo se
                  puede modificar a traves de cambiar_estado(), que valida
                  la transicion.
  Herencia        Estandar, Familiar y Suite comparten datos y comportamiento.
  Polimorfismo    Las tres implementan calcular_tarifa() con formulas
                  distintas y el resto del sistema las trata igual.

Las formulas de este modulo son el espejo exacto de la funcion SQL
fn_calcular_tarifa (database/04_procedures.sql).
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from decimal import Decimal, ROUND_HALF_UP
from enum import Enum

from .excepciones import TransicionInvalidaError, ValorInvalidoError


class EstadoHabitacion(str, Enum):
    """Estados fisicos posibles de una habitacion."""

    DISPONIBLE = "DISPONIBLE"
    RESERVADA = "RESERVADA"
    OCUPADA = "OCUPADA"
    LIMPIEZA = "LIMPIEZA"
    MANTENIMIENTO = "MANTENIMIENTO"


#: Maquina de estados. Es el espejo del trigger trg_reserva_estado.
TRANSICIONES: dict[EstadoHabitacion, set[EstadoHabitacion]] = {
    EstadoHabitacion.DISPONIBLE: {EstadoHabitacion.RESERVADA,
                                  EstadoHabitacion.MANTENIMIENTO},
    EstadoHabitacion.RESERVADA: {EstadoHabitacion.OCUPADA,
                                 EstadoHabitacion.DISPONIBLE},
    EstadoHabitacion.OCUPADA: {EstadoHabitacion.LIMPIEZA},
    EstadoHabitacion.LIMPIEZA: {EstadoHabitacion.DISPONIBLE,
                                EstadoHabitacion.MANTENIMIENTO},
    EstadoHabitacion.MANTENIMIENTO: {EstadoHabitacion.DISPONIBLE},
}


class Habitacion(ABC):
    """Clase base abstracta de toda habitacion del hotel."""

    def __init__(self, numero: str, piso: int, tarifa_base: Decimal,
                 id_habitacion: int | None = None,
                 estado: EstadoHabitacion = EstadoHabitacion.DISPONIBLE) -> None:
        if not str(numero).isdigit() or not 3 <= len(str(numero)) <= 4:
            raise ValorInvalidoError(
                "El numero de habitacion debe tener 3 o 4 digitos.")
        if Decimal(tarifa_base) <= 0:
            raise ValorInvalidoError("La tarifa base debe ser mayor que cero.")
        if not 1 <= int(piso) <= 12:
            raise ValorInvalidoError("El piso debe estar entre 1 y 12.")

        self.id_habitacion = id_habitacion
        self._numero = str(numero)
        self._piso = int(piso)
        self._tarifa_base = Decimal(tarifa_base)
        self.__estado = EstadoHabitacion(estado)   # atributo privado real

    # ------------------------------------------------------------------
    # Encapsulamiento: lectura publica, escritura controlada
    # ------------------------------------------------------------------
    @property
    def numero(self) -> str:
        return self._numero

    @property
    def piso(self) -> int:
        return self._piso

    @property
    def tarifa_base(self) -> Decimal:
        return self._tarifa_base

    @property
    def estado(self) -> EstadoHabitacion:
        """Solo lectura. Para cambiarlo hay que usar cambiar_estado()."""
        return self.__estado

    def cambiar_estado(self, nuevo: EstadoHabitacion) -> None:
        """Cambia el estado solo si la transicion es valida."""
        nuevo = EstadoHabitacion(nuevo)
        if nuevo not in TRANSICIONES[self.__estado]:
            raise TransicionInvalidaError(
                f"La habitacion {self._numero} no puede pasar de "
                f"{self.__estado.value} a {nuevo.value}."
            )
        self.__estado = nuevo

    def esta_disponible(self) -> bool:
        return self.__estado is EstadoHabitacion.DISPONIBLE

    # ------------------------------------------------------------------
    # Contrato abstracto: cada subclase debe implementarlo
    # ------------------------------------------------------------------
    @abstractmethod
    def calcular_tarifa(self, noches: int,
                        factor_temporada: Decimal = Decimal("1.0")) -> Decimal:
        """Precio total de la estadia segun la politica de cada tipo."""

    @abstractmethod
    def servicios_incluidos(self) -> list[str]:
        """Servicios que vienen sin costo adicional."""

    @abstractmethod
    def capacidad(self) -> int:
        """Numero maximo de huespedes."""

    @abstractmethod
    def descripcion_tipo(self) -> str:
        """Nombre comercial del tipo de habitacion."""

    # ------------------------------------------------------------------
    # Utilidades compartidas por toda la jerarquia
    # ------------------------------------------------------------------
    @staticmethod
    def _redondear(valor: Decimal) -> Decimal:
        return Decimal(valor).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

    def __eq__(self, otro: object) -> bool:
        return isinstance(otro, Habitacion) and otro._numero == self._numero

    def __hash__(self) -> int:
        return hash(self._numero)

    def __str__(self) -> str:
        return (f"{self.descripcion_tipo()} {self._numero} "
                f"(piso {self._piso}) - {self.estado.value}")

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} {self._numero}>"


class HabitacionEstandar(Habitacion):
    """Tarifa lineal: tarifa base por noche, sin recargos."""

    def calcular_tarifa(self, noches, factor_temporada=Decimal("1.0")):
        return self._redondear(self._tarifa_base * noches * Decimal(factor_temporada))

    def servicios_incluidos(self):
        return ["Wi-Fi", "TV por cable", "Bano privado"]

    def capacidad(self):
        return 2

    def descripcion_tipo(self):
        return "Estandar"


class HabitacionSuite(Habitacion):
    """Recargo del 25 % por amenidades y 10 % de descuento desde 5 noches."""

    RECARGO = Decimal("1.25")
    DESCUENTO_LARGA = Decimal("0.90")
    NOCHES_PARA_DESCUENTO = 5

    def calcular_tarifa(self, noches, factor_temporada=Decimal("1.0")):
        subtotal = (self._tarifa_base * self.RECARGO
                    * noches * Decimal(factor_temporada))
        if noches >= self.NOCHES_PARA_DESCUENTO:
            subtotal *= self.DESCUENTO_LARGA
        return self._redondear(subtotal)

    def servicios_incluidos(self):
        return ["Wi-Fi", "TV por cable", "Desayuno buffet", "Minibar", "Jacuzzi"]

    def capacidad(self):
        return 3

    def descripcion_tipo(self):
        return "Suite"


class HabitacionFamiliar(Habitacion):
    """Tarifa base mas un cargo fijo por cada cama adicional y por noche."""

    CARGO_CAMA_EXTRA = Decimal("12.00")

    def __init__(self, numero, piso, tarifa_base, id_habitacion=None,
                 estado=EstadoHabitacion.DISPONIBLE, camas_extra: int = 1):
        super().__init__(numero, piso, tarifa_base, id_habitacion, estado)
        if not 0 <= camas_extra <= 3:
            raise ValorInvalidoError(
                "Una habitacion familiar admite hasta 3 camas extra.")
        self._camas_extra = camas_extra

    def calcular_tarifa(self, noches, factor_temporada=Decimal("1.0")):
        base = self._tarifa_base * noches * Decimal(factor_temporada)
        extras = self.CARGO_CAMA_EXTRA * self._camas_extra * noches
        return self._redondear(base + extras)

    def servicios_incluidos(self):
        return ["Wi-Fi", "TV por cable", "Cuna a pedido", "Desayuno infantil"]

    def capacidad(self):
        return 2 + self._camas_extra

    def descripcion_tipo(self):
        return "Familiar"


class FabricaHabitaciones:
    """Convierte el codigo de tipo de la base de datos en el objeto correcto.

    Concentra en un solo lugar la decision de que clase instanciar, de modo que
    agregar un tipo nuevo no obliga a tocar el resto del sistema.
    """

    _MAPA: dict[str, type[Habitacion]] = {
        "EST": HabitacionEstandar,
        "SUI": HabitacionSuite,
        "FAM": HabitacionFamiliar,
    }

    @classmethod
    def crear(cls, codigo_tipo: str, **datos) -> Habitacion:
        clase = cls._MAPA.get(codigo_tipo)
        if clase is None:
            raise ValorInvalidoError(
                f"Tipo de habitacion desconocido: {codigo_tipo}")
        return clase(**datos)

    @classmethod
    def desde_fila(cls, fila: dict) -> Habitacion:
        """Construye la habitacion a partir de una fila de la consulta SQL."""
        return cls.crear(
            fila["codigo"],
            numero=fila["numero"],
            piso=fila["piso"],
            tarifa_base=fila["tarifa_base"],
            id_habitacion=fila["id_habitacion"],
            estado=fila["estado"],
        )

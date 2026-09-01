"""QUE HACE: es el centro del sistema. Una reserva junta un cliente, una o
varias habitaciones, los servicios contratados y en que etapa esta.

SI PREGUNTAN POR ESTE ARCHIVO:
"La reserva no hereda de habitacion, la contiene. Guarda una lista de
habitaciones y otra de servicios, y para calcular el total le pregunta a cada
una cuanto cobra."

Tambien controla por que etapas puede pasar: pendiente, confirmada, entrada
registrada, salida registrada. No deja saltarse pasos. No se puede registrar
la salida de alguien que nunca entro.

UN DETALLE QUE VALE LA PENA SABER:
El constructor comprueba que la salida sea posterior a la entrada y que haya
al menos un adulto, porque eso siempre debe cumplirse. Pero no comprueba que
la fecha no sea del pasado: eso esta en un metodo aparte, porque depende de
cuando se pregunte. Una reserva de septiembre es valida hoy e invalida en
octubre. Si estuviera en el constructor, no se podrian cargar las reservas
antiguas guardadas en la base.
"""
from __future__ import annotations

from datetime import date
from decimal import Decimal
from enum import Enum

from .excepciones import ReglaNegocioError, TransicionInvalidaError
from .habitaciones import Habitacion
from .servicios import Servicio


class EstadoReserva(str, Enum):
    PENDIENTE = "PENDIENTE"
    CONFIRMADA = "CONFIRMADA"
    CHECK_IN = "CHECK_IN"
    CHECK_OUT = "CHECK_OUT"
    CANCELADA = "CANCELADA"
    NO_SHOW = "NO_SHOW"


class Reserva:
    """Agrupa habitaciones y servicios y gobierna su propio ciclo de vida."""

    MAX_NOCHES = 30
    PENALIDAD_TARDIA = Decimal("0.20")
    DIAS_LIMITE_CANCELACION = 2

    def __init__(self, cliente, checkin: date, checkout: date,
                 adultos: int = 1, ninos: int = 0,
                 codigo: str | None = None,
                 estado: EstadoReserva = EstadoReserva.PENDIENTE) -> None:
        if checkout <= checkin:
            raise ReglaNegocioError(
                "La fecha de salida debe ser posterior a la de entrada.")
        if (checkout - checkin).days > self.MAX_NOCHES:
            raise ReglaNegocioError(
                f"La estadia no puede superar {self.MAX_NOCHES} noches.")
        if adultos < 1:
            raise ReglaNegocioError("Debe haber al menos un adulto en la reserva.")

        self._codigo = codigo
        self._cliente = cliente
        self._checkin = checkin
        self._checkout = checkout
        self._adultos = adultos
        self._ninos = ninos
        self._habitaciones: list[Habitacion] = []
        self._servicios: list[tuple[Servicio, int]] = []
        self._total: Decimal = Decimal("0.00")
        self.__estado = EstadoReserva(estado)

    # ------------------------------------------------------------------
    # Propiedades de solo lectura
    # ------------------------------------------------------------------
    @property
    def codigo(self) -> str | None:
        return self._codigo

    @property
    def cliente(self):
        return self._cliente

    @property
    def checkin(self) -> date:
        return self._checkin

    @property
    def checkout(self) -> date:
        return self._checkout

    @property
    def adultos(self) -> int:
        return self._adultos

    @property
    def ninos(self) -> int:
        return self._ninos

    @property
    def estado(self) -> EstadoReserva:
        return self.__estado

    @property
    def habitaciones(self) -> tuple[Habitacion, ...]:
        """Se devuelve una tupla para que nadie modifique la lista por fuera."""
        return tuple(self._habitaciones)

    @property
    def noches(self) -> int:
        return (self._checkout - self._checkin).days

    @property
    def huespedes(self) -> int:
        return self._adultos + self._ninos

    @property
    def capacidad_total(self) -> int:
        return sum(h.capacidad() for h in self._habitaciones)

    @property
    def total(self) -> Decimal:
        return self._total

    # ------------------------------------------------------------------
    # Validacion previa: valida sin lanzar excepcion
    # ------------------------------------------------------------------
    def validar_fecha_inicio(self) -> None:
        if self._checkin < date.today():
            raise ReglaNegocioError("No se pueden reservar fechas que ya pasaron.")

    # ------------------------------------------------------------------
    # Composicion
    # ------------------------------------------------------------------
    def agregar_habitacion(self, habitacion: Habitacion) -> None:
        if self.__estado is not EstadoReserva.PENDIENTE:
            raise TransicionInvalidaError(
                "Solo una reserva pendiente admite cambios.")
        if habitacion in self._habitaciones:
            raise ReglaNegocioError(
                f"La habitacion {habitacion.numero} ya esta en la reserva.")
        self._habitaciones.append(habitacion)

    def agregar_servicio(self, servicio: Servicio, cantidad: int = 1) -> None:
        if cantidad < 1:
            raise ReglaNegocioError("La cantidad de un servicio debe ser al menos 1.")
        self._servicios.append((servicio, cantidad))

    # ------------------------------------------------------------------
    # Calculo polimorfico del total
    # ------------------------------------------------------------------
    def calcular_alojamiento(self,
                             factor_temporada: Decimal = Decimal("1.0")) -> Decimal:
        """Suma las tarifas sin preguntar el tipo de cada habitacion."""
        return sum(
            (h.calcular_tarifa(self.noches, factor_temporada)
             for h in self._habitaciones),
            Decimal("0.00"),
        )

    def calcular_servicios(self) -> Decimal:
        return sum(
            (s.costo(self.noches, cantidad) for s, cantidad in self._servicios),
            Decimal("0.00"),
        )

    def calcular_total(self,
                       factor_temporada: Decimal = Decimal("1.0")) -> Decimal:
        self._total = (self.calcular_alojamiento(factor_temporada)
                       + self.calcular_servicios())
        return self._total

    # ------------------------------------------------------------------
    # Ciclo de vida
    # ------------------------------------------------------------------
    def confirmar(self) -> None:
        if self.__estado is not EstadoReserva.PENDIENTE:
            raise TransicionInvalidaError("Solo se confirma una reserva pendiente.")
        if not self._habitaciones:
            raise ReglaNegocioError("Debes seleccionar al menos una habitacion.")
        if self.huespedes > self.capacidad_total:
            raise ReglaNegocioError(
                f"Seleccionaste {self.huespedes} huespedes y las habitaciones "
                f"elegidas admiten {self.capacidad_total}. Agrega otra habitacion "
                f"o reduce el numero de personas."
            )
        self.__estado = EstadoReserva.CONFIRMADA

    def registrar_check_in(self) -> None:
        if self.__estado is not EstadoReserva.CONFIRMADA:
            raise TransicionInvalidaError(
                "El check-in requiere una reserva confirmada.")
        self.__estado = EstadoReserva.CHECK_IN

    def registrar_check_out(self) -> None:
        if self.__estado is not EstadoReserva.CHECK_IN:
            raise TransicionInvalidaError(
                "El check-out requiere que el huesped haya hecho check-in.")
        self.__estado = EstadoReserva.CHECK_OUT

    def cancelar(self, motivo: str) -> Decimal:
        """Cancela y devuelve la penalidad. Espejo de sp_cancelar_reserva."""
        if self.__estado in (EstadoReserva.CHECK_IN, EstadoReserva.CHECK_OUT,
                             EstadoReserva.CANCELADA):
            raise TransicionInvalidaError(
                f"Una reserva en estado {self.__estado.value} no se puede cancelar.")

        dias_faltantes = (self._checkin - date.today()).days
        penalidad = (Decimal(self._total) * self.PENALIDAD_TARDIA
                     if dias_faltantes < self.DIAS_LIMITE_CANCELACION
                     else Decimal("0.00"))

        self.__estado = EstadoReserva.CANCELADA
        self._motivo_cancelacion = motivo
        return Decimal(penalidad).quantize(Decimal("0.01"))

    def asignar_codigo(self, codigo: str, total: Decimal) -> None:
        """Lo llama el repositorio con los valores que devolvio la base."""
        self._codigo = codigo
        self._total = Decimal(total)
        self.__estado = EstadoReserva.PENDIENTE

    def __repr__(self) -> str:
        return (f"<Reserva {self._codigo or 'sin codigo'} "
                f"{self._checkin} a {self._checkout} {self.__estado.value}>")

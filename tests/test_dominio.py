"""Pruebas del dominio.

Se ejecutan sin base de datos y sin servidor: el paquete app.dominio no
importa Flask ni psycopg. Eso es justamente lo que demuestra la separacion
de capas.

    .venv\\Scripts\\python.exe -m pytest -v
"""
from datetime import date, timedelta
from decimal import Decimal

import pytest

from app.dominio import (Administrador, Cliente, EstadoHabitacion,
                         FabricaHabitaciones, Habitacion, HabitacionEstandar,
                         HabitacionFamiliar, HabitacionSuite, Recepcionista,
                         ReglaNegocioError, Reserva, ServicioPorNoche,
                         ServicioPorUnidad, TransicionInvalidaError,
                         ValorInvalidoError)


# ===========================================================================
# ABSTRACCION
# ===========================================================================
def test_no_se_puede_instanciar_la_clase_abstracta():
    """Una 'habitacion generica' no existe en el negocio."""
    with pytest.raises(TypeError):
        Habitacion("101", 1, Decimal("45.00"))


# ===========================================================================
# POLIMORFISMO
# ===========================================================================
def test_polimorfismo_cada_tipo_cobra_distinto():
    habitaciones = [
        HabitacionEstandar("101", 1, Decimal("45.00")),
        HabitacionSuite("401", 4, Decimal("45.00")),
        HabitacionFamiliar("301", 3, Decimal("45.00"), camas_extra=2),
    ]
    # La misma llamada, tres resultados distintos, sin un solo isinstance
    tarifas = [h.calcular_tarifa(3) for h in habitaciones]

    assert tarifas[0] == Decimal("135.00")     # 45 x 3
    assert tarifas[1] == Decimal("168.75")     # 45 x 1.25 x 3
    assert tarifas[2] == Decimal("207.00")     # 135 + (12 x 2 x 3)
    assert len(set(tarifas)) == 3


def test_suite_aplica_descuento_por_estadia_larga():
    suite = HabitacionSuite("402", 4, Decimal("100.00"))
    assert suite.calcular_tarifa(5) == Decimal("562.50")   # 100x1.25x5x0.90


def test_factor_de_temporada_multiplica_la_tarifa():
    est = HabitacionEstandar("102", 1, Decimal("50.00"))
    assert est.calcular_tarifa(2, Decimal("1.50")) == Decimal("150.00")


def test_servicios_polimorficos():
    por_noche = ServicioPorNoche("Desayuno", Decimal("8.50"))
    por_unidad = ServicioPorUnidad("Traslado", Decimal("25.00"))

    assert por_noche.costo(noches=3, cantidad=1) == Decimal("25.50")
    assert por_unidad.costo(noches=3, cantidad=2) == Decimal("50.00")


# ===========================================================================
# ENCAPSULAMIENTO
# ===========================================================================
def test_el_estado_no_se_puede_asignar_directamente():
    hab = HabitacionEstandar("103", 1, Decimal("45.00"))
    with pytest.raises(AttributeError):
        hab.estado = EstadoHabitacion.OCUPADA


def test_transicion_de_estado_invalida_se_rechaza():
    hab = HabitacionEstandar("104", 1, Decimal("45.00"))
    # No se puede pasar de DISPONIBLE a OCUPADA sin pasar por RESERVADA
    with pytest.raises(TransicionInvalidaError):
        hab.cambiar_estado(EstadoHabitacion.OCUPADA)


def test_transicion_de_estado_valida_funciona():
    hab = HabitacionEstandar("105", 1, Decimal("45.00"))
    hab.cambiar_estado(EstadoHabitacion.RESERVADA)
    hab.cambiar_estado(EstadoHabitacion.OCUPADA)
    assert hab.estado is EstadoHabitacion.OCUPADA


def test_validaciones_del_constructor():
    with pytest.raises(ValorInvalidoError):
        HabitacionEstandar("AB", 1, Decimal("45.00"))       # numero invalido
    with pytest.raises(ValorInvalidoError):
        HabitacionEstandar("106", 1, Decimal("0"))          # tarifa en cero
    with pytest.raises(ValorInvalidoError):
        HabitacionEstandar("107", 99, Decimal("45.00"))     # piso inexistente


# ===========================================================================
# HERENCIA
# ===========================================================================
def test_cada_rol_tiene_sus_propios_permisos():
    datos = ("1712345678", "Mateo", "Hidalgo", "mateo@aurora.ec")
    admin = Administrador(*datos)
    recep = Recepcionista(*datos)
    cliente = Cliente(*datos, fecha_nacimiento=date(1995, 5, 5))

    assert admin.puede("ver_reportes")
    assert not recep.puede("ver_reportes")
    assert not cliente.puede("gestionar_reservas")
    assert cliente.puede("reservar")
    assert admin.descripcion_rol() != cliente.descripcion_rol()


def test_cliente_menor_de_edad_es_rechazado():
    with pytest.raises(ValorInvalidoError):
        Cliente("1712345678", "Ana", "Perez", "ana@correo.com",
                fecha_nacimiento=date.today() - timedelta(days=365 * 15))


def test_la_contrasena_se_guarda_hasheada():
    admin = Administrador("1712345678", "Mateo", "Hidalgo", "mateo@aurora.ec")
    admin.establecer_clave("aurora123")

    assert admin.hash_guardado != "aurora123"
    assert admin.verificar_clave("aurora123")
    assert not admin.verificar_clave("otra_clave")


# ===========================================================================
# REGLAS DE NEGOCIO DE LA RESERVA
# ===========================================================================
def _cliente_demo():
    return Cliente("1712345678", "Ana", "Perez", "ana@correo.com",
                   fecha_nacimiento=date(1990, 1, 1))


def test_reserva_rechaza_salida_anterior_a_entrada():
    hoy = date.today()
    with pytest.raises(ReglaNegocioError):
        Reserva(_cliente_demo(), hoy + timedelta(days=5), hoy + timedelta(days=2))


def test_reserva_rechaza_mas_huespedes_que_capacidad():
    hoy = date.today()
    reserva = Reserva(_cliente_demo(), hoy + timedelta(days=1),
                      hoy + timedelta(days=3), adultos=4, ninos=2)
    reserva.agregar_habitacion(HabitacionEstandar("108", 1, Decimal("45.00")))

    with pytest.raises(ReglaNegocioError) as error:
        reserva.confirmar()
    # El mensaje debe ser accionable: dice cuantos caben y que hacer
    mensaje = str(error.value).lower()
    assert "6 huespedes" in mensaje and "admiten 2" in mensaje


def test_total_suma_alojamiento_y_servicios():
    hoy = date.today()
    reserva = Reserva(_cliente_demo(), hoy + timedelta(days=1),
                      hoy + timedelta(days=3), adultos=2)
    reserva.agregar_habitacion(HabitacionEstandar("109", 1, Decimal("50.00")))
    reserva.agregar_servicio(ServicioPorNoche("Desayuno", Decimal("10.00")))

    assert reserva.noches == 2
    assert reserva.calcular_total() == Decimal("120.00")   # 100 + 20


def test_cancelacion_tardia_aplica_penalidad_del_20():
    hoy = date.today()
    reserva = Reserva(_cliente_demo(), hoy + timedelta(days=1),
                      hoy + timedelta(days=3), adultos=2)
    reserva.agregar_habitacion(HabitacionEstandar("110", 1, Decimal("50.00")))
    reserva.calcular_total()

    assert reserva.cancelar("Cambio de planes") == Decimal("20.00")


def test_cancelacion_con_anticipacion_no_tiene_cargo():
    hoy = date.today()
    reserva = Reserva(_cliente_demo(), hoy + timedelta(days=10),
                      hoy + timedelta(days=12), adultos=2)
    reserva.agregar_habitacion(HabitacionEstandar("111", 1, Decimal("50.00")))
    reserva.calcular_total()

    assert reserva.cancelar("Cambio de planes") == Decimal("0.00")


def test_no_se_puede_cancelar_una_reserva_ya_iniciada():
    hoy = date.today()
    reserva = Reserva(_cliente_demo(), hoy + timedelta(days=1),
                      hoy + timedelta(days=3), adultos=2)
    reserva.agregar_habitacion(HabitacionEstandar("112", 1, Decimal("50.00")))
    reserva.confirmar()
    reserva.registrar_check_in()

    with pytest.raises(TransicionInvalidaError):
        reserva.cancelar("Ya no viajo")


# ===========================================================================
# FABRICA
# ===========================================================================
def test_la_fabrica_devuelve_la_clase_correcta():
    fila = {"codigo": "SUI", "numero": "401", "piso": 4,
            "tarifa_base": Decimal("85.00"), "id_habitacion": 23,
            "estado": "DISPONIBLE"}
    habitacion = FabricaHabitaciones.desde_fila(fila)

    assert isinstance(habitacion, HabitacionSuite)
    assert habitacion.capacidad() == 3


def test_la_fabrica_rechaza_un_tipo_desconocido():
    with pytest.raises(ValorInvalidoError):
        FabricaHabitaciones.crear("XXX", numero="999", piso=1,
                                  tarifa_base=Decimal("10.00"))

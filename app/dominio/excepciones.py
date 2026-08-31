"""Excepciones propias del dominio del Hotel Aurora.

Tener excepciones propias permite que la capa web distinga un error de negocio
(que se le muestra al usuario con un mensaje claro) de un error tecnico
(que se registra y produce una pagina 500).
"""


class ErrorDominio(Exception):
    """Clase base de todos los errores del dominio."""


class ReglaNegocioError(ErrorDominio):
    """Se incumplio una regla del negocio. El mensaje es apto para el usuario."""


class TransicionInvalidaError(ErrorDominio):
    """Se intento un cambio de estado que la maquina de estados no permite."""


class ValorInvalidoError(ErrorDominio):
    """Un dato no cumple el formato o el rango esperado."""

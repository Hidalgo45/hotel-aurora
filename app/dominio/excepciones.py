"""QUE HACE: define los cuatro tipos de error propios del sistema.

SI PREGUNTAN POR ESTE ARCHIVO:
"Sirven para distinguir 'la persona hizo algo que no se puede' de 'el
programa se rompio'. Lo primero se muestra como un mensaje amable en
pantalla; lo segundo va a la pagina de error."

- ReglaNegocioError: se rompio una regla del hotel (demasiados huespedes)
- TransicionInvalidaError: se intento un paso imposible (salida sin entrada)
- ValorInvalidoError: un dato mal formado (numero de habitacion con letras)
- ErrorDominio: la base de los tres, para poder atraparlos todos juntos
"""


class ErrorDominio(Exception):
    """Clase base de todos los errores del dominio."""


class ReglaNegocioError(ErrorDominio):
    """Se incumplio una regla del negocio. El mensaje es apto para el usuario."""


class TransicionInvalidaError(ErrorDominio):
    """Se intento un cambio de estado que la maquina de estados no permite."""


class ValorInvalidoError(ErrorDominio):
    """Un dato no cumple el formato o el rango esperado."""

"""Jerarquia de personas del Hotel Aurora.

Segunda demostracion de herencia y polimorfismo: Persona es abstracta y cada
rol concreto define sus propios permisos y su descripcion.
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import date

from werkzeug.security import check_password_hash, generate_password_hash

from .excepciones import ValorInvalidoError


class Persona(ABC):
    """Datos y comportamiento comunes a cualquier persona del sistema."""

    def __init__(self, cedula: str, nombres: str, apellidos: str, email: str,
                 telefono: str | None = None, id_usuario: int | None = None) -> None:
        if not str(cedula).isdigit() or len(str(cedula)) != 10:
            raise ValorInvalidoError("La cedula debe tener exactamente 10 digitos.")
        if "@" not in email:
            raise ValorInvalidoError("El correo electronico no tiene un formato valido.")

        self.id_usuario = id_usuario
        self._cedula = str(cedula)
        self._nombres = nombres.strip().title()
        self._apellidos = apellidos.strip().title()
        self._email = email.strip().lower()
        self._telefono = telefono

    @property
    def cedula(self) -> str:
        return self._cedula

    @property
    def email(self) -> str:
        return self._email

    @property
    def nombres(self) -> str:
        return self._nombres

    def nombre_completo(self) -> str:
        return f"{self._nombres} {self._apellidos}"

    @abstractmethod
    def descripcion_rol(self) -> str:
        """Nombre del rol tal como se muestra en la interfaz."""

    @abstractmethod
    def permisos(self) -> list[str]:
        """Acciones que esta persona puede realizar en el sistema."""

    def puede(self, accion: str) -> bool:
        """Polimorfismo en accion: la respuesta depende del tipo real."""
        return accion in self.permisos()

    def __str__(self) -> str:
        return f"{self.nombre_completo()} ({self.descripcion_rol()})"


class Usuario(Persona):
    """Persona que inicia sesion. Encapsula el manejo de la contrasena."""

    def __init__(self, *args, password_hash: str | None = None, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.__password_hash = password_hash   # privado: nunca sale de la clase

    def establecer_clave(self, clave_plana: str) -> None:
        if len(clave_plana) < 8:
            raise ValorInvalidoError(
                "La contrasena debe tener al menos 8 caracteres.")
        self.__password_hash = generate_password_hash(clave_plana)

    def verificar_clave(self, clave_plana: str) -> bool:
        if not self.__password_hash:
            return False
        return check_password_hash(self.__password_hash, clave_plana)

    @property
    def hash_guardado(self) -> str | None:
        """Solo para que el repositorio pueda persistirlo."""
        return self.__password_hash

    def descripcion_rol(self) -> str:
        return "Usuario"

    def permisos(self) -> list[str]:
        return ["ver_catalogo"]


class Administrador(Usuario):
    """Acceso total: inventario, reservas, reportes y usuarios."""

    def descripcion_rol(self) -> str:
        return "Administrador"

    def permisos(self) -> list[str]:
        return ["ver_catalogo", "reservar", "gestionar_reservas",
                "gestionar_habitaciones", "ver_reportes", "gestionar_usuarios"]


class Recepcionista(Usuario):
    """Opera el dia a dia: check-in, check-out y creacion de reservas."""

    def __init__(self, *args, turno: str = "Matutino", **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self._turno = turno

    def descripcion_rol(self) -> str:
        return "Recepcionista"

    def permisos(self) -> list[str]:
        return ["ver_catalogo", "reservar", "gestionar_reservas"]


class Cliente(Usuario):
    """Huesped que reserva en linea."""

    def __init__(self, *args, fecha_nacimiento: date | None = None,
                 ciudad: str | None = None, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        if fecha_nacimiento and self._calcular_edad(fecha_nacimiento) < 18:
            raise ValorInvalidoError(
                "Debes ser mayor de edad para registrarte como huesped.")
        self._fecha_nacimiento = fecha_nacimiento
        self._ciudad = ciudad
        self._historial: list = []

    @staticmethod
    def _calcular_edad(nacimiento: date) -> int:
        hoy = date.today()
        return hoy.year - nacimiento.year - (
            (hoy.month, hoy.day) < (nacimiento.month, nacimiento.day))

    @property
    def edad(self) -> int | None:
        if self._fecha_nacimiento is None:
            return None
        return self._calcular_edad(self._fecha_nacimiento)

    def registrar_reserva(self, reserva) -> None:
        self._historial.append(reserva)

    def es_recurrente(self) -> bool:
        """Un cliente con 3 o mas estadias accede a beneficios."""
        return len(self._historial) >= 3

    def descripcion_rol(self) -> str:
        return "Huesped"

    def permisos(self) -> list[str]:
        return ["ver_catalogo", "reservar", "ver_mis_reservas"]


class FabricaUsuarios:
    """Crea el subtipo de usuario correcto segun el rol guardado en la base."""

    _MAPA: dict[str, type[Usuario]] = {
        "ADMIN": Administrador,
        "RECEPCION": Recepcionista,
        "CLIENTE": Cliente,
    }

    @classmethod
    def desde_fila(cls, fila: dict) -> Usuario:
        clase = cls._MAPA.get(fila["rol"], Usuario)
        extra = {}
        if clase is Cliente:
            extra = {"fecha_nacimiento": fila.get("fecha_nacimiento"),
                     "ciudad": fila.get("ciudad")}
        return clase(
            fila["cedula"], fila["nombres"], fila["apellidos"], fila["email"],
            telefono=fila.get("telefono"),
            id_usuario=fila["id_usuario"],
            password_hash=fila.get("password_hash"),
            **extra,
        )

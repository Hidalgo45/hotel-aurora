"""Usuarios y autenticacion sobre PostgreSQL."""
from __future__ import annotations

from werkzeug.security import generate_password_hash

from .. import db
from ..dominio.excepciones import ReglaNegocioError
from .base import RepositorioUsuarios


class UsuarioRepositorioPG(RepositorioUsuarios):

    _CAMPOS = """
        u.id_usuario, u.cedula, u.nombres, u.apellidos, u.email, u.telefono,
        u.password_hash, u.activo, ro.nombre AS rol,
        c.fecha_nacimiento, c.ciudad
    """

    def buscar_por_email(self, email: str) -> dict | None:
        return db.consultar_uno(f"""
            SELECT {self._CAMPOS}
              FROM usuario u
              JOIN rol ro ON ro.id_rol = u.id_rol
              LEFT JOIN cliente c ON c.id_cliente = u.id_usuario
             WHERE u.email = lower(%s) AND u.activo
        """, (email.strip(),))

    def obtener(self, id_usuario: int) -> dict | None:
        return db.consultar_uno(f"""
            SELECT {self._CAMPOS}
              FROM usuario u
              JOIN rol ro ON ro.id_rol = u.id_rol
              LEFT JOIN cliente c ON c.id_cliente = u.id_usuario
             WHERE u.id_usuario = %s
        """, (id_usuario,))

    def registrar_cliente(self, datos: dict) -> int:
        """Crea el usuario y su especializacion cliente en una transaccion."""
        if self.buscar_por_email(datos["email"]):
            raise ReglaNegocioError(
                "Ya existe una cuenta con este correo. Inicia sesion o "
                "recupera tu contrasena.")

        try:
            with db.obtener_conexion() as conn:
                fila = conn.execute("""
                    INSERT INTO usuario (id_rol, cedula, nombres, apellidos,
                                         email, telefono, password_hash)
                    VALUES ((SELECT id_rol FROM rol WHERE nombre = 'CLIENTE'),
                            %s, %s, %s, %s, %s, %s)
                    RETURNING id_usuario
                """, (datos["cedula"], datos["nombres"], datos["apellidos"],
                      datos["email"], datos.get("telefono"),
                      generate_password_hash(datos["password"]))).fetchone()

                id_usuario = fila["id_usuario"]

                conn.execute("""
                    INSERT INTO cliente (id_cliente, fecha_nacimiento, ciudad)
                    VALUES (%s, %s, %s)
                """, (id_usuario, datos["fecha_nacimiento"], datos.get("ciudad")))

            return id_usuario

        except Exception as e:                                # noqa: BLE001
            texto = str(e).split("\n")[0]
            if "ck_usuario_cedula" in texto:
                raise ReglaNegocioError(
                    "La cedula debe tener exactamente 10 digitos.") from None
            if "usuario_cedula_key" in texto:
                raise ReglaNegocioError(
                    "Ya existe una cuenta registrada con esa cedula.") from None
            if "usuario_email_key" in texto:
                raise ReglaNegocioError(
                    "Ya existe una cuenta con este correo.") from None
            if "ck_cliente_mayor_edad" in texto:
                raise ReglaNegocioError(
                    "Debes ser mayor de 18 anos para registrarte.") from None
            if "ck_usuario_email" in texto:
                raise ReglaNegocioError(
                    "El correo electronico no tiene un formato valido.") from None
            if "ck_usuario_telefono" in texto:
                raise ReglaNegocioError(
                    "El telefono debe tener entre 7 y 15 digitos.") from None
            raise

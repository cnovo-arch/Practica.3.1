from __future__ import annotations

from uuid import uuid4


class Usuario:
    """Representa a una persona que interactúa con la tienda."""

    def __init__(self, nombre: str, email: str) -> None:
        """Crea un usuario validando nombre y correo electrónico."""
        if not isinstance(nombre, str) or not nombre.strip():
            raise ValueError("El nombre no puede estar vacío.")
        if not isinstance(email, str) or not self._email_valido(email):
            raise ValueError("El correo electrónico no tiene un formato válido.")

        self.id: str = str(uuid4())
        self.nombre: str = nombre.strip()
        self.email: str = email.strip()

    @staticmethod
    def _email_valido(email: str) -> bool:
        """Comprueba de forma sencilla que el correo tenga un formato básico."""
        email = email.strip()
        return "@" in email and "." in email.rsplit("@", 1)[-1] and " " not in email

    def is_admin(self) -> bool:
        """Indica si el usuario tiene permisos de administrador."""
        return False

    def __str__(self) -> str:
        """Devuelve una descripción legible del usuario."""
        return f"{self.nombre} | ID: {self.id[:8]} | Email: {self.email}"


class Cliente(Usuario):
    """Usuario que puede realizar compras en la tienda."""

    def __init__(self, nombre: str, email: str, direccion_postal: str) -> None:
        """Crea un cliente con una dirección postal."""
        super().__init__(nombre, email)
        if not isinstance(direccion_postal, str) or not direccion_postal.strip():
            raise ValueError("La dirección postal no puede estar vacía.")
        self.direccion_postal: str = direccion_postal.strip()

    def __str__(self) -> str:
        """Devuelve una descripción del cliente y su dirección."""
        return f"Cliente: {super().__str__()} | Dirección: {self.direccion_postal}"


class Administrador(Usuario):
    """Usuario encargado de gestionar la tienda."""

    def is_admin(self) -> bool:
        """Indica que este usuario tiene rol de administrador."""
        return True

    def __str__(self) -> str:
        """Devuelve una descripción del administrador."""
        return f"Administrador: {super().__str__()}"

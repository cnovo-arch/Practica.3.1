from __future__ import annotations

from numbers import Real
from uuid import uuid4


class Producto:
    """Representa un producto genérico disponible en la tienda."""

    def __init__(self, nombre: str, precio: float, stock: int) -> None:
        """Crea un producto validando sus datos básicos."""
        if not isinstance(nombre, str) or not nombre.strip():
            raise ValueError("El nombre del producto no puede estar vacío.")
        if isinstance(precio, bool) or not isinstance(precio, Real):
            raise TypeError("El precio debe ser un número.")
        if precio < 0:
            raise ValueError("El precio no puede ser negativo.")
        if isinstance(stock, bool) or not isinstance(stock, int):
            raise TypeError("El stock debe ser un número entero.")
        if stock < 0:
            raise ValueError("El stock no puede ser negativo.")

        self.id: str = str(uuid4())
        self.nombre: str = nombre.strip()
        self.precio: float = float(precio)
        self.stock: int = stock

    def hay_stock(self, cantidad: int) -> bool:
        """Indica si existe stock suficiente para la cantidad solicitada."""
        self._validar_cantidad(cantidad, permitir_cero=True)
        return self.stock >= cantidad

    def actualizar_stock(self, cantidad: int) -> None:
        """Aumenta o reduce el stock sin permitir valores negativos."""
        if isinstance(cantidad, bool) or not isinstance(cantidad, int):
            raise TypeError("La cantidad de stock debe ser un número entero.")

        nuevo_stock = self.stock + cantidad
        if nuevo_stock < 0:
            raise ValueError(
                f"Stock insuficiente para {self.nombre}: "
                f"stock actual={self.stock}, cambio={cantidad}."
            )
        self.stock = nuevo_stock

    @staticmethod
    def _validar_cantidad(cantidad: int, permitir_cero: bool = False) -> None:
        """Valida que una cantidad sea un entero con signo permitido."""
        if isinstance(cantidad, bool) or not isinstance(cantidad, int):
            raise TypeError("La cantidad debe ser un número entero.")
        if permitir_cero and cantidad < 0:
            raise ValueError("La cantidad no puede ser negativa.")
        if not permitir_cero and cantidad <= 0:
            raise ValueError("La cantidad debe ser positiva.")

    def __str__(self) -> str:
        """Devuelve una descripción legible del producto."""
        return (
            f"{self.nombre} | ID: {self.id[:8]} | "
            f"Precio: {self.precio:.2f} € | Stock: {self.stock}"
        )


class ProductoElectronico(Producto):
    """Producto electrónico con garantía expresada en meses."""

    def __init__(
        self,
        nombre: str,
        precio: float,
        stock: int,
        garantia_meses: int,
    ) -> None:
        """Crea un producto electrónico con su periodo de garantía."""
        super().__init__(nombre, precio, stock)
        if isinstance(garantia_meses, bool) or not isinstance(garantia_meses, int):
            raise TypeError("La garantía debe ser un número entero de meses.")
        if garantia_meses < 0:
            raise ValueError("La garantía no puede ser negativa.")
        self.garantia_meses: int = garantia_meses

    def __str__(self) -> str:
        """Devuelve la descripción del producto incluyendo la garantía."""
        return (
            f"{super().__str__()} | Electrónico | "
            f"Garantía: {self.garantia_meses} meses"
        )


class ProductoRopa(Producto):
    """Producto de ropa con talla y color."""

    def __init__(
        self,
        nombre: str,
        precio: float,
        stock: int,
        talla: str,
        color: str,
    ) -> None:
        """Crea una prenda validando talla y color."""
        super().__init__(nombre, precio, stock)
        if not isinstance(talla, str) or not talla.strip():
            raise ValueError("La talla no puede estar vacía.")
        if not isinstance(color, str) or not color.strip():
            raise ValueError("El color no puede estar vacío.")
        self.talla: str = talla.strip()
        self.color: str = color.strip()

    def __str__(self) -> str:
        """Devuelve la descripción del producto incluyendo talla y color."""
        return (
            f"{super().__str__()} | Ropa | "
            f"Talla: {self.talla} | Color: {self.color}"
        )

from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING
from uuid import uuid4

if TYPE_CHECKING:
    try:
        from .Producto import Producto
        from .Usuario import Cliente
    except ImportError:
        from models.Producto import Producto
        from models.Usuario import Cliente


class Pedido:
    """Representa un pedido realizado por un cliente."""

    def __init__(self, cliente: Cliente, productos: dict[Producto, int]) -> None:
        """Crea un pedido y conserva el precio de cada producto en la compra."""
        if not productos:
            raise ValueError("Un pedido debe contener al menos un producto.")

        self.id: str = str(uuid4())
        self.cliente: Cliente = cliente
        self.productos: dict[Producto, int] = dict(productos)
        self.precios_unitarios: dict[str, float] = {
            producto.id: producto.precio for producto in self.productos
        }
        self.fecha_pedido: datetime = datetime.now()

    def calcular_total(self) -> float:
        """Calcula el importe total usando los precios de la fecha del pedido."""
        return sum(
            self.precios_unitarios[producto.id] * cantidad
            for producto, cantidad in self.productos.items()
        )

    def __str__(self) -> str:
        """Devuelve un resumen legible del pedido, cliente, líneas y total."""
        lineas = [
            f"Pedido {self.id[:8]} | Cliente: {self.cliente.nombre}",
            f"Fecha: {self.fecha_pedido:%d/%m/%Y %H:%M:%S}",
        ]
        for producto, cantidad in self.productos.items():
            precio = self.precios_unitarios[producto.id]
            subtotal = precio * cantidad
            lineas.append(f"  - {producto.nombre} x{cantidad}: {subtotal:.2f} €")
        lineas.append(f"Total: {self.calcular_total():.2f} €")
        return "\n".join(lineas)

from __future__ import annotations

from typing import Dict, List

try:
    from ..models.Pedido import Pedido
    from ..models.Producto import Producto
    from ..models.Usuario import Administrador, Cliente, Usuario
except ImportError:
    # Permite ejecutar main.py directamente desde la carpeta del proyecto.
    from models.Pedido import Pedido
    from models.Producto import Producto
    from models.Usuario import Administrador, Cliente, Usuario


class TiendaService:
    """Centraliza las operaciones principales de la tienda online."""

    def __init__(self) -> None:
        """Inicializa los repositorios en memoria de usuarios, productos y pedidos."""
        self.usuarios: Dict[str, Usuario] = {}
        self.productos: Dict[str, Producto] = {}
        self.pedidos: List[Pedido] = []

    def registrar_usuario(
        self,
        tipo: str,
        nombre: str,
        email: str,
        direccion_postal: str | None = None,
    ) -> Usuario:
        """Registra un cliente o administrador y devuelve el objeto creado."""
        if not isinstance(tipo, str) or not tipo.strip():
            raise ValueError("El tipo de usuario no puede estar vacío.")

        tipo_normalizado = tipo.strip().lower()

        if tipo_normalizado == "cliente":
            if not direccion_postal or not direccion_postal.strip():
                raise ValueError("Un cliente necesita dirección postal.")
            usuario: Usuario = Cliente(nombre, email, direccion_postal)
        elif tipo_normalizado in {"admin", "administrador"}:
            usuario = Administrador(nombre, email)
        else:
            raise ValueError("El tipo de usuario debe ser 'cliente' o 'administrador'.")

        self.usuarios[usuario.id] = usuario
        return usuario

    def anadir_producto(self, producto: Producto) -> None:
        """Añade un producto válido al inventario."""
        if not isinstance(producto, Producto):
            raise TypeError("Solo se pueden añadir objetos de tipo Producto.")
        if producto.id in self.productos:
            raise ValueError("Ya existe un producto con ese identificador.")
        self.productos[producto.id] = producto

    def eliminar_producto(self, producto_id: str) -> Producto:
        """Elimina y devuelve un producto del inventario por su identificador."""
        if not isinstance(producto_id, str) or not producto_id.strip():
            raise ValueError("El identificador del producto no puede estar vacío.")
        if producto_id not in self.productos:
            raise KeyError("El producto indicado no existe en el inventario.")
        return self.productos.pop(producto_id)

    def listar_productos(self) -> List[Producto]:
        """Devuelve una copia de la lista de productos del inventario."""
        return list(self.productos.values())

    def realizar_pedido(self, usuario_id: str, cantidades: Dict[str, int]) -> Pedido:
        """Crea un pedido comprobando usuario, productos y stock previamente."""
        if not isinstance(usuario_id, str) or not usuario_id.strip():
            raise ValueError("El identificador del usuario no puede estar vacío.")

        usuario = self.usuarios.get(usuario_id)
        if usuario is None:
            raise ValueError("El usuario indicado no existe.")
        if not isinstance(usuario, Cliente):
            raise ValueError("Solo un cliente puede realizar pedidos.")
        if not isinstance(cantidades, dict) or not cantidades:
            raise ValueError("El pedido debe contener al menos un producto.")

        productos_pedido: Dict[Producto, int] = {}

        # Se comprueba todo antes de modificar el inventario para evitar
        # actualizaciones parciales si alguna línea del pedido falla.
        for producto_id, cantidad in cantidades.items():
            if not isinstance(producto_id, str) or not producto_id.strip():
                raise ValueError("Todos los identificadores de producto deben ser válidos.")
            if isinstance(cantidad, bool) or not isinstance(cantidad, int) or cantidad <= 0:
                raise ValueError("Las cantidades deben ser enteros positivos.")

            producto = self.productos.get(producto_id)
            if producto is None:
                raise ValueError(f"No existe el producto con ID {producto_id}.")
            if not producto.hay_stock(cantidad):
                raise ValueError(
                    f"Stock insuficiente para {producto.nombre}. "
                    f"Disponible: {producto.stock}, solicitado: {cantidad}."
                )
            productos_pedido[producto] = cantidad

        # Solo después de superar todas las comprobaciones se modifica el stock.
        for producto, cantidad in productos_pedido.items():
            producto.actualizar_stock(-cantidad)

        pedido = Pedido(usuario, productos_pedido)
        self.pedidos.append(pedido)
        return pedido

    def listar_pedidos_usuario(self, usuario_id: str) -> List[Pedido]:
        """Devuelve los pedidos de un usuario ordenados por fecha ascendente."""
        if usuario_id not in self.usuarios:
            raise ValueError("El usuario indicado no existe.")

        pedidos = [
            pedido for pedido in self.pedidos if pedido.cliente.id == usuario_id
        ]
        return sorted(pedidos, key=lambda pedido: pedido.fecha_pedido)


    def buscar_usuario(self, usuario_id: str) -> Usuario | None:
        """Busca y devuelve un usuario por su identificador único."""
        return self.usuarios.get(usuario_id)


    def buscar_producto(self, producto_id: str) -> Producto | None:
        """Busca y devuelve un producto por su identificador único."""
        return self.productos.get(producto_id)

"""
Punto de entrada de la aplicación FastAPI (Práctica 2 - Parte 1).
Expone la funcionalidad de la Tienda Online como una API REST.
"""


from datetime import datetime
from typing import List, Optional
from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from models.Producto import Producto, ProductoElectronico, ProductoRopa
from Services.Tienda_service import TiendaService

app = FastAPI(
    title="API Tienda Online • UIE",
    description="Servicio REST para gestión de usuarios, productos y pedidos.",
    version="1.0.0"
)

# Habilitar CORS para permitir que el frontend web (HTML) se conecte
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Instancia central de tu servicio
tienda = TiendaService()


# 1. ESQUEMAS PYDANTIC (VALIDACIÓN Y SERIALIZACIÓN)


# --- Esquemas de Usuario ---
class UsuarioCreate(BaseModel):
    nombre: str = Field(..., example="Ana García")
    email: str = Field(..., example="ana@example.com")
    tipo: str = Field(..., example="cliente", description="'cliente' o 'administrador'")
    direccion_postal: Optional[str] = Field(None, example="Rúa Nova 10, Vigo")


class UsuarioRead(BaseModel):
    id: str
    nombre: str
    email: str
    es_admin: bool
    direccion_postal: Optional[str] = None


# --- Esquemas de Producto ---
class ProductoCreate(BaseModel):
    tipo: str = Field(default="generico", example="electronico")
    nombre: str = Field(..., example="Teclado mecánico")
    precio: float = Field(..., gt=0, example=89.90)
    stock: int = Field(..., ge=0, example=15)
    meses_garantia: Optional[int] = Field(None, example=24)
    talla: Optional[str] = Field(None, example="M")
    color: Optional[str] = Field(None, example="Negro")


class ProductoRead(BaseModel):
    id: str
    tipo: str
    nombre: str
    precio: float
    stock: int
    meses_garantia: Optional[int] = None
    talla: Optional[str] = None
    color: Optional[str] = None


# --- Esquemas de Pedido ---
class PedidoItemCreate(BaseModel):
    producto_id: str
    cantidad: int = Field(..., gt=0)


class PedidoCreate(BaseModel):
    cliente_id: str
    items: List[PedidoItemCreate]


class PedidoItemRead(BaseModel):
    producto_id: str
    nombre_producto: str
    cantidad: int
    precio_unitario: float
    subtotal: float


class PedidoRead(BaseModel):
    id: str
    fecha: datetime
    cliente_id: str
    cliente_nombre: str
    items: List[PedidoItemRead]
    total: float


# 2. ENDPOINTS HTTP


@app.get("/", tags=["General"])
def inicio():
    return {"mensaje": "API Tienda Online funcionando", "docs": "/docs"}


# --- Usuarios ---
@app.post("/usuarios", response_model=UsuarioRead, status_code=status.HTTP_201_CREATED, tags=["Usuarios"])
def crear_usuario(payload: UsuarioCreate):
    try:
        nuevo_user = tienda.registrar_usuario(
            tipo=payload.tipo,
            nombre=payload.nombre,
            email=payload.email,
            direccion_postal=payload.direccion_postal
        )
        return UsuarioRead(
            id=nuevo_user.id,
            nombre=nuevo_user.nombre,
            email=nuevo_user.email,
            es_admin=nuevo_user.is_admin(),
            direccion_postal=getattr(nuevo_user, "direccion_postal", None)
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@app.get("/usuarios", response_model=List[UsuarioRead], tags=["Usuarios"])
def listar_usuarios():
    return [
        UsuarioRead(
            id=u.id,
            nombre=u.nombre,
            email=u.email,
            es_admin=u.is_admin(),
            direccion_postal=getattr(u, "direccion_postal", None)
        )
        for u in tienda.usuarios.values()
    ]


@app.get("/usuarios/{usuario_id}", response_model=UsuarioRead, tags=["Usuarios"])
def obtener_usuario(usuario_id: str):
    u = tienda.buscar_usuario(usuario_id)
    if not u:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return UsuarioRead(
        id=u.id,
        nombre=u.nombre,
        email=u.email,
        es_admin=u.is_admin(),
        direccion_postal=getattr(u, "direccion_postal", None)
    )


# --- Productos ---
@app.post("/productos", response_model=ProductoRead, status_code=status.HTTP_201_CREATED, tags=["Productos"])
def crear_producto(payload: ProductoCreate):
    t = payload.tipo.strip().lower()
    if t == "electronico":
        if payload.meses_garantia is None:
            raise HTTPException(status_code=400, detail="Falta el campo 'meses_garantia'.")
        prod = ProductoElectronico(payload.nombre, payload.precio, payload.stock, payload.meses_garantia)
    elif t == "ropa":
        if not payload.talla or not payload.color:
            raise HTTPException(status_code=400, detail="Faltan los campos 'talla' o 'color'.")
        prod = ProductoRopa(payload.nombre, payload.precio, payload.stock, payload.talla, payload.color)
    else:
        prod = Producto(payload.nombre, payload.precio, payload.stock)

    tienda.anadir_producto(prod)
    return ProductoRead(
        id=prod.id,
        tipo=t,
        nombre=prod.nombre,
        precio=prod.precio,
        stock=prod.stock,
        meses_garantia=getattr(prod, "garantia_meses", None),
        talla=getattr(prod, "talla", None),
        color=getattr(prod, "color", None)
    )


@app.get("/productos", response_model=List[ProductoRead], tags=["Productos"])
def listar_productos():
    resultado = []
    for p in tienda.listar_productos():
        tipo = "electronico" if isinstance(p, ProductoElectronico) else "ropa" if isinstance(p, ProductoRopa) else "generico"
        resultado.append(ProductoRead(
            id=p.id,
            tipo=tipo,
            nombre=p.nombre,
            precio=p.precio,
            stock=p.stock,
            meses_garantia=getattr(p, "garantia_meses", None),
            talla=getattr(p, "talla", None),
            color=getattr(p, "color", None)
        ))
    return resultado


@app.get("/productos/{producto_id}", response_model=ProductoRead, tags=["Productos"])
def obtener_producto(producto_id: str):
    p = tienda.buscar_producto(producto_id)
    if not p:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    tipo = "electronico" if isinstance(p, ProductoElectronico) else "ropa" if isinstance(p, ProductoRopa) else "generico"
    return ProductoRead(
        id=p.id,
        tipo=tipo,
        nombre=p.nombre,
        precio=p.precio,
        stock=p.stock,
        meses_garantia=getattr(p, "garantia_meses", None),
        talla=getattr(p, "talla", None),
        color=getattr(p, "color", None)
    )


@app.delete("/productos/{producto_id}", response_model=dict, tags=["Productos"])
def eliminar_producto(producto_id: str):
    try:
        p = tienda.eliminar_producto(producto_id)
        return {"mensaje": f"Producto '{p.nombre}' eliminado correctamente."}
    except KeyError:
        raise HTTPException(status_code=404, detail="Producto no encontrado")


# --- Pedidos ---
@app.post("/pedidos", response_model=PedidoRead, status_code=status.HTTP_201_CREATED, tags=["Pedidos"])
def crear_pedido(payload: PedidoCreate):
    try:
        cantidades = {item.producto_id: item.cantidad for item in payload.items}
        # Reutilizamos tu método realizar_pedido de TiendaService con toda su lógica
        pedido = tienda.realizar_pedido(payload.cliente_id, cantidades)

        items_salida = [
            PedidoItemRead(
                producto_id=prod.id,
                nombre_producto=prod.nombre,
                cantidad=cant,
                precio_unitario=pedido.precios_unitarios[prod.id],
                subtotal=round(cant * pedido.precios_unitarios[prod.id], 2)
            )
            for prod, cant in pedido.productos.items()
        ]

        return PedidoRead(
            id=pedido.id,
            fecha=pedido.fecha_pedido,
            cliente_id=pedido.cliente.id,
            cliente_nombre=pedido.cliente.nombre,
            items=items_salida,
            total=pedido.calcular_total()
        )
    except (ValueError, TypeError) as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@app.get("/usuarios/{cliente_id}/pedidos", response_model=List[PedidoRead], tags=["Pedidos"])
def listar_pedidos_cliente(cliente_id: str):
    if not tienda.buscar_usuario(cliente_id):
        raise HTTPException(status_code=404, detail="Usuario no existe")

    pedidos = tienda.listar_pedidos_usuario(cliente_id)
    resultado = []
    for ped in pedidos:
        items = [
            PedidoItemRead(
                producto_id=prod.id,
                nombre_producto=prod.nombre,
                cantidad=cant,
                precio_unitario=ped.precios_unitarios[prod.id],
                subtotal=round(cant * ped.precios_unitarios[prod.id], 2)
            )
            for prod, cant in ped.productos.items()
        ]
        resultado.append(PedidoRead(
            id=ped.id,
            fecha=ped.fecha_pedido,
            cliente_id=ped.cliente.id,
            cliente_nombre=ped.cliente.nombre,
            items=items,
            total=ped.calcular_total()
        ))
    return resultado


# Poblamos datos iniciales de prueba para que al arrancar no esté vacío
def _poblar_datos():
    c1 = tienda.registrar_usuario("cliente", "Carlos", "carlos@example.com", "Rúa Principal 1, Pontevedra")
    c2 = tienda.registrar_usuario("cliente", "Ana", "ana@example.com", "Rúa Nova 10, Vigo")
    tienda.registrar_usuario("administrador", "Marta", "marta@tienda.com")
    
    p1 = ProductoElectronico("Auriculares inalámbricos", 59.99, 12, 24)
    p2 = ProductoRopa("Camiseta básica", 19.95, 20, "M", "Negro")
    p3 = ProductoRopa("Sudadera", 44.50, 10, "L", "Azul")
    for p in (p1, p2, p3):
        tienda.anadir_producto(p)

_poblar_datos()
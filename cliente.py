"""
Cliente Python independiente para la API de la Tienda Online (Práctica 2 Parte 1 y 2).
Usa la librería 'requests' y se comunica únicamente por HTTP.
"""
import sys
import requests

# Si estás probando en tu ordenador:
BASE_URL = "http://127.0.0.1:8000"
# Para probar en el ordenador de un usuario en la misma Wi-Fi, poner la IP:
# BASE_URL = "http://192.168.1.34:8000"

if len(sys.argv) > 1 and sys.argv[1].startswith("http"):
    BASE_URL = sys.argv[1]

print(f"Conectando a la API en: {BASE_URL}")

# 1. Crear un usuario cliente
print("\n[1] Creando usuario...")
resp_user = requests.post(f"{BASE_URL}/usuarios", json={
    "nombre": "Estudiante UIE",
    "email": "alumno@uie.edu",
    "tipo": "cliente",
    "direccion_postal": "Campus UIE, A Coruña"
})
print(f"Estado HTTP: {resp_user.status_code}")
user_data = resp_user.json()
cliente_id = user_data["id"]
print(f"Usuario registrado: {user_data['nombre']} (ID: {cliente_id})")

# 2. Consultar lista de usuarios
print("\n[2] Consultando lista de usuarios...")
usuarios = requests.get(f"{BASE_URL}/usuarios").json()
print(f"Total de usuarios en la tienda: {len(usuarios)}")

# 3. Crear productos (uno electrónico y uno de ropa)
print("\n[3] Creando productos...")
p_elec = requests.post(f"{BASE_URL}/productos", json={
    "tipo": "electronico",
    "nombre": "Smartwatch Deportivo",
    "precio": 89.95,
    "stock": 15,
    "meses_garantia": 24
}).json()

p_ropa = requests.post(f"{BASE_URL}/productos", json={
    "tipo": "ropa",
    "nombre": "Gorra Bordada",
    "precio": 15.00,
    "stock": 30,
    "talla": "Única",
    "color": "Negro"
}).json()
print(f"Productos creados: '{p_elec['nombre']}' y '{p_ropa['nombre']}'")

# 4. Consultar catálogo de productos
print("\n[4] Consultando productos disponibles...")
catalogo = requests.get(f"{BASE_URL}/productos").json()
print(f"Total de productos en catálogo: {len(catalogo)}")

# 5. Crear un pedido para el usuario
print("\n[5] Realizando un pedido...")
pedido_payload = {
    "cliente_id": cliente_id,
    "items": [
        {"producto_id": p_elec["id"], "cantidad": 1},
        {"producto_id": p_ropa["id"], "cantidad": 2}
    ]
}
resp_pedido = requests.post(f"{BASE_URL}/pedidos", json=pedido_payload)
print(f"Estado HTTP: {resp_pedido.status_code}")
pedido_data = resp_pedido.json()
print(f"Pedido #{pedido_data['id']} creado con éxito. Total: {pedido_data['total']}€")

# 6. Consultar histórico de pedidos del usuario
print("\n[6] Consultando pedidos del cliente...")
pedidos_cliente = requests.get(f"{BASE_URL}/usuarios/{cliente_id}/pedidos").json()
print(f"Historial de compras: {len(pedidos_cliente)} pedido(s) encontrado(s)")
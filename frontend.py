"""
Interfaz Gráfica de Usuario en Streamlit (Práctica 2 Parte 3).
Consume la API REST de FastAPI mediante peticiones HTTP con 'requests'.
No importa modelos de dominio ni la capa de servicio directamente.

Ejecución:
    streamlit run frontend.py
"""
import streamlit as st
import requests
import os

st.set_page_config(
    page_title="Tienda Online • UIE",
    page_icon="🛒",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================================
# BARRA LATERAL: CONEXIÓN Y USUARIO ACTIVO
# ============================================================================

st.sidebar.title("⚙️ Conexión API")
base_url = st.sidebar.text_input(
    "URL del Servidor FastAPI",
    value=os.getenv("API_URL", "http://localhost:8000"),
    help="Si conectas con otro ordenador en LAN, pon ej. http://172.16.18.152:8000"
).rstrip("/")

# Comprobar estado de la API
try:
    check = requests.get(f"{base_url}/", timeout=2)
    if check.status_code == 200:
        st.sidebar.success("🟢 Servidor FastAPI Conectado")
    else:
        st.sidebar.warning(f"🟡 Estado HTTP: {check.status_code}")
except Exception:
    st.sidebar.error("🔴 Servidor no detectado. Inicia uvicorn en el puerto 8000.")


# Funciones auxiliares para consumir la API
def obtener_usuarios():
    try:
        r = requests.get(f"{base_url}/usuarios", timeout=3)
        return r.json() if r.status_code == 200 else []
    except Exception:
        return []

def obtener_productos():
    try:
        r = requests.get(f"{base_url}/productos", timeout=3)
        return r.json() if r.status_code == 200 else []
    except Exception:
        return []

# Carrito en la memoria de la sesión
if "carrito" not in st.session_state:
    st.session_state.carrito = {}

lista_usuarios = obtener_usuarios()
usuario_activo = None

st.sidebar.markdown("---")
st.sidebar.subheader("👤 Usuario Activo")

if lista_usuarios:
    mapa_usuarios = {
        f"{u['nombre']} ({'ADMIN' if u['es_admin'] else 'CLIENTE'})": u
        for u in lista_usuarios
    }
    seleccion = st.sidebar.selectbox("Seleccionar usuario:", list(mapa_usuarios.keys()))
    usuario_activo = mapa_usuarios[seleccion]

    if usuario_activo["es_admin"]:
        st.sidebar.info("🔒 Rol: **Administrador** (Gestión de tienda, no compra)")
    else:
        st.sidebar.success(f"🛍️ Rol: **Cliente**\n📍 Envío: {usuario_activo.get('direccion_postal', 'Sin dirección')}")
else:
    st.sidebar.warning("No hay usuarios. Registra uno en la pestaña 'Gestión de Usuarios'.")


# ============================================================================
# PESTAÑAS PRINCIPALES
# ============================================================================

st.title("🛒 Tienda Online • Panel de Control")
st.caption("Arquitectura de Software • Práctica 2 (FastAPI + Streamlit)")

tab_catalogo, tab_nuevo_prod, tab_usuarios, tab_historial = st.tabs([
    "🛍️ Catálogo y Compra",
    "➕ Añadir Producto",
    "👥 Gestión de Usuarios",
    "📦 Historial de Pedidos"
])

# ----------------------------------------------------------------------------
# PESTAÑA 1: CATÁLOGO Y CARRITO
# ----------------------------------------------------------------------------
with tab_catalogo:
    col_prod, col_cart = st.columns([7, 5])

    productos = obtener_productos()

    with col_prod:
        st.subheader("Productos Disponibles")
        st.caption("Petición: `GET /productos`")

        filtro = st.radio("Filtrar por categoría:", ["Todos", "Genérico", "Electrónico", "Ropa"], horizontal=True)
        
        prods_filtrados = productos
        if filtro != "Todos":
            prods_filtrados = [p for p in productos if p.get("tipo", "").lower() == filtro.lower()]

        if not prods_filtrados:
            st.info("No hay productos disponibles en esta categoría.")
        else:
            for p in prods_filtrados:
                with st.container(border=True):
                    c1, c2, c3 = st.columns([5, 3, 3])
                    with c1:
                        st.markdown(f"**{p['nombre']}**")
                        st.caption(f"Tipo: {p.get('tipo', 'generico').capitalize()}")
                        if p.get("meses_garantia"):
                            st.caption(f"🛡️ Garantía: {p['meses_garantia']} meses")
                        if p.get("talla") or p.get("color"):
                            st.caption(f"📏 Talla: {p.get('talla')} | Color: {p.get('color')}")
                    with c2:
                        st.markdown(f"### {p['precio']:.2f} €")
                        if p["stock"] > 5:
                            st.success(f"Stock: {p['stock']}")
                        elif p["stock"] > 0:
                            st.warning(f"Stock: {p['stock']} (¡Últimas!)")
                        else:
                            st.error("Agotado")
                    with c3:
                        if p["stock"] > 0:
                            if st.button("➕ Al Carrito", key=f"btn_add_{p['id']}"):
                                cant_actual = st.session_state.carrito.get(p["id"], {"cantidad": 0})["cantidad"]
                                if cant_actual < p["stock"]:
                                    st.session_state.carrito[p["id"]] = {
                                        "nombre": p["nombre"],
                                        "precio": p["precio"],
                                        "cantidad": cant_actual + 1
                                    }
                                    st.rerun()
                                else:
                                    st.error("Stock máximo alcanzado.")
                        else:
                            st.button("Agotado", disabled=True, key=f"btn_dis_{p['id']}")

    with col_cart:
        st.subheader("🛒 Carrito de Compra")
        st.caption("Petición al confirmar: `POST /pedidos`")

        if not st.session_state.carrito:
            st.info("El carrito está vacío. Añade productos desde el catálogo.")
        else:
            total_pedido = 0.0
            eliminar_ids = []

            for pid, item in st.session_state.carrito.items():
                subtotal = item["precio"] * item["cantidad"]
                total_pedido += subtotal
                
                c_nom, c_tot, c_del = st.columns([6, 3, 2])
                with c_nom:
                    st.write(f"**{item['nombre']}**")
                    st.caption(f"{item['precio']:.2f} € x {item['cantidad']}")
                with c_tot:
                    st.markdown(f"**{subtotal:.2f} €**")
                with c_del:
                    if st.button("❌", key=f"del_{pid}"):
                        eliminar_ids.append(pid)

            for pid in eliminar_ids:
                del st.session_state.carrito[pid]
                st.rerun()

            st.markdown("---")
            st.markdown(f"### Total a pagar: `{total_pedido:.2f} €`")

            col_b1, col_b2 = st.columns(2)
            with col_b1:
                if st.button("Vaciar Carrito"):
                    st.session_state.carrito = {}
                    st.rerun()
            with col_b2:
                if st.button("✅ Confirmar Pedido", type="primary"):
                    if not usuario_activo:
                        st.error("Selecciona un usuario en la barra lateral.")
                    elif usuario_activo["es_admin"]:
                        st.error("❌ Los Administradores no pueden realizar compras. Selecciona un Cliente.")
                    else:
                        items_payload = [
                            {"producto_id": pid, "cantidad": it["cantidad"]}
                            for pid, it in st.session_state.carrito.items()
                        ]
                        payload = {
                            "cliente_id": usuario_activo["id"],
                            "items": items_payload
                        }
                        try:
                            resp = requests.post(f"{base_url}/pedidos", json=payload)
                            if resp.status_code == 201:
                                data = resp.json()
                                st.success(f"🎉 Pedido #{data['id'][:8]} realizado con éxito. Total: {data['total']:.2f} €")
                                st.session_state.carrito = {}
                                st.rerun()
                            else:
                                st.error(f"Error {resp.status_code}: {resp.json().get('detail', 'Error al procesar pedido')}")
                        except Exception as e:
                            st.error(f"Error de red: {e}")


# ----------------------------------------------------------------------------
# PESTAÑA 2: AÑADIR PRODUCTO (CREACIÓN DINÁMICA DE PRODUCTOS)
# ----------------------------------------------------------------------------
with tab_nuevo_prod:
    st.subheader("➕ Añadir Nuevo Producto al Inventario")
    st.caption("Petición: `POST /productos`")

    with st.form("form_alta_producto", clear_on_submit=True):
        tipo_producto = st.selectbox(
            "Categoría de Producto:",
            ["generico", "electronico", "ropa"],
            format_func=lambda x: "Genérico" if x == "generico" else "Electrónico (+Meses de Garantía)" if x == "electronico" else "Ropa (+Talla y Color)"
        )

        col1, col2 = st.columns(2)
        with col1:
            nombre = st.text_input("Nombre del Producto *", placeholder="Ej. Ratón Inalámbrico Pro")
            precio = st.number_input("Precio (€) *", min_value=0.01, value=39.99, step=1.0)
        with col2:
            stock = st.number_input("Cantidad en Stock *", min_value=1, value=15, step=1)

        # Campos dinámicos condicionales según el tipo
        garantia = None
        talla = None
        color = None

        if tipo_producto == "electronico":
            st.markdown("##### Especificaciones de Electrónica")
            garantia = st.number_input("Garantía en meses *", min_value=1, value=24, step=6)
        elif tipo_producto == "ropa":
            st.markdown("##### Especificaciones de Ropa")
            c_t, c_c = st.columns(2)
            with c_t:
                talla = st.selectbox("Talla *", ["XS", "S", "M", "L", "XL", "40", "42", "44"])
            with c_c:
                color = st.text_input("Color *", value="Azul Marino")

        guardar_prod = st.form_submit_button("💾 Guardar Producto en la Tienda", type="primary")

        if guardar_prod:
            if not nombre.strip():
                st.error("El nombre del producto no puede estar vacío.")
            else:
                payload = {
                    "tipo": tipo_producto,
                    "nombre": nombre.strip(),
                    "precio": float(precio),
                    "stock": int(stock),
                    "meses_garantia": int(garantia) if garantia else None,
                    "talla": talla,
                    "color": color
                }
                try:
                    res = requests.post(f"{base_url}/productos", json=payload)
                    if res.status_code == 201:
                        p_creado = res.json()
                        st.success(f"✅ ¡Producto '{p_creado['nombre']}' creado con éxito (ID: `{p_creado['id'][:8]}`!)")
                    else:
                        st.error(f"Error {res.status_code}: {res.json().get('detail')}")
                except Exception as e:
                    st.error(f"Error al conectar con FastAPI: {e}")


# ----------------------------------------------------------------------------
# PESTAÑA 3: GESTIÓN DE USUARIOS
# ----------------------------------------------------------------------------
with tab_usuarios:
    c_u1, c_u2 = st.columns([6, 6])

    with c_u1:
        st.subheader("Usuarios Registrados en el Sistema")
        st.caption("Petición: `GET /usuarios`")
        if lista_usuarios:
            for u in lista_usuarios:
                with st.container(border=True):
                    rol_tag = "ADMINISTRADOR" if u["es_admin"] else "CLIENTE"
                    st.markdown(f"**{u['nombre']}** (`{rol_tag}`)")
                    st.write(f"📧 {u['email']}")
                    if u.get("direccion_postal"):
                        st.caption(f"📍 {u['direccion_postal']}")
        else:
            st.info("No hay usuarios registrados.")

    with c_u2:
        st.subheader("➕ Registrar Nuevo Usuario")
        st.caption("Petición: `POST /usuarios`")

        with st.form("form_alta_usuario", clear_on_submit=True):
            tipo_u = st.selectbox("Tipo de Usuario:", ["cliente", "administrador"], format_func=lambda x: x.capitalize())
            nombre_u = st.text_input("Nombre Completo *", placeholder="Ej. Laura Silva")
            email_u = st.text_input("Correo Electrónico *", placeholder="laura@example.com")
            
            direccion_u = None
            if tipo_u == "cliente":
                direccion_u = st.text_input("Dirección Postal *", placeholder="Rúa Real 10, A Coruña")

            guardar_u = st.form_submit_button("Crear Usuario", type="primary")

            if guardar_u:
                if not nombre_u.strip() or not email_u.strip():
                    st.error("El nombre y el correo son obligatorios.")
                elif tipo_u == "cliente" and (not direccion_u or not direccion_u.strip()):
                    st.error("Un cliente debe tener dirección postal obligatoria.")
                else:
                    payload = {
                        "tipo": tipo_u,
                        "nombre": nombre_u.strip(),
                        "email": email_u.strip(),
                        "direccion_postal": direccion_u.strip() if direccion_u else None
                    }
                    try:
                        res = requests.post(f"{base_url}/usuarios", json=payload)
                        if res.status_code == 201:
                            st.success(f"✅ Usuario '{nombre_u}' creado con éxito.")
                            st.rerun()
                        else:
                            st.error(f"Error {res.status_code}: {res.json().get('detail')}")
                    except Exception as e:
                        st.error(f"Error de red: {e}")


# ----------------------------------------------------------------------------
# PESTAÑA 4: HISTORIAL DE PEDIDOS
# ----------------------------------------------------------------------------
with tab_historial:
    st.subheader("📦 Historial de Pedidos")
    st.caption("Petición: `GET /usuarios/{cliente_id}/pedidos`")

    if not usuario_activo:
        st.warning("Selecciona un usuario en la barra lateral.")
    elif usuario_activo["es_admin"]:
        st.info("El usuario seleccionado es Administrador. Los administradores no realizan pedidos.")
    else:
        try:
            r = requests.get(f"{base_url}/usuarios/{usuario_activo['id']}/pedidos")
            if r.status_code == 200:
                pedidos = r.json()
                if not pedidos:
                    st.info(f"El cliente {usuario_activo['nombre']} no tiene compras realizadas.")
                else:
                    st.write(f"Historial de **{len(pedidos)}** pedido(s):")
                    for ped in pedidos:
                        with st.container(border=True):
                            c_info, c_total = st.columns([8, 4])
                            with c_info:
                                st.markdown(f"#### Pedido #{ped['id'][:8]}")
                                st.caption(f"Fecha: {ped['fecha'].replace('T', ' ')[:16]}")
                                for it in ped["items"]:
                                    st.write(f"• **{it['nombre_producto']}** x{it['cantidad']} @ {it['precio_unitario']:.2f} € = **{it['subtotal']:.2f} €**")
                            with c_total:
                                st.metric("Total", f"{ped['total']:.2f} €")
            else:
                st.error(f"Error HTTP {r.status_code}")
        except Exception as e:
            st.error(f"Error al obtener historial: {e}")
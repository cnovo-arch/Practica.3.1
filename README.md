## Este nuevo proyecto conocido como Practica.3.1. muestra mi manejo básico en las herramientas de Git y GitHub


Mi nombre es Carlos Novo Moruja y la aplicación de Python que voy a desarrollar consiste en una tienda en la se añaden y se quitan una serie de productos y está formada por sus clases que representan la tienda, los productos, los tipos de usuarios que hay en esta tienda, y los pedidos.


A continuación voy a especificar algunos de sus términos




## 1.  Estructura del proyecto

La estructura principal del proyecto es la siguiente:

```text
tienda-online/
├── models
├── Services
├── cliente.py
├── frontend.py
├── main.py
├── requirements.txt
├── Dockerfile
├── .gitignore
└── README.md
```

**Nota:** `main.py` es un nombre de ejemplo para el archivo que contiene la aplicación FastAPI.

## 2. Requisitos previos

Para ejecutar el proyecto es necesario tener instalado:

- Python 3.12 o una versión compatible con las dependencias del proyecto.
- Docker Desktop.
- Git, para clonar el repositorio.

## 3. Ejecución del backend

La API de FastAPI se ejecuta por separado del contenedor de la interfaz.

Desde la carpeta del backend, inicia el servidor con:

```bash
python -m uvicorn main:app --host 0.0.0.0 --port 8000
```

Si la rama por defecto del git es `master` u otro nombre distinto de `main`, sustituye `main` por ese nombre.

La documentación interactiva de la API estará disponible en:

http://localhost:8000/docs

Mantén el servidor en ejecución mientras utilizas la tienda.

## 5. Ejecución con Docker

### 5.0. Obtención contenedor

El contenedor está disponible en "doc", aunque descargarlo es sencillo si completas los siguientes pasos

### 5.1. Construir la imagen

Desde la carpeta raíz del proyecto, donde se encuentra el Dockerfile, ejecuta:

```bash
docker build -t tienda-online .
```

### 5.2. Iniciar el contenedor

Con la API funcionando en el puerto 8000, ejecuta:

```bash
docker run --name tienda-ui -p 8501:8501 -e API_URL=http://host.docker.internal:8000 tienda-online
```

La variable `API_URL` configura la dirección de la API que utilizará la interfaz. En Docker Desktop para Windows, `host.docker.internal` permite acceder desde el contenedor a los servicios que se ejecutan en el ordenador anfitrión.

### 5.3. Acceder a la interfaz gráfica

Abre el siguiente enlace en el navegador:

http://localhost:8501

### 5.4. Detener y eliminar el contenedor

Para detenerlo:

```bash
docker stop tienda-ui
```

Para eliminarlo:

```bash
docker rm tienda-ui
```

Si necesitas volver a crearlo con el mismo nombre, primero debes eliminar el contenedor anterior.

## 6. Cliente de pruebas

El archivo `cliente.py` realiza solicitudes HTTP a la API para comprobar operaciones relacionadas con usuarios, productos y pedidos.

El cliente necesita que el backend esté disponible en la dirección configurada. Sus operaciones de creación pueden añadir registros a los datos de la aplicación, por lo que conviene revisar los datos antes de ejecutar las pruebas repetidamente.

## 7. Consideraciones importantes

- MI CONTENEDOR NO PERMITE DE MOMENTO LA EJECUCIÓN EN EL PROTOCOLO TCP/IP, SÓLO FUNCIONA EN LOCAL (Intentaré corregirlo para que se pueda ver desde cualquier dispositivo en HTTP)
- El contenedor descrito en esta versión ejecuta el cliente de pruebas y la interfaz Streamlit.
- La API de FastAPI se ejecuta por separado en el ordenador anfitrión.
- El puerto `8000` se utiliza para la API y el puerto `8501` para la interfaz Streamlit.
- No se deben subir contraseñas, tokens, credenciales ni archivos de configuración que contengan información privada.

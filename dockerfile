# Para iniciar voy a crear la imagen de nuestro docker con Python preinstalado sobre la distribución más ligera de Linux.
FROM python:3.12-alpine

# A continuación creo el directorio sobre el que se va a trabajar
WORKDIR /app

# Copio los archivos principales sobre los que se va a basar el proyecto
COPY . .

# Instalo las dependencias necesarias para el proyecto
RUN pip install --no-cache-dir -r requirements.txt     

## Añado --no-cache-dir para que no copie lo que hay dentro de __pycache__

## Este trozo de comando en principio es irrelevante ya que he creado ya el archivo .dockerignore, pero lo dejo por si acaso.

# Expone el puerto de la aplicación para que sea accessible desde fuera del ordenador y se pueda ejecutar el módulo de Streamlit (interfaz web)
EXPOSE 8501

# Ponemos el comando de arranque
CMD ["sh", "-c", "python cliente.py http://host.docker.internal:8000; exec streamlit run frontend.py --server.address=0.0.0.0 --server.port=8501"]

## Se ejecuta cliente.py y el streamlit de frontend.py para que se pueda acceder y modificar la tienda
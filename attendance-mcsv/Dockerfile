# Usamos una imagen base de Python 3.11 (puedes ajustarla)
FROM python:3.11-slim

# Establecemos el directorio de trabajo
WORKDIR /app

# Copiamos el archivo de requerimientos primero
COPY requirements.txt ./

# Instalamos las dependencias de Python
# --no-cache-dir reduce el tamaño de la imagen
RUN pip install --no-cache-dir -r requirements.txt

# Copiamos todo el código de la aplicación
# (app/, config.py, run.py, etc.)
COPY . .

# Exponemos el puerto 5000 que declaraste
EXPOSE 5000

# --- Comando para ejecutar la aplicación ---
#
# Para producción, no debes usar "python run.py".
# Debes usar un servidor WSGI como Gunicorn.
#
# 1. Asegúrate de que 'gunicorn' esté en tu requirements.txt
# 2. El comando asume que tu archivo 'run.py' define una variable 'app'
#    (ej. app = create_app() o app = Flask(__name__))
#    Si tu variable se llama diferente o está en otro archivo, ajusta "run:app"
#
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "run:app"]
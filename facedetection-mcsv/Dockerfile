# Usamos una imagen base de Python 3.11 (puedes ajustarla)
FROM python:3.11-slim

# Establecemos el directorio de trabajo
WORKDIR /app

# Copiamos el archivo de requerimientos primero
COPY requirements.txt ./

# Instalamos las dependencias de Python
# RUN pip install --no-cache-dir -r requirements.txt

RUN apt-get update && apt-get install -y --no-install-recommends build-essential g++ gcc python3-dev libgl1 libglib2.0-0 libsm6 libxext6 libxrender-dev libgomp1 && pip install --no-cache-dir -r requirements.txt && apt-get purge -y --auto-remove g++ gcc python3-dev && apt-get clean && rm -rf /var/lib/apt/lists/*

# Copiamos todo el código de la aplicación
COPY . .

# Exponemos el puerto 4000
EXPOSE 4000

# Comando para ejecutar con Gunicorn en producción
# CMD ["gunicorn", "--bind", "0.0.0.0:4000", "run:app"]
CMD ["python", "-m", "gunicorn", "--bind", "0.0.0.0:4000", "run:app"]
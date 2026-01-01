# Usamos una imagen base de Python 3.11 (puedes ajustarla)
FROM python:3.11-slim

# Establecemos el directorio de trabajo
WORKDIR /app

# Copiamos el archivo de requerimientos primero
COPY requirements.txt ./

# Instalamos las dependencias de Python
# --no-cache-dir reduce el tamaño de la imagen
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Exponemos el puerto 5000 que declaraste
EXPOSE 5000

# Comando para ejecutar con Gunicorn en producción
CMD ["python", "-m", "gunicorn", "--bind", "0.0.0.0:5000", "run:app"]
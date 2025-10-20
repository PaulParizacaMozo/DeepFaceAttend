import os

# Directorio base del proyecto
base_dir = os.path.abspath(os.path.dirname(__file__))

class Config:
    """Configuraciones para la aplicación Flask."""
    SQLALCHEMY_DATABASE_URI = "sqlite:///" + os.path.join(base_dir, "database.db")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JSON_SORT_KEYS = False # Opcional: Mantiene el orden de los campos en las respuestas JSON
    CORS_HEADERS = 'Content-Type'
    CORS_RESOURCES = {r"/*": {"origins": "*"}}  # Configuración de CORS para todas las rutas
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'attendance-system-with-face-recognition'

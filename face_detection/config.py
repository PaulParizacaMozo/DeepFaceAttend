# config.py

# --- Rutas y Nombres de Archivos ---
DB_PATH = 'database.sqlite'
CSV_OUTPUT_DIR = 'embeddings_csvs'

# --- Parámetros del Modelo y Reconocimiento ---
SIMILARITY_THRESHOLD = 0.39  # Umbral para considerar una coincidencia (0.0 a 1.0)
DETECTION_THRESHOLD = 0.8    # Umbral mínimo para detectar un rostro (0.0 a 1.0)

# --- Configuración de Red ---
SERVICE_URL = 'http://localhost:4000/process_frame'
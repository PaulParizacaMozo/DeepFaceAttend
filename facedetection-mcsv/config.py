# config.py
import os

# --- Path Configuration  ---
PROJECT_ROOT = os.path.abspath(os.path.dirname(__file__))
DB_PATH = os.path.join(os.path.dirname(PROJECT_ROOT), 'attendance-mcsv', 'database.db')
CSV_OUTPUT_DIR = os.path.join(PROJECT_ROOT, 'embeddings_csvs')

# --- Model and Recognition Parameters  ---
SIMILARITY_THRESHOLD = 0.50
DETECTION_THRESHOLD = 0.7

# --- Network Configuration  ---
SERVICE_URL = 'http://localhost:4000/process_frame'

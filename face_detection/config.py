# config.py
import os

# --- Path Configuration  ---
PROJECT_ROOT = os.path.abspath(os.path.dirname(__file__))
DB_PATH = os.path.join(os.path.dirname(PROJECT_ROOT), 'attendance-mcsv', 'database.db')
CSV_OUTPUT_DIR = os.path.join(PROJECT_ROOT, 'embeddings_csvs')

# --- Model and Recognition Parameters (No changes needed here) ---
SIMILARITY_THRESHOLD = 0.39
DETECTION_THRESHOLD = 0.7

# --- Network Configuration (No changes needed here) ---
SERVICE_URL = 'http://localhost:4000/process_frame'
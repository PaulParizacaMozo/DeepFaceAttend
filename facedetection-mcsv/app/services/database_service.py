import sqlite3
import os
import numpy as np
import pandas as pd
from .. import config

def load_known_faces_from_csv(course_name):
    """
    Carga embeddings conocidos desde un CSV específico del curso.
    El archivo debe estar en config.CSV_OUTPUT_DIR y tener columnas:
        id, embedding
    """
    known_face_db = {}

    # Construir ruta completa
    csv_path = os.path.join(config.CSV_OUTPUT_DIR, f"{course_name}.csv")

    if not os.path.exists(csv_path):
        print(f"[WARN] CSV file not found: {csv_path}")
        return known_face_db

    try:
        df = pd.read_csv(csv_path)

        # Validar columnas
        if not {'student_id', 'embedding'}.issubset(df.columns):
            print(f"[ERROR] CSV {csv_path} must contain 'id' and 'embedding' columns.")
            return known_face_db

        for _, row in df.iterrows():
            student_id = row['student_id']
            emb_str = row['embedding']

            if not isinstance(emb_str, str) or not emb_str.strip():
                print(f"  - Warning: Empty embedding for {student_id}. Skipping.")
                continue

            try:
                embedding = np.fromstring(emb_str, sep=';')
                known_face_db[student_id] = embedding
            except Exception as e:
                print(f"  - Error parsing embedding for {student_id}: {e}")

        print(f"[INFO] Loaded {len(known_face_db)} embeddings from {csv_path}")
        return known_face_db

    except Exception as e:
        print(f"[ERROR] Failed to read CSV {csv_path}: {e}")
        return {}
    
def prepare_vectorized_db(known_face_db):
    """
    Convierte el diccionario de embeddings a una matriz NumPy normalizada
    y un arreglo de etiquetas.
    """
    if not known_face_db:
        return None, None

    labels = list(known_face_db.keys())
    matrix = np.vstack(list(known_face_db.values())).astype('float32')

    # Normalizar cada embedding (para similitud del coseno)
    norms = np.linalg.norm(matrix, axis=1, keepdims=True)
    matrix = matrix / norms

    return matrix, labels
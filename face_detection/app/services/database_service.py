import sqlite3
import os
import numpy as np
import pandas as pd
from .. import config

def load_known_faces_from_db():
    known_face_db = {}
    
    if not os.path.exists(config.DB_PATH):
        print("Warning: Database not found. No faces will be recognized.")
        return known_face_db

    try:
        conn = sqlite3.connect(config.DB_PATH)
        cursor = conn.cursor()
        
        cursor.execute("SELECT cui, first_name, last_name, filepath_embeddings FROM students")
        persons = cursor.fetchall()
        conn.close()

        for cui, first_name, last_name, filepath in persons:
            full_name = f"{first_name} {last_name}"

            if not filepath or not os.path.exists(filepath):
                print(f"  - Warning: CSV file not found for {full_name}. Skipping.")
                continue
            
            try:
                df = pd.read_csv(filepath)

                # Se espera solo una fila con un embedding promedio
                if 'embedding' not in df.columns or df.empty:
                    print(f"  - Warning: Invalid embedding file for {full_name}.")
                    continue

                embedding_str = df['embedding'].iloc[0]
                embedding = np.fromstring(embedding_str, sep=';')

                known_face_db[cui] = embedding

            except Exception as e:
                print(f"  - Error reading {full_name}'s embedding: {e}")
                
        print(f"Success: Loaded {len(known_face_db)} known faces into memory.")
        return known_face_db

    except Exception as e:
        print(f"Error loading face database: {e}")
        return {}
    
def prepare_vectorized_db(known_face_db):
    """Convierte el diccionario a una matriz NumPy normalizada."""
    if not known_face_db:
        return None, None

    labels = list(known_face_db.keys())
    matrix = np.vstack(list(known_face_db.values())).astype('float32')

    # Normalizar cada embedding (para similitud del coseno)
    norms = np.linalg.norm(matrix, axis=1, keepdims=True)
    matrix = matrix / norms

    return matrix, labels
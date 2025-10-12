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
            
            df = pd.read_csv(filepath)
            embeddings = df['embedding'].apply(lambda x: np.fromstring(x, sep=';')).tolist()
            
            if embeddings:
                average_embedding = np.mean(np.array(embeddings), axis=0)
                known_face_db[cui] = average_embedding
        print(f"Success: Loaded {len(known_face_db)} known faces into memory.")
        return known_face_db

    except Exception as e:
        print(f"Error loading face database: {e}")
        return {}
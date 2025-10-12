# database_manager.py

import sqlite3
import os
import numpy as np
import pandas as pd
import config


"""
    Crea la tabla 'persons' en la base de datos si no existe.
"""
def setup_database():
    conn = sqlite3.connect(config.DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS persons (
            name TEXT PRIMARY KEY,
            csv_path TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

"""
    Guarda los embeddings en un CSV y actualiza la base de datos.
"""
def save_person_embeddings(person_name, embeddings_data):
    os.makedirs(config.CSV_OUTPUT_DIR, exist_ok=True)
    person_csv_path = os.path.join(config.CSV_OUTPUT_DIR, f"{person_name}.csv")
    df = pd.DataFrame(embeddings_data)
    df.to_csv(person_csv_path, index=False)
    # print(f"\n✅ Se guardaron {len(df)} embeddings en '{person_csv_path}'.")
    try:
        conn = sqlite3.connect(config.DB_PATH)
        cursor = conn.cursor()
        cursor.execute("INSERT OR REPLACE INTO persons (name, csv_path) VALUES (?, ?)", (person_name, person_csv_path))
        conn.commit()
        conn.close()
        print(f"Base de datos '{config.DB_PATH}' actualizada correctamente.")
    except sqlite3.Error as e:
        print(f"\nError al actualizar la base de datos: {e}")

"""
    Carga y promedia los embeddings de todas las personas en la DB.
"""
def load_known_faces_from_db():
    known_face_db = {}
    # print("\nCargando rostros conocidos desde la base de datos...")
    if not os.path.exists(config.DB_PATH):
        print(f"Advertencia: No se encontró la base de datos. No se reconocerá a nadie.")
        return known_face_db
    try:
        conn = sqlite3.connect(config.DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT name, csv_path FROM persons")
        persons = cursor.fetchall()
        conn.close()
        for name, csv_path in persons:
            if not os.path.exists(csv_path):
                print(f"  - Advertencia: No se encontró el archivo CSV '{csv_path}' para '{name}'. Saltando.")
                continue
            df = pd.read_csv(csv_path)
            embeddings = df['embedding'].apply(lambda x: np.fromstring(x, sep=';')).tolist()
            if embeddings:
                average_embedding = np.mean(np.array(embeddings), axis=0)
                known_face_db[name] = average_embedding
                print(f"  - Cargado y promediado perfil para: {name}")
        print(f"\nBase de datos cargada. {len(known_face_db)} personas conocidas en memoria.")
        return known_face_db
    except Exception as e:
        print(f"Error al cargar la base de datos de rostros: {e}")
        return {}
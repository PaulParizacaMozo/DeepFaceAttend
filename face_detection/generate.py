# generate.py

import cv2
import numpy as np
import os
import sys
import face_analyzer
import database_manager

"""
    Procesa una carpeta de imágenes para generar y guardar embeddings.
"""
def process_images_and_generate_embeddings(input_folder, person_name, model):
    database_manager.setup_database()
    embeddings_data = []
    image_files = sorted([f for f in os.listdir(input_folder) if f.lower().endswith(('.png', '.jpg', '.jpeg'))])

    if not image_files:
        print(f"Error: No se encontraron imágenes en la carpeta '{input_folder}'.")
        return

    print(f"\nProcesando {len(image_files)} imágenes para '{person_name}'...")

    for i, filename in enumerate(image_files):
        image_path = os.path.join(input_folder, filename)
        frame = cv2.imread(image_path)

        if frame is None:
            continue

        faces = model.get(frame)
        if not faces:
            continue
        
        best_face = max(faces, key=lambda face: face.det_score)
        
        if best_face.det_score < 0.50:
            continue
        
        embedding = best_face.embedding
        embedding_str = ';'.join(map(str, embedding))
        embeddings_data.append({'image_number': i + 1, 'embedding': embedding_str})
        print(f"  - Procesada '{filename}' exitosamente ({i+1}/{len(image_files)}).")
    
    if embeddings_data:
        database_manager.save_person_embeddings(person_name, embeddings_data)
    else:
        print("\nNo se pudo extraer ningún embedding de alta calidad.")


if __name__ == '__main__':
    if len(sys.argv) != 3:
        print("Uso: python generate.py <ruta_a_la_carpeta_de_imagenes> <nombre_de_la_persona>")
        sys.exit(1)
        
    input_folder_path = sys.argv[1]
    person_identity = sys.argv[2]
    
    if not os.path.isdir(input_folder_path):
        print(f"Error: La carpeta especificada no existe -> '{input_folder_path}'")
        sys.exit(1)

    face_model = face_analyzer.load_model()
    process_images_and_generate_embeddings(input_folder_path, person_identity, face_model)
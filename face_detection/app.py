from flask import Flask, request, jsonify
import cv2
import numpy as np
import pandas as pd
import insightface
from insightface.app import FaceAnalysis
import os
import time

app = Flask(__name__)

# --- CONFIGURACIÓN ---
PERSON_NAME = "shinji" 
FACES_DIR = 'detected_faces'
EMBEDDINGS_CSV = 'embeddings.csv'
os.makedirs(FACES_DIR, exist_ok=True)

# --- CARGA DEL MODELO ---
print("Cargando modelo de análisis facial...")
face_analysis_model = FaceAnalysis(allowed_modules=['detection', 'recognition'])
face_analysis_model.prepare(ctx_id=0, det_size=(640, 640))
print("Modelo cargado exitosamente.")

# --- ENDPOINTS DE LA API ---
@app.route('/process_frame', methods=['POST'])
def process_frame():
    if 'image' not in request.files:
        return jsonify({"error": "No se encontró ninguna imagen"}), 400
    file = request.files['image']
    
    img_stream = file.read()
    np_img = np.frombuffer(img_stream, np.uint8)
    frame = cv2.imdecode(np_img, cv2.IMREAD_COLOR)

    if frame is None:
        return jsonify({"error": "No se pudo decodificar la imagen"}), 400

    faces = face_analysis_model.get(frame)
    if not faces:
        return jsonify({"message": "No se detectaron rostros"}), 200
    
    saved_faces_count = 0
    for i, face in enumerate(faces):
        detection_score = face.det_score

        if detection_score < 0.5: # Umbral más estricto para mejor calidad
            print(f"Rostro {i}: Ignorado por bajo puntaje ({detection_score:.2f}).")
            continue
        print(f"Rostro {i}: Pasó el umbral de calidad ({detection_score:.2f}).")

        embedding = face.embedding
        final_crop = face.norm_crop # Intenta obtener el recorte alineado

        # Si 'norm_crop' falla, creamos un recorte manual como respaldo.
        if final_crop is None:
            print(f"Rostro {i}: 'norm_crop' falló. Creando recorte manual.")
            # Obtener las coordenadas del bounding box
            bbox = face.bbox.astype(int)
            x1, y1, x2, y2 = bbox
            
            y1 = max(0, y1)
            x1 = max(0, x1)
            y2 = min(frame.shape[0], y2)
            x2 = min(frame.shape[1], x2)
            manual_crop = frame[y1:y2, x1:x2]
            
            # Si el recorte manual tiene un tamaño válido, redimensionarlo
            if manual_crop.size > 0:
                final_crop = cv2.resize(manual_crop, (112, 112))
                print(f"Rostro {i}: Recorte manual creado y redimensionado a 112x112.")
            else:
                print(f"Rostro {i}: El recorte manual resultó en una imagen vacía. Se omite.")
                continue # Pasa al siguiente rostro

        if final_crop is not None and final_crop.size > 0:
            timestamp = int(time.time())
            
            image_filename = f"{PERSON_NAME}_{timestamp}_{i}.jpg"
            image_path = os.path.join(FACES_DIR, image_filename)
            cv2.imwrite(image_path, final_crop)
            print(f"Guardado rostro para '{PERSON_NAME}' en: {image_path}")
            
            embedding_str = ';'.join(map(str, embedding))
            new_entry = pd.DataFrame([{'name': PERSON_NAME, 'embedding': embedding_str}])

            if not os.path.exists(EMBEDDINGS_CSV):
                 new_entry.to_csv(EMBEDDINGS_CSV, mode='w', header=True, index=False)
            else:
                new_entry.to_csv(EMBEDDINGS_CSV, mode='a', header=False, index=False)
            
            saved_faces_count += 1
        else:
            print(f"Rostro {i}: Falló tanto 'norm_crop' como el recorte manual. Se omite.")

    return jsonify({"message": f"{saved_faces_count} de {len(faces)} rostro(s) guardado(s) como '{PERSON_NAME}'"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=4000)
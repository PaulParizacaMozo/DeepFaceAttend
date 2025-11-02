import cv2
import numpy as np
from .. import config
import time
import requests
from collections import defaultdict
import os
import datetime

base_dir = os.path.abspath(os.path.dirname(__file__))
CAPTURES_DIR = os.path.join(base_dir, '..', '..', 'captures')
os.makedirs(CAPTURES_DIR, exist_ok=True)
print(f"[INFO] Directorio de capturas asegurado en: {CAPTURES_DIR}")

CAMERA_CLIENT_URL = "http://localhost:6000/start_capture" 

def find_best_match(new_embedding, known_face_db, threshold):
    best_match_name = "Unknown"
    highest_similarity = threshold

    for name, known_embedding in known_face_db.items():
        similarity = np.dot(new_embedding, known_embedding) / (np.linalg.norm(new_embedding) * np.linalg.norm(known_embedding))

        if similarity > highest_similarity:
            highest_similarity = similarity
            best_match_name = name
            
    if best_match_name == "Unknown":
        return "Unknown", 0.0

    return best_match_name, highest_similarity

def find_best_match_vectorized(new_embedding, known_matrix, known_labels, threshold):
    """Versión vectorizada usando NumPy puro."""
    if known_matrix is None or known_labels is None or len(known_labels) == 0:
        return "Unknown", 0.0

    # Normalizar embedding de entrada
    new_embedding = new_embedding / np.linalg.norm(new_embedding)

    # Producto punto vectorizado (coseno)
    similarities = np.dot(known_matrix, new_embedding)  # (N,)

    # Buscar el índice con mayor similitud
    idx_max = np.argmax(similarities)
    best_sim = similarities[idx_max]

    if best_sim < threshold:
        return "Unknown", best_sim

    return known_labels[idx_max], float(best_sim)

def recognize_faces_in_frame_2(frame, face_model, known_matrix, known_labels, schedule_id=None):
    faces = face_model.get(frame)
    if not faces:
        return []

    recognized_faces = []
    for face in faces:
        if face.det_score < config.DETECTION_THRESHOLD:
            continue

        # --- Inicio del temporizador ---
        start_time = time.perf_counter()

        identity, confidence = find_best_match_vectorized(
            face.embedding, known_matrix, known_labels, config.SIMILARITY_THRESHOLD
        )

        # --- Fin del temporizador ---
        end_time = time.perf_counter()
        elapsed_time = end_time - start_time
        print(f"[DEBUG] Tiempo ejecución find_best_match_vectorized: {elapsed_time:.6f} segundos")

        # --- INICIO DE LÓGICA PARA GUARDAR IMAGEN ---
        try:
            # 1. Crear un nombre de archivo único
            now_str = datetime.datetime.now().strftime("%Y%m%d_%H%M%S_%f")
            file_identity = identity.replace(" ", "_").replace("/", "_")
            schedule_str = schedule_id or "NO_SCHEDULE"
            
            # 2. Crear subcarpeta para el schedule (ej: /captures/sched_abc123)
            schedule_capture_dir = os.path.join(CAPTURES_DIR, schedule_str)
            os.makedirs(schedule_capture_dir, exist_ok=True)
            
            # 3. Definir el nombre del archivo (ej: Kevin_Chambi_20251101_203000_123456.jpg)
            filename = f"{file_identity}_{now_str}.jpg"
            filepath = os.path.join(schedule_capture_dir, filename)

            # 4. Recortar la cara del frame original usando el bbox
            [x1, y1, x2, y2] = [int(v) for v in face.bbox]
            # Asegurar que las coordenadas no estén fuera de los límites
            y1_crop, y2_crop = max(0, y1), min(frame.shape[0], y2)
            x1_crop, x2_crop = max(0, x1), min(frame.shape[1], x2)
            
            cropped_face = frame[y1_crop:y2_crop, x1_crop:x2_crop]

            # 5. Guardar la imagen si el recorte es válido
            if cropped_face.size > 0:
                cv2.imwrite(filepath, cropped_face)
                print(f"[DEBUG] Rostro guardado en: {filepath}")
            else:
                print(f"[DEBUG] No se pudo guardar el rostro (tamaño 0) para {identity}")
                
        except Exception as e:
            print(f"[ERROR] No se pudo guardar la imagen del rostro: {e}")
        # --- FIN DE LÓGICA PARA GUARDAR IMAGEN ---

        recognized_faces.append({
            "identity": identity,
            "confidence": f"{confidence:.2f}" if identity != "Unknown" else "N/A"
        })

    return recognized_faces

def capture_and_recognize_faces(scheduler_id):
    print(f"[INFO] Sending remote capture command to camera client for attendance")
    
    payload = {
        "scheduler_id": scheduler_id,
        "duration": 1,  # minutos
        "interval": 30  # segundos
    }
    try:
        response = requests.post(CAMERA_CLIENT_URL, json=payload, timeout=10)
        if response.status_code == 200:
            print(f"[INFO] Camera client acknowledged start: {response.json()}")
        else:
            print(f"[ERROR] Camera client error: {response.status_code} - {response.text}")
    except requests.exceptions.RequestException as e:
        print(f"[ERROR] Failed to contact camera client: {e}")
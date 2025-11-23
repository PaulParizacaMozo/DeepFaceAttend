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
ATTENDANCE_UNKNOWN_URL = "http://127.0.0.1:5000/unknown-faces"

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
    print("simila: ")
    print(similarities)
    print("best: ")
    print(best_sim)
    print(threshold)
    if best_sim < threshold:
        return "Unknown", best_sim

    return known_labels[idx_max], float(best_sim)

def send_unknown_face_to_attendance(embedding, image_path, schedule_id):
    """
    Envía un rostro desconocido al microservicio de attendance para que quede
    registrado con embedding, horario y ruta de imagen.
    """
    if not schedule_id:
        print("[WARN] Unknown face sin schedule_id. No se enviará a attendance.")
        return

    try:
        embedding = np.asarray(embedding, dtype='float32').flatten()
        embedding_str = ';'.join(map(str, embedding))

        payload = {
            "schedule_id": schedule_id,  # ← sin int()
            "embedding": embedding_str,
            "image_path": image_path,
            "detected_at": datetime.datetime.utcnow().isoformat()
        }

        print(f"[INFO] Enviando Unknown face a {ATTENDANCE_UNKNOWN_URL} ...")
        resp = requests.post(ATTENDANCE_UNKNOWN_URL, json=payload, timeout=5)
        if 200 <= resp.status_code < 300:
            print(f"[INFO] Unknown face registrado en attendance: {resp.json()}")
        else:
            print(f"[ERROR] Attendance devolvió {resp.status_code}: {resp.text}")
    except Exception as e:
        print(f"[ERROR] No se pudo enviar Unknown face a attendance: {e}")


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
        filepath = None
        try:
            # 1. Crear un nombre de archivo único
            now_str = datetime.datetime.now().strftime("%Y%m%d_%H%M%S_%f")
            file_identity = identity.replace(" ", "_").replace("/", "_")
            schedule_str = schedule_id or "NO_SCHEDULE"
            
            # 2. Crear subcarpeta para el schedule (ej: /captures/<schedule_id>)
            schedule_capture_dir = os.path.join(CAPTURES_DIR, schedule_str)
            os.makedirs(schedule_capture_dir, exist_ok=True)
            
            # 3. Definir el nombre del archivo (ej: Kevin_Chambi_20251101_203000_123456.jpg)
            filename = f"{file_identity}_{now_str}.jpg"
            filepath = os.path.join(schedule_capture_dir, filename)

            # 4. Recortar la cara del frame original usando el bbox
            [x1, y1, x2, y2] = [int(v) for v in face.bbox]
            y1_crop, y2_crop = max(0, y1), min(frame.shape[0], y2)
            x1_crop, x2_crop = max(0, x1), min(frame.shape[1], x2)
            
            cropped_face = frame[y1_crop:y2_crop, x1_crop:x2_crop]

            # 5. Guardar la imagen si el recorte es válido
            if cropped_face.size > 0:
                cv2.imwrite(filepath, cropped_face)
                print(f"[DEBUG] Rostro guardado en: {filepath}")
            else:
                print(f"[DEBUG] No se pudo guardar el rostro (tamaño 0) para {identity}")
                filepath = None
                
        except Exception as e:
            print(f"[ERROR] No se pudo guardar la imagen del rostro: {e}")
            filepath = None
        # --- FIN DE LÓGICA PARA GUARDAR IMAGEN ---

        # --- NUEVO: si es Unknown, enviar a attendance ---
        if identity == "Unknown" and filepath is not None:
            send_unknown_face_to_attendance(
                embedding=face.embedding,
                image_path=filepath,
                schedule_id=schedule_id
            )

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
        "interval": 100  # segundos
    }
    try:
        response = requests.post(CAMERA_CLIENT_URL, json=payload, timeout=10)
        if response.status_code == 200:
            print(f"[INFO] Camera client acknowledged start: {response.json()}")
        else:
            print(f"[ERROR] Camera client error: {response.status_code} - {response.text}")
    except requests.exceptions.RequestException as e:
        print(f"[ERROR] Failed to contact camera client: {e}")

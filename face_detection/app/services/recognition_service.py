import numpy as np
from .. import config
import time

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

def recognize_faces_in_frame(frame, face_model, known_db):
    faces = face_model.get(frame)
    if not faces:
        return []

    recognized_faces = []
    for face in faces:
        if face.det_score < config.DETECTION_THRESHOLD:
            continue

        # --- Inicio del temporizador ---
        start_time = time.perf_counter()

        identity, confidence = find_best_match(
            face.embedding, 
            known_db, 
            config.SIMILARITY_THRESHOLD
        )

        # --- Fin del temporizador ---
        end_time = time.perf_counter()
        elapsed_time = end_time - start_time
        print(f"[DEBUG ANTERIOR] Tiempo ejecución find_best_match: {elapsed_time:.6f} segundos")

        
        recognized_faces.append({
            "identity": identity,
            "confidence": f"{confidence:.2f}" if identity != "Unknown" else "N/A"
        })
        
    return recognized_faces

def recognize_faces_in_frame_2(frame, face_model, known_matrix, known_labels):
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

        recognized_faces.append({
            "identity": identity,
            "confidence": f"{confidence:.2f}" if identity != "Unknown" else "N/A"
        })

    return recognized_faces
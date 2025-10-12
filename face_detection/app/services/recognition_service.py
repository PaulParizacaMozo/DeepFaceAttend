import numpy as np
from .. import config

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

def recognize_faces_in_frame(frame, face_model, known_db):
    faces = face_model.get(frame)
    if not faces:
        return []

    recognized_faces = []
    for face in faces:
        if face.det_score < config.DETECTION_THRESHOLD:
            continue

        identity, confidence = find_best_match(
            face.embedding, 
            known_db, 
            config.SIMILARITY_THRESHOLD
        )
        
        recognized_faces.append({
            "identity": identity,
            "confidence": f"{confidence:.2f}" if identity != "Unknown" else "N/A"
        })
        
    return recognized_faces
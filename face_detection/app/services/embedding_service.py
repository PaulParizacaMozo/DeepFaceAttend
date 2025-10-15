import cv2
import numpy as np
import pandas as pd
import os
from .. import config

def process_and_save_embeddings(image_files, student_id, face_model):
    if not image_files:
        print("Error: No image files provided for processing.")
        return None

    embeddings_data = []
    processed_count = 0

    for file in image_files:
        np_img = np.frombuffer(file.read(), np.uint8)
        frame = cv2.imdecode(np_img, cv2.IMREAD_COLOR)

        if frame is None:
            continue

        faces = face_model.get(frame)
        if not faces:
            continue
        best_face = max(faces, key=lambda face: face.det_score)
        if best_face.det_score < config.DETECTION_THRESHOLD:
            continue
        embedding = best_face.embedding
        embedding_str = ';'.join(map(str, embedding))
        embeddings_data.append({'image_number': processed_count + 1, 'embedding': embedding_str})
        processed_count += 1
    if not embeddings_data:
        print("Error: No high-quality embeddings could be extracted.")
        return None
    output_dir = config.CSV_OUTPUT_DIR
    os.makedirs(output_dir, exist_ok=True)
    filepath = os.path.join(output_dir, f"{student_id}.csv")
    df = pd.DataFrame(embeddings_data)
    df.to_csv(filepath, index=False)
    print(f"Success: Saved {len(df)} embeddings for student '{student_id}' to {filepath}")
    return filepath
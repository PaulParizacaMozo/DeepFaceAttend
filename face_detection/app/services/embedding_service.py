import cv2
import numpy as np
import pandas as pd
import os
from .. import config

# ==========================================================
# Servicio 1: Genera y guarda el embedding promedio del estudiante
# ==========================================================

def generate_student_embedding(image_files, student_id, face_model):
    if not image_files:
        print("Error: No image files provided for processing.")
        return False

    embeddings = []

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

        embeddings.append(best_face.embedding)

    if not embeddings:
        print("Error: No high-quality embeddings could be extracted.")
        return False

    # Calcular embedding promedio
    avg_embedding = np.mean(np.array(embeddings), axis=0)
    embedding_str = ';'.join(map(str, avg_embedding))

    # Guardar o actualizar en students.csv global
    output_dir = config.CSV_OUTPUT_DIR
    os.makedirs(output_dir, exist_ok=True)
    global_path = os.path.join(output_dir, "students.csv")

    if os.path.exists(global_path):
        df = pd.read_csv(global_path)
        if student_id in df['student_id'].values:
            df.loc[df['student_id'] == student_id, 'embedding'] = embedding_str
        else:
            df = pd.concat([df, pd.DataFrame([{'student_id': student_id, 'embedding': embedding_str}])], ignore_index=True)
    else:
        df = pd.DataFrame([{'student_id': student_id, 'embedding': embedding_str}])

    df.to_csv(global_path, index=False)
    print(f"Success: Saved/Updated averaged embedding for student '{student_id}'")
    return True


# ==========================================================
# Servicio 2: Asigna embedding del estudiante a un curso
# ==========================================================
def assign_student_to_course(student_id, course_id):
    """
    Copia el embedding del estudiante desde students.csv hacia el CSV del curso.
    """
    output_dir = config.CSV_OUTPUT_DIR
    global_path = os.path.join(output_dir, "students.csv")
    course_path = os.path.join(output_dir, f"{course_id}.csv")

    if not os.path.exists(global_path):
        print("Error: Global students.csv not found.")
        return False

    df_global = pd.read_csv(global_path)

    if student_id not in df_global['student_id'].values:
        print(f"Error: Embedding for student '{student_id}' not found in global CSV.")
        return False

    # Obtener embedding del estudiante
    embedding_str = df_global.loc[df_global['student_id'] == student_id, 'embedding'].iloc[0]
    new_entry = pd.DataFrame([{'student_id': student_id, 'embedding': embedding_str}])

    # Si ya existe CSV del curso, actualiza o agrega
    if os.path.exists(course_path):
        df_course = pd.read_csv(course_path)
        if student_id in df_course['student_id'].values:
            df_course.loc[df_course['student_id'] == student_id, 'embedding'] = embedding_str
        else:
            df_course = pd.concat([df_course, new_entry], ignore_index=True)
    else:
        df_course = new_entry

    # Guardar CSV del curso
    df_course.to_csv(course_path, index=False)
    print(f"Student '{student_id}' assigned to course '{course_id}'.")
    return True

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

# ==========================================================
# Servicio 3: Obtener embedding del estudiante desde students.csv
# ==========================================================
def get_student_embedding_from_csv(student_id):
    """
    Devuelve el embedding del estudiante como np.array(float32)
    buscándolo en students.csv. Si no existe o hay error → None.
    """
    output_dir = config.CSV_OUTPUT_DIR
    global_path = os.path.join(output_dir, "students.csv")

    if not os.path.exists(global_path):
        print(f"[ERROR] Global students.csv not found at {global_path}")
        return None

    try:
        df = pd.read_csv(global_path)
    except Exception as e:
        print(f"[ERROR] Failed to read {global_path}: {e}")
        return None

    # Validar columnas
    if 'student_id' not in df.columns or 'embedding' not in df.columns:
        print(f"[ERROR] CSV {global_path} must contain 'student_id' and 'embedding' columns.")
        return None

    sid_str = str(student_id)

    # Comparar casteando a string para evitar problemas de tipo (int vs str)
    row = df[df['student_id'].astype(str) == sid_str]
    if row.empty:
        print(f"[WARN] No embedding found for student_id={sid_str} in {global_path}")
        return None

    emb_str = row.iloc[0]['embedding']
    if not isinstance(emb_str, str) or not emb_str.strip():
        print(f"[WARN] Empty embedding string for student_id={sid_str}")
        return None

    try:
        emb_array = np.fromstring(emb_str, sep=';').astype('float32')
    except Exception as e:
        print(f"[ERROR] Failed to parse embedding for student_id={sid_str}: {e}")
        return None

    return emb_array

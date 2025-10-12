# app.py

from flask import Flask, request, jsonify
import cv2
import numpy as np
import config
import face_analyzer
import database_manager

app = Flask(__name__)

# --- INICIALIZACIÓN (se ejecuta una sola vez al arrancar) ---
face_analysis_model = face_analyzer.load_model()
known_face_db = database_manager.load_known_faces_from_db()

# --- ENDPOINT DE REGISTRO DE NUEVAS PERSONAS ---
@app.route('/register', methods=['POST'])
def register_person():
    """
    Recibe un nombre y N imágenes, extrae embeddings y los guarda en la DB.
    """
    global known_face_db
    
    # 1. Validar entradas
    if 'name' not in request.form:
        return jsonify({"error": "El campo 'name' es requerido."}), 400
    person_name = request.form['name']

    images = request.files.getlist('images')
    if not images:
        return jsonify({"error": "No se proporcionaron imágenes en el campo 'images'."}), 400

    # 2. Procesar cada imagen enviada
    embeddings_data = []
    print(f"\nIniciando proceso de registro para: {person_name}")
    for i, file in enumerate(images):
        np_img = np.frombuffer(file.read(), np.uint8)
        frame = cv2.imdecode(np_img, cv2.IMREAD_COLOR)

        if frame is None:
            print(f"  - Advertencia: No se pudo leer la imagen {i+1}. Saltando.")
            continue

        faces = face_analysis_model.get(frame)
        if not faces:
            print(f"  - Advertencia: No se detectó rostro en la imagen {i+1}. Saltando.")
            continue
        
        best_face = max(faces, key=lambda face: face.det_score)
        
        if best_face.det_score < config.DETECTION_THRESHOLD:
            print(f"  - Advertencia: Rostro en imagen {i+1} con bajo puntaje ({best_face.det_score:.2f}). Saltando.")
            continue
        
        embedding = best_face.embedding
        embedding_str = ';'.join(map(str, embedding))
        embeddings_data.append({'image_number': i + 1, 'embedding': embedding_str})
        print(f"  - Procesada imagen {i+1}/{len(images)} exitosamente.")
    
    # 3. Guardar los embeddings si se extrajo al menos uno
    if not embeddings_data:
        return jsonify({"error": "No se pudo extraer ningún embedding de alta calidad de las imágenes proporcionadas."}), 400

    database_manager.save_person_embeddings(person_name, embeddings_data)
    
    # 4. CRÍTICO: Recargar la base de datos en memoria para que el reconocimiento funcione de inmediato
    print("\nRegistro exitoso. Recargando la base de datos en memoria...")
    known_face_db = database_manager.load_known_faces_from_db()

    return jsonify({
        "status": "success",
        "message": f"Se registró a '{person_name}' con {len(embeddings_data)} embeddings de alta calidad."
    }), 201

# --- ENDPOINT DE RECONOCIMIENTO EN TIEMPO REAL ---
@app.route('/process_frame', methods=['POST'])
def process_frame():
    if 'image' not in request.files:
        return jsonify({"error": "No se encontró ninguna imagen"}), 400
    
    file = request.files['image']
    np_img = np.frombuffer(file.read(), np.uint8)
    frame = cv2.imdecode(np_img, cv2.IMREAD_COLOR)

    if frame is None:
        return jsonify({"error": "No se pudo decodificar la imagen"}), 400

    faces = face_analysis_model.get(frame)
    if not faces:
        return jsonify({"recognized_faces": [], "message": "No se detectaron rostros"})

    recognized_faces_in_frame = []
    for face in faces:
        if face.det_score < config.DETECTION_THRESHOLD:
            continue

        new_embedding = face.embedding
        best_match_name = "Desconocido"
        highest_similarity = config.SIMILARITY_THRESHOLD
        
        for name, known_embedding in known_face_db.items():
            similarity = np.dot(new_embedding, known_embedding) / (np.linalg.norm(new_embedding) * np.linalg.norm(known_embedding))
            if similarity > highest_similarity:
                highest_similarity = similarity
                best_match_name = name
        
        recognized_faces_in_frame.append({
            "identity": best_match_name,
            "confidence": f"{highest_similarity:.2f}" if best_match_name != "Desconocido" else "N/A"
        })
    return jsonify({"recognized_faces": recognized_faces_in_frame})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=4000)
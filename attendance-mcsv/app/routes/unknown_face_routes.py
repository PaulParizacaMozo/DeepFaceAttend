from flask import Blueprint, request, jsonify
from app import db
from app.models.unknown_face import UnknownFace
from app.models.schedule import Schedule
from app.schemas.unknown_face_schema import unknown_face_schema
from datetime import datetime
import requests
import numpy as np
import json

unknown_face_bp = Blueprint('unknown_face_bp', __name__, url_prefix='/unknown-faces')
FACEDETECTION_SERVICE_URL = "http://localhost:4000/processing/extract-embedding"

@unknown_face_bp.route('', methods=['POST'])
def create_unknown_face():
    data = request.get_json() or {}

    schedule_id = data.get('schedule_id')
    embedding = data.get('embedding')
    image_path = data.get('image_path')
    detected_at_str = data.get('detected_at')

    # Validaciones mínimas
    if not schedule_id or not embedding or not image_path:
        return jsonify({"error": "Fields 'schedule_id', 'embedding' and 'image_path' are required."}), 400

    # Verificar que el schedule existe
    schedule = Schedule.query.get(schedule_id)
    if not schedule:
        return jsonify({"error": f"Schedule with id {schedule_id} not found."}), 404

    # Parsear detected_at si viene, sino usar ahora
    if detected_at_str:
        try:
            detected_at = datetime.fromisoformat(detected_at_str)
        except ValueError:
            return jsonify({"error": "Invalid 'detected_at' format. Use ISO 8601."}), 400
    else:
        detected_at = datetime.utcnow()

    unknown_face = UnknownFace(
        schedule_id=schedule_id,
        embedding=embedding,
        image_path=image_path,
        detected_at=detected_at
    )

    db.session.add(unknown_face)
    db.session.commit()

    return unknown_face_schema.jsonify(unknown_face), 201

# Falta probar este endpoint
@unknown_face_bp.route('/match', methods=['POST'])
def match_unknown_faces():
    """
    1. Recibe foto del usuario.
    2. Pide embedding al servicio de IA (4000).
    3. Compara con UnknownFaces en BD.
    4. Devuelve coincidencias agrupadas.
    """
    if 'image' not in request.files:
        return jsonify({"message": "Se requiere una imagen"}), 400

    image_file = request.files['image']

    # 1. Obtener embedding del microservicio de IA
    try:
        # Rebobinar archivo para enviarlo via requests
        image_file.seek(0)
        files = {'image': (image_file.filename, image_file.read(), image_file.content_type)}
        
        response = requests.post(FACEDETECTION_SERVICE_URL, files=files, timeout=5)
        
        if response.status_code != 200:
            return jsonify({"message": "No se pudo procesar el rostro (IA Error)"}), 400
            
        data = response.json()
        target_embedding = np.array(data['embedding'], dtype='float32')
        
        # Normalizar vector de entrada
        norm = np.linalg.norm(target_embedding)
        target_embedding = target_embedding / norm

    except Exception as e:
        print(f"Error contactando Face Service: {e}")
        return jsonify({"message": "Error interno al procesar biometría"}), 500

    # 2. Obtener todos los UnknownFaces
    unknowns = UnknownFace.query.all()
    matches = []
    THRESHOLD = 0.45 # Umbral de similitud (Ajustar según necesidad, 0.4 - 0.6 suele estar bien)

    for face in unknowns:
        try:
            # Convertir string guardado "0.1;0.2;..." a numpy array
            db_emb = np.fromstring(face.embedding, sep=';', dtype='float32')
            
            # Normalizar vector de BD
            db_norm = np.linalg.norm(db_emb)
            db_emb = db_emb / db_norm

            # Calcular similitud coseno (Producto punto de vectores normalizados)
            similarity = np.dot(target_embedding, db_emb)

            if similarity > THRESHOLD:
                # Obtener info del horario
                schedule = Schedule.query.get(face.schedule_id)
                course_name = schedule.course.course_name if schedule and schedule.course else "Curso Desconocido"
                
                # Crear URL de imagen accesible (Ajustar según cómo sirvas estáticos)
                # Asumimos que tienes una ruta estática configurada o guardas URL completa
                # Por ahora devolvemos el path relativo.
                
                # OJO: Necesitarás una ruta en Flask para servir estas imágenes estáticas
                # ej: http://localhost:5000/captures/nombre_archivo.jpg
                full_image_url = f"http://localhost:4000/captures/{face.image_path.split('/')[-2]}/{face.image_path.split('/')[-1]}" 
                # Nota: La lógica de arriba asume estructura /captures/schedule_id/foto.jpg en el puerto 4000

                matches.append({
                    "unknown_face_id": face.id,
                    "similarity": float(similarity),
                    "image_url": full_image_url, 
                    "schedule_id": face.schedule_id,
                    "schedule_name": f"{schedule.start_time.strftime('%H:%M')} - {schedule.end_time.strftime('%H:%M')} | {course_name}",
                    "date": face.detected_at.strftime('%Y-%m-%d')
                })

        except Exception as e:
            print(f"Error procesando face {face.id}: {e}")
            continue

    # 3. Agrupar resultados por fecha y horario
    grouped_results = {}
    for match in matches:
        key = f"{match['date']}_{match['schedule_id']}"
        if key not in grouped_results:
            grouped_results[key] = {
                "date": match['date'],
                "schedule_name": match['schedule_name'],
                "schedule_id": match['schedule_id'],
                "faces": []
            }
        grouped_results[key]['faces'].append({
            "id": match['unknown_face_id'],
            "url": match['image_url'],
            "similarity": match['similarity']
        })

    # Convertir dict a lista ordenada por fecha
    final_response = list(grouped_results.values())
    final_response.sort(key=lambda x: x['date'], reverse=True)

    return jsonify(final_response), 200
from flask import Blueprint, request, jsonify, send_from_directory, current_app
from app import db
from app.models.unknown_face import UnknownFace
from app.models.schedule import Schedule
from app.schemas.unknown_face_schema import unknown_face_schema
from datetime import datetime
import requests
import os
import numpy as np
import json

from app.services.unknown_face_service import resolve_unknown_faces_for_student

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


# ==========================================================
# Resolver unknown faces para un student_id dado
# ==========================================================
@unknown_face_bp.route('/resolve', methods=['POST'])
def resolve_unknown_faces():
    """
    Body JSON:
    {
      "student_id": "719e8e13-9e56-49d6-a86d-47a8abeb6737",
      "threshold": 0.3   # opcional
    }

    - Resuelve UnknownFace para ese student_id.
    - Devuelve unknown_faces resueltos (sin embedding).
    - Devuelve cursos detectados para que el front decida dónde matricular.
    """
    data = request.get_json() or {}

    student_id = data.get('student_id')
    if not student_id:
        return jsonify({"error": "Field 'student_id' is required."}), 400

    if not isinstance(student_id, str):
        student_id = str(student_id)

    threshold = data.get('threshold')

    try:
        matched, detected_courses = resolve_unknown_faces_for_student(
            student_id,
            threshold=threshold
        )
    except ValueError as ve:
        # student no existe
        return jsonify({"error": str(ve)}), 404
    except RuntimeError as re:
        # sin embedding en facedetection
        return jsonify({"error": str(re)}), 400
    except Exception as e:
        print(f"[ERROR] Failed to resolve unknown faces: {e}")
        return jsonify({"error": "Internal error while resolving unknown faces."}), 500

    # ---- matches: incluye course_id / course_name para tu UI ----
    matches_json = []
    for uf, sim in matched:
        schedule = uf.schedule            # relación UnknownFace -> Schedule
        course = schedule.course if schedule else None

        matches_json.append({
            "id": uf.id,
            "schedule_id": uf.schedule_id,
            "course_id": course.id if course else None,
            "course_name": course.course_name if course else None,
            "image_path": uf.image_path,
            "detected_at": uf.detected_at.isoformat(),
            "student_id": uf.student_id,
            "resolved": uf.resolved,
            "similarity": sim,
        })

    # ---- cursos detectados (para la columna COURSES) ----
    courses_json = []
    for c in detected_courses:
        courses_json.append({
            "id": c.id,
            "course_code": c.course_code,
            "course_name": c.course_name,
            "semester": c.semester,
        })

    return jsonify({
        "status": "success",
        "student_id": student_id,
        "threshold": threshold if threshold is not None else None,
        "matched_count": len(matches_json),
        "matches": matches_json,
        "detected_courses_count": len(courses_json),
        "detected_courses": courses_json
    }), 200

@unknown_face_bp.route('/<int:unknown_id>/resolve-finish', methods=['POST'])
def finalize_unknown_face(unknown_id):
    """
    Marca un UnknownFace como resuelto.

    POST /unknown-faces/<unknown_id>/resolve-finish

    Sin body (o lo ignoramos). Solo:
      - uf.resolved = True
      - NO toca uf.student_id
    """
    # 1. Buscar UnknownFace
    uf = UnknownFace.query.get(unknown_id)
    if not uf:
        return jsonify({"error": f"UnknownFace with id={unknown_id} not found."}), 404

    # 2. Si ya estaba resuelto, devolver info y salir
    if uf.resolved:
        schedule = uf.schedule
        course = schedule.course if schedule else None
        return jsonify({
            "status": "already_resolved",
            "match": {
                "id": uf.id,
                "schedule_id": uf.schedule_id,
                "course_id": course.id if course else None,
                "course_name": course.course_name if course else None,
                "image_path": uf.image_path,
                "detected_at": uf.detected_at.isoformat(),
                "student_id": uf.student_id,   # puede ser None
                "resolved": uf.resolved,
            }
        }), 200

    # 3. Marcar como resuelto
    uf.resolved = True

    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        print(f"[ERROR] Failed to finalize unknown face {unknown_id}: {e}")
        return jsonify({"error": "Database error while finalizing unknown face."}), 500

    # 4. Respuesta con info útil para el front
    schedule = uf.schedule
    course = schedule.course if schedule else None

    return jsonify({
        "status": "success",
        "message": f"UnknownFace {unknown_id} marked as resolved.",
        "match": {
            "id": uf.id,
            "schedule_id": uf.schedule_id,
            "course_id": course.id if course else None,
            "course_name": course.course_name if course else None,
            "image_path": uf.image_path,
            "detected_at": uf.detected_at.isoformat(),
            "student_id": uf.student_id,   # sigue como esté (probablemente None)
            "resolved": uf.resolved,
        }
    }), 200


captures_bp = Blueprint('captures_bp', __name__, url_prefix='/captures')
@captures_bp.route('/<path:filename>', methods=['GET'])
def get_capture_image(filename):
    """
    Sirve imágenes desde la carpeta 'captures' ubicada en el proyecto hermano 'facedetection-mcsv'.
    """
    try:
        # 1. current_app.root_path apunta a: .../attendance-mcsv/app
        # 2. Subimos 2 niveles ('..', '..') para salir de 'app' y de 'attendance-mcsv'
        # 3. Entramos a 'facedetection-mcsv' y luego a 'captures'
        captures_dir = os.path.join(
            current_app.root_path, 
            '..', '..', 
            'facedetection-mcsv', 
            'captures'
        )
        captures_dir = os.path.abspath(captures_dir)
        print(f"Serving from: {captures_dir}")

        return send_from_directory(captures_dir, filename)
    except Exception as e:
        print(f"Error serving image: {e}")
        return jsonify({"error": "Image not found"}), 404
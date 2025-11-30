import os
import requests
from app import db  # Importación necesaria para actualizar la DB
from app.models.student import Student # Importación del modelo

# ==========================================================
# Función: Actualiza el estado de embeddings a True
# ==========================================================
def update_student_embedding_status(student_id):
    try:
        student = Student.query.get(student_id)
        if student:
            student.embeddings = True
            db.session.commit()
            print(f"STATUS UPDATE: Student {student.cui} embeddings set to True.")
            return True
        return False
    except Exception as e:
        db.session.rollback()
        print(f"Error updating embedding status: {e}")
        return False

# ==========================================================
# Función interna: envía N imágenes al endpoint de embeddings
# ==========================================================
def _send_to_embedding_service(files_payload, student_id):
    recognition_service_url = "http://localhost:4000/generate-embedding"
    data = {'student_id': student_id}

    try:
        # Enviar todas las imágenes en un solo request
        response = requests.post(recognition_service_url, files=files_payload, data=data)
        if response.status_code == 200:
            res = update_student_embedding_status(student_id)
            if res: return True
            else:
                print("Failed to update student embedding status in DB.")
                return False
        else:
            print(f"Recognition service error: {response.status_code} - {response.text}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"Connection to recognition service failed: {e}")
        return False

# ==========================================================
# Función pública: llama al servicio con request.files
# ==========================================================
def call_embedding_service(request_files, student_id):
    """
    request_files: lista de werkzeug.FileStorage (request.files.getlist('images'))
    """
    # Enviar todas las imágenes juntas bajo el mismo campo 'images'
    files_to_upload = [('images', (img.filename, img.stream, img.mimetype)) for img in request_files]
    return _send_to_embedding_service(files_to_upload, student_id)

# ==========================================================
# Función pública: procesa imágenes locales
# ==========================================================
def process_local_images(image_paths, student_id):
    """
    image_paths: lista de rutas locales a imágenes
    """
    files_to_upload = []
    opened_files = []

    try:
        for path in image_paths:
            f = open(path, 'rb')
            opened_files.append(f)
            ext = os.path.splitext(path)[1].lower()
            mime = 'image/jpeg' if ext in ['.jpg', '.jpeg'] else 'image/png'
            files_to_upload.append(('images', (os.path.basename(path), f, mime)))

        # Enviar todas las imágenes juntas en un solo request
        return _send_to_embedding_service(files_to_upload, student_id)
    finally:
        for f in opened_files:
            f.close()

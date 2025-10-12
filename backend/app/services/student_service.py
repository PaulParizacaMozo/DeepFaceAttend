import requests
import os

def _send_to_embedding_service(files_payload, student_cui):
    recognition_service_url = "http://localhost:4000/process-images"
    data = {'student_id': student_cui}
    try:
        response = requests.post(recognition_service_url, files=files_payload, data=data)
        if response.status_code == 200:
            return response.json().get('filepath')
        else:
            print(f"Recognition service error: {response.status_code} - {response.text}")
            return None
    except requests.exceptions.RequestException as e:
        print(f"Connection to recognition service failed: {e}")
        return None

def call_embedding_service(request_files, student_cui):
    files_to_upload = [('images', (img.filename, img.stream, img.mimetype)) for img in request_files]
    return _send_to_embedding_service(files_to_upload, student_cui)

def process_local_images(image_paths, student_cui):
    files_to_upload = []
    opened_files = [] 
    try:
        for path in image_paths:
            f = open(path, 'rb')
            opened_files.append(f)
            files_to_upload.append(('images', (os.path.basename(path), f, 'image/jpeg')))
        return _send_to_embedding_service(files_to_upload, student_cui)
    finally:
        for f in opened_files:
            f.close()
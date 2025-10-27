import requests

# ==========================================================
# Función interna: envía los datos al microservicio remoto
# ==========================================================
def _send_to_course_service(student_id, course_id):
    course_service_url = "http://localhost:4000/assign-to-course"
    payload = {
        "student_id": student_id,
        "course_id": course_id
    }

    try:
        response = requests.post(course_service_url, json=payload)
        if response.status_code == 200:
            return True
        else:
            print(f"Course service error: {response.status_code} - {response.text}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"Connection to course service failed: {e}")
        return False

# ==========================================================
# Función pública: llamada desde el endpoint Flask
# ==========================================================
def assign_to_course(student_id, course_id):
    result = _send_to_course_service(student_id, course_id)
    return result

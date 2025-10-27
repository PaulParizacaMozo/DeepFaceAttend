#!/bin/bash

# Script para probar los endpoints de la API de Asistencia.

echo "=================================================="
echo "Probando Endpoints de Estudiantes"
echo "=================================================="

echo -e "\n--- GET /students/ ---"
# Obtiene todos los estudiantes
curl -X GET "http://localhost:5000/students/" | jq

echo -e "\n--- POST /students/ ---"
# Crea un nuevo estudiante
curl -X POST http://localhost:5000/students/ \
-F "cui=20250001" \
-F "first_name=Shinji" \
-F "last_name=Ikari" \
-F "images=@../datasets/epcc_photos/braulio_pics/braulio_front.png" \
-F "images=@../datasets/epcc_photos/braulio_pics/braulio_right.png"

# curl -X POST "http://localhost:5000/students/" \
# -H "Content-Type: application/json" \
# -d '{
#     "cui": "20259999",
#     "first_name": "Juan",
#     "last_name": "Perez",
#     "filepath_embeddings": "embeddings/20259999.npy"
# }' | jq

echo -e "\n--- PUT /students/{student_id} ---"
# Actualiza un estudiante existente (reemplaza {student_id} con un ID real)
curl -X PUT http://localhost:5000/students/8fb5852c-14bc-4510-adfd-e3982dd33a24 \
-F "last_name=Ikari-Katsuragi" \
-F "images=@../datasets/epcc_photos/braulio_pics/braulio_left.png" 

# curl -X PUT "http://localhost:5000/students/ca9379b9-ea84-4bd5-8c51-ed8b80c3be5c" \
# -H "Content-Type: application/json" \
# -d '{
#     "filepath_embeddings": "embeddings/20259999.npy"
# }' | jq

echo -e "\n\n=================================================="
echo "Probando Endpoints de Cursos"
echo "=================================================="

echo -e "\n--- GET /courses/ ---"
# Obtiene todos los cursos
curl -X GET "http://localhost:5000/courses/" | jq

echo -e "\n--- POST /courses/ ---"
# Crea un nuevo curso
curl -X POST "http://localhost:5000/courses/" \
-H "Content-Type: application/json" \
-d '{
    "course_code": "1709999",
    "course_name": "IA Generativa",
    "semester": "10"
}' | jq

echo -e "\n\n=================================================="
echo "Probando Endpoints de Matrículas"
echo "=================================================="

echo -e "\n--- POST /enrollments/ ---"
# Matricula un estudiante en un curso
curl -X POST "http://localhost:5000/enrollments/" \
-H "Content-Type: application/json" \
-d '{
    "student_id": "ca9379b9-ea84-4bd5-8c51-ed8b80c3be5c",
    "course_id": "9377f155-f5de-4388-a344-f2aadbdd7562"
}' | jq

echo -e "\n--- GET /enrollments/ ---"
# Obtiene todas las matrículas
curl -X GET "http://localhost:5000/enrollments/" | jq

echo -e "\n\n=================================================="
echo "Probando Endpoints de Asistencia"
echo "=================================================="

echo -e "\n--- POST /attendance/ ---"
# Registra una nueva asistencia
curl -X POST "http://localhost:5000/attendance/" \
-H "Content-Type: application/json" \
-d '{
    "student_id": "ca9379b9-ea84-4bd5-8c51-ed8b80c3be5c",
    "course_id": "9377f155-f5de-4388-a344-f2aadbdd7562",
    "attendance_date": "2025-10-10",
    "status": "presente"
}' | jq


echo -e "\n--- POST /attendance/search ---"

# Obtiene la asistencia para un curso específico 
curl -X POST "http://localhost:5000/attendance/search" \
-H "Content-Type: application/json" \
-d '{
    "course_id": "c8729434-f8af-4703-846c-474942d3b4c1"
}' | jq


echo -e "\n--- POST /attendance/search ---"
# Obtiene la asistencia para una fecha específica
curl -X POST "http://localhost:5000/attendance/search" \
-H "Content-Type: application/json" \
-d '{
    "date": "2025-09-02"
}' | jq

echo -e "\n--- GET /attendance?course_id=...&date=... ---"
# Obtiene la asistencia para un curso y fecha específicos
curl -X POST "http://localhost:5000/attendance/search" \
-H "Content-Type: application/json" \
-d '{
    "course_id": "c8729434-f8af-4703-846c-474942d3b4c1",
    "date": "2025-09-03"
}' | jq

echo -e "\n\nPruebas finalizadas."

#!/bin/bash
# Script para insertar estudiantes de ejemplo en la base de datos

echo "Creando estudiante: Braulio Gomez"
curl -X POST http://127.0.0.1:5000/students \
     -H "Content-Type: application/json" \
     -d '{"cui":"20250001","first_name":"Braulio","last_name":"Gomez","filepath_embeddings":"embeddings/braulio.npy"}'

echo "\n\nCreando estudiante: Nelzon Quispe"
curl -X POST http://127.0.0.1:5000/students \
     -H "Content-Type: application/json" \
     -d '{"cui":"20250002","first_name":"Nelzon","last_name":"Quispe","filepath_embeddings":"embeddings/nelzon.npy"}'

echo "\n\nCreando estudiante: Kevin Flores"
curl -X POST http://127.0.0.1:5000/students \
     -H "Content-Type: application/json" \
     -d '{"cui":"20250003","first_name":"Kevin","last_name":"Flores","filepath_embeddings":"embeddings/kevin.npy"}'

echo "\n\nCreando estudiante: Luciana Mamani"
curl -X POST http://127.0.0.1:5000/students \
     -H "Content-Type: application/json" \
     -d '{"cui":"20250004","first_name":"Luciana","last_name":"Mamani","filepath_embeddings":"embeddings/luciana.npy"}'

echo "\n\nCreando estudiante: Sergio Choque"
curl -X POST http://127.0.0.1:5000/students \
     -H "Content-Type: application/json" \
     -d '{"cui":"20250005","first_name":"Sergio","last_name":"Choque","filepath_embeddings":"embeddings/sergio.npy"}'

echo "\n\nProceso completado."
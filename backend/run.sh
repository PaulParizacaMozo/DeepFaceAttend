# Inicializar la base de datos
flask --app app.py init-db

# Ejecutar app
flask --app app.py run


# Pruebas
## Crear un estudiante
curl -X POST http://127.0.0.1:5000/students \
     -H "Content-Type: application/json" \
     -d '{"cui":"20250001","first_name":"Braulio","last_name":"Gomez","filepath_embeddings":"embeddings/braulio.npy"}'

## Listar estudiantes
curl http://127.0.0.1:5000/students

## Obtener estudiante por UUID
curl http://127.0.0.1:5000/students/<uuid>


## Actualizar estudiante
curl -X PUT http://127.0.0.1:5000/students/<uuid> \
     -H "Content-Type: application/json" \
     -d '{"last_name":"Perez"}'

## Eliminar estudiante
curl -X DELETE http://127.0.0.1:5000/students/<uuid>

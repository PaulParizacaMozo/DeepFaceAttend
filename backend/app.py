from flask import Flask, request, jsonify
from flask_marshmallow import Marshmallow
from models import db, Student
import os

app = Flask(__name__)

# Configuracion de SQLite
base_dir = os.path.abspath(os.path.dirname(__file__))
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///" + os.path.join(base_dir, "database.db")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# Inicializar extensiones
db.init_app(app)
ma = Marshmallow(app)

# Esquema para serializacion
class StudentSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Student
        load_instance = True

student_schema = StudentSchema()
students_schema = StudentSchema(many=True)

# ==========================
# Rutas
# ==========================

@app.route("/students", methods=["POST"])
def add_student():
    """
    Crea un nuevo estudiante
    """
    data = request.get_json()

    new_student = Student(
        cui=data["cui"],
        first_name=data["first_name"],
        last_name=data["last_name"],
        filepath_embeddings=data["filepath_embeddings"]
    )
    db.session.add(new_student)
    db.session.commit()

    return student_schema.jsonify(new_student), 201


@app.route("/students", methods=["GET"])
def get_students():
    """
    Obtiene todos los estudiantes
    """
    students = Student.query.all()
    return students_schema.jsonify(students), 200


@app.route("/students/<string:student_id>", methods=["GET"])
def get_student(student_id):
    """
    Obtiene un estudiante por su UUID
    """
    student = Student.query.get_or_404(student_id)
    return student_schema.jsonify(student), 200


@app.route("/students/<string:student_id>", methods=["PUT"])
def update_student(student_id):
    """
    Actualiza datos de un estudiante
    """
    student = Student.query.get_or_404(student_id)
    data = request.get_json()

    student.cui = data.get("cui", student.cui)
    student.first_name = data.get("first_name", student.first_name)
    student.last_name = data.get("last_name", student.last_name)
    student.filepath_embeddings = data.get("filepath_embeddings", student.filepath_embeddings)

    db.session.commit()
    return student_schema.jsonify(student), 200


@app.route("/students/<string:student_id>", methods=["DELETE"])
def delete_student(student_id):
    """
    Elimina un estudiante
    """
    student = Student.query.get_or_404(student_id)
    db.session.delete(student)
    db.session.commit()
    return jsonify({"message": "Student deleted"}), 200


# ==========================
# Inicializacion de la BD
# ==========================
@app.cli.command("init-db")
def init_db():
    db.create_all()
    print("Database initialized successfully.")


# ==========================
# Ejecutar app
# ==========================
if __name__ == "__main__":
    app.run(debug=True)

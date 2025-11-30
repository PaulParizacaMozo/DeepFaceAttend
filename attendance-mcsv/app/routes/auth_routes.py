# app/routes/auth_routes.py
import datetime
from flask import Blueprint, request, jsonify, current_app
import jwt
from app import db # Importa db
from app.models.user import User, UserRole 
from app.models.student import Student 
from app.models.teacher import Teacher 
from functools import wraps
from app.schemas.course_schema import courses_schema

auth_bp = Blueprint('auth_bp', __name__, url_prefix='/auth')

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        # Espera un header en formato "Bearer <token>"
        if 'Authorization' in request.headers:
            try:
                token = request.headers['Authorization'].split(" ")[1]
            except IndexError:
                return jsonify({'message': 'Formato de token inválido'}), 401
        
        if not token:
            return jsonify({'message': 'Falta el token de autorización'}), 401

        try:
            # Decodifica el token para obtener los datos (payload)
            data = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=['HS256'])
            # Busca al usuario en la BD usando el 'id' del token
            current_user = User.query.get(data['sub'])
            if not current_user:
                return jsonify({'message': 'Usuario no encontrado'}), 401
        except jwt.ExpiredSignatureError:
            return jsonify({'message': 'El token ha expirado'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'message': 'Token inválido'}), 401
        
        # Pasa el objeto de usuario a la ruta
        return f(current_user, *args, **kwargs)
    return decorated

@auth_bp.route('/profile', methods=['GET'])
@token_required 
def get_profile(current_user):    
    if current_user.role == UserRole.STUDENT and current_user.student:
        profile_data = {
            "id": current_user.id,
            "email": current_user.email,
            "role": current_user.role.value,
            "first_name": current_user.student.first_name,
            "last_name": current_user.student.last_name,
            "cui": current_user.student.cui
        }
    elif current_user.role == UserRole.TEACHER and current_user.teacher:
        profile_data = {
            "id": current_user.id,
            "email": current_user.email,
            "role": current_user.role.value,
            "first_name": current_user.teacher.first_name,
            "last_name": current_user.teacher.last_name,
        }
    else:
        # Este caso podría ocurrir si hay inconsistencia en los datos
        return jsonify({"message": "Perfil de usuario no encontrado"}), 404
        
    return jsonify(profile_data), 200

@auth_bp.route('/profile/courses', methods=['GET'])
@token_required # Protegemos la ruta y obtenemos el usuario actual
def get_my_courses(current_user):
    """
    Devuelve los cursos asociados al usuario autenticado.
    - Si es Estudiante, devuelve los cursos en los que está matriculado.
    - Si es Profesor, devuelve los cursos que tiene asignados.
    """
    courses = []
    
    # Lógica para Estudiantes
    if current_user.role == UserRole.STUDENT:
        # A través de la relación User -> Student -> Enrollments -> Course
        if current_user.student and current_user.student.enrollments:
            courses = [enrollment.course for enrollment in current_user.student.enrollments]

    # Lógica para Profesores
    elif current_user.role == UserRole.TEACHER:
        # A través de la relación User -> Teacher -> Courses
        if current_user.teacher:
            courses = current_user.teacher.courses
    
    return courses_schema.jsonify(courses), 200

@auth_bp.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')
    role = data.get('role')
    first_name = data.get('first_name')
    last_name = data.get('last_name')

    if not all([email, password, role, first_name, last_name]):
        return jsonify({"message": "Faltan datos requeridos"}), 400

    if User.query.filter_by(email=email).first():
        return jsonify({"message": "El correo electrónico ya está en uso"}), 409

    try:
        user_role = UserRole(role)
    except ValueError:
        return jsonify({"message": "Rol inválido. Debe ser 'student' o 'teacher'"}), 400

    # --- Creación del nuevo usuario ---
    new_user = User(email=email, role=user_role)
    new_user.set_password(password)
    
    # Inicia una transacción
    try:
        db.session.add(new_user)

        # --- Lógica específica por rol ---
        if user_role == UserRole.STUDENT:
            cui = data.get('cui')
            if not cui:
                db.session.rollback()
                return jsonify({"message": "El CUI es requerido para estudiantes"}), 400
            
            if Student.query.filter_by(cui=cui).first():
                db.session.rollback()
                return jsonify({"message": "El CUI ya está registrado"}), 409

            # Crea el perfil del estudiante y lo asocia al usuario
            new_student = Student(
                cui=cui,
                first_name=first_name,
                last_name=last_name,
                user=new_user  # ¡Aquí ocurre la magia de la asociación!
            )
            db.session.add(new_student)

        elif user_role == UserRole.TEACHER:
            # Crea el perfil del profesor y lo asocia al usuario
            new_teacher = Teacher(
                first_name=first_name,
                last_name=last_name,
                user=new_user # Asociación
            )
            db.session.add(new_teacher)

        # Confirma todos los cambios en la base de datos
        db.session.commit()
    
    except Exception as e:
        db.session.rollback() # Si algo falla, revierte todo
        return jsonify({"message": "Error al crear el usuario", "error": str(e)}), 500


    return jsonify({"message": f"Usuario '{role}' registrado exitosamente"}), 201

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')
    user = User.query.filter_by(email=email).first()

    if not user or not user.check_password(password):
        return jsonify({"message": "Credenciales inválidas"}), 401
    
    token_payload = {
        'sub': user.id,            
        'role': user.role.value,
        'iat': datetime.datetime.utcnow(),
        'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=24)
    }
    
    token = jwt.encode(
        token_payload,
        current_app.config['SECRET_KEY'],
        algorithm='HS256'
    )

    return jsonify({"message": "Login exitoso", "token": token}), 200
    
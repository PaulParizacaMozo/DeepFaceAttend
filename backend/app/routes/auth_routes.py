# app/routes/auth_routes.py
import datetime
from flask import Blueprint, request, jsonify, current_app
import jwt
from app import db # Importa db
from app.models.user import User, UserRole 
from app.models.student import Student 
from app.models.teacher import Teacher 

auth_bp = Blueprint('auth_bp', __name__, url_prefix='/auth')

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
    
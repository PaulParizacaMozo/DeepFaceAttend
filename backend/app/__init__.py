from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from flask_cors import CORS
from config import Config

# Inicializar extensiones globalmente pero sin una aplicación específica
db = SQLAlchemy()
ma = Marshmallow()

def create_app(config_class=Config):
    """Fábrica para crear y configurar la instancia de la aplicación Flask."""
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Inicializar las extensiones con la aplicación
    db.init_app(app)
    ma.init_app(app)
    CORS(app, resources={r"/*": {"origins": "*"}})

    # Importar y registrar los Blueprints (grupos de rutas)
    from app.routes.student_routes import students_bp
    from app.routes.course_routes import courses_bp
    from app.routes.schedule_routes import schedules_bp
    from app.routes.enrollment_routes import enrollments_bp
    from app.routes.attendance_routes import attendance_bp

    app.register_blueprint(students_bp)
    app.register_blueprint(courses_bp)
    app.register_blueprint(schedules_bp)
    app.register_blueprint(enrollments_bp)
    app.register_blueprint(attendance_bp)

    # Registrar comandos CLI personalizados
    register_commands(app)

    return app

def register_commands(app):
    """Registra comandos CLI como 'flask init-db'."""
    @app.cli.command("init-db")
    def init_db():
        """Inicializa la base de datos creando todas las tablas."""
        # Importar todos los modelos aquí para que SQLAlchemy los detecte
        from app.models import student, course, schedule, enrollment, attendance
        db.create_all()
        print("Database initialized and all tables created successfully.")

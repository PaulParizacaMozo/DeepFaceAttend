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

    @app.cli.command("drop-db")
    def drop_db():
        """Elimina todas las tablas de la base de datos."""
        db.drop_all()
        print("All tables dropped successfully.")
        
    @app.cli.command("insert-db")
    def insert_db():
        """Inserta datos de ejemplo en la base de datos."""
        # Importar modelos dentro de la función para evitar dependencias circulares
        from app.models.student import Student
        from app.models.course import Course
        from app.models.schedule import Schedule
        from app.models.enrollment import Enrollment
        from app.models.attendance import Attendance
        from datetime import time, date, datetime

        # Limpiar tablas existentes en el orden correcto para evitar errores de FK
        db.session.query(Attendance).delete()
        db.session.query(Enrollment).delete()
        db.session.query(Schedule).delete()
        db.session.query(Course).delete()
        db.session.query(Student).delete()
        db.session.commit()
        print("Existing data cleared.")

        try:
            # 1. Crear Estudiantes
            students_to_add = [
                Student(cui='20210001', first_name='Luciana Julissa', last_name='Huaman Coaquira', filepath_embeddings='embeddings/20210001.npy'),
                Student(cui='20210002', first_name='Nelzon Jorge', last_name='Apaza Apaza', filepath_embeddings='embeddings/20210002.npy'),
                Student(cui='20210003', first_name='Kevin Joaquin', last_name='Chambi Tapia', filepath_embeddings='embeddings/20210003.npy'),
                Student(cui='20210004', first_name='Braulio Nayap', last_name='Maldonado Casilla', filepath_embeddings='embeddings/20210004.npy')
            ]
            db.session.add_all(students_to_add)
            db.session.commit()
            print(f"{len(students_to_add)} students created.")

            # 2. Crear Cursos (guardamos la referencia a Cloud Computing)
            course_cloud = Course(course_name='Cloud Computing', course_code='1705265', semester='10')
            courses_to_add = [
                Course(course_name='Trabajo Interdisciplinar 3', course_code='1705267', semester='10'),
                course_cloud,
                Course(course_name='Internet de las Cosas', course_code='1705268', semester='10'),
                Course(course_name='Robotica (E)', course_code='1705269', semester='10'),
                Course(course_name='Topicos en Ciberserguridad (E)', course_code='1705270', semester='10')
            ]
            db.session.add_all(courses_to_add)
            db.session.commit()
            print(f"{len(courses_to_add)} courses created.")

            # 3. Crear Horarios (para Cloud Computing)
            schedules_to_add = [
                Schedule(course_id=course_cloud.id, day_of_week=2, start_time=time(12, 20), end_time=time(14, 0), location='Aula 301'),
                Schedule(course_id=course_cloud.id, day_of_week=3, start_time=time(12, 20), end_time=time(14, 0), location='Aula 301'),
                Schedule(course_id=course_cloud.id, day_of_week=4, start_time=time(12, 20), end_time=time(14, 0), location='Laboratorio 2')
            ]
            db.session.add_all(schedules_to_add)
            db.session.commit()
            print(f"{len(schedules_to_add)} schedules for Cloud Computing created.")

            # 4. Matricular estudiantes en Cloud Computing
            enrollments_to_add = [Enrollment(student_id=s.id, course_id=course_cloud.id) for s in students_to_add]
            db.session.add_all(enrollments_to_add)
            db.session.commit()
            print(f"{len(enrollments_to_add)} students enrolled in Cloud Computing.")

            # 5. Registrar Asistencia
            attendance_records = [
                # 2 de Sep, 2025
                Attendance(student_id=students_to_add[0].id, course_id=course_cloud.id, attendance_date=date(2025, 9, 2), status='presente', check_in_time=datetime(2025, 9, 2, 12, 21)),
                Attendance(student_id=students_to_add[1].id, course_id=course_cloud.id, attendance_date=date(2025, 9, 2), status='presente', check_in_time=datetime(2025, 9, 2, 12, 22)),
                Attendance(student_id=students_to_add[2].id, course_id=course_cloud.id, attendance_date=date(2025, 9, 2), status='presente', check_in_time=datetime(2025, 9, 2, 12, 23)),
                Attendance(student_id=students_to_add[3].id, course_id=course_cloud.id, attendance_date=date(2025, 9, 2), status='presente', check_in_time=datetime(2025, 9, 2, 12, 24)),
                # 3 de Sep, 2025
                Attendance(student_id=students_to_add[0].id, course_id=course_cloud.id, attendance_date=date(2025, 9, 3), status='presente', check_in_time=datetime(2025, 9, 3, 12, 25)),
                Attendance(student_id=students_to_add[1].id, course_id=course_cloud.id, attendance_date=date(2025, 9, 3), status='tarde', check_in_time=datetime(2025, 9, 3, 12, 40)),
                Attendance(student_id=students_to_add[2].id, course_id=course_cloud.id, attendance_date=date(2025, 9, 3), status='ausente', check_in_time=datetime(2025, 9, 3, 14, 1)),
            ]
            db.session.add_all(attendance_records)
            db.session.commit()
            print(f"{len(attendance_records)} attendance records created.")

            print("\nSample data inserted successfully!")

        except Exception as e:
            db.session.rollback()
            print(f"An error occurred: {e}")

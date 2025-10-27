# app/__init__.py
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
    CORS(app, 
         resources={r"/*": {"origins": "*"}}, 
         supports_credentials=True,
         allow_headers=["Authorization", "Content-Type"])

    # Importar y registrar los Blueprints (grupos de rutas)
    from app.routes.student_routes import students_bp
    from app.routes.course_routes import courses_bp
    from app.routes.schedule_routes import schedules_bp
    from app.routes.enrollment_routes import enrollments_bp
    from app.routes.attendance_routes import attendance_bp
    from app.routes.auth_routes import auth_bp

    app.register_blueprint(students_bp)
    app.register_blueprint(courses_bp)
    app.register_blueprint(schedules_bp)
    app.register_blueprint(enrollments_bp)
    app.register_blueprint(attendance_bp)
    app.register_blueprint(auth_bp)

    # Registrar comandos CLI personalizados
    register_commands(app)

    return app

def register_commands(app):
    """Registra comandos CLI como 'flask init-db'."""
    @app.cli.command("init-db")
    def init_db():
        # ... (código sin cambios)
        from app.models import user, student, course, schedule, enrollment, attendance, teacher
        db.create_all()
        print("Database initialized and all tables created successfully.")

    @app.cli.command("drop-db")
    def drop_db():
        # ... (código sin cambios)
        db.drop_all()
        print("All tables dropped successfully.")
        
    @app.cli.command("insert-db")
    def insert_db():
        """Inserta datos de ejemplo en la base de datos."""
        from app.models.user import User, UserRole
        from app.models.teacher import Teacher
        from app.models.student import Student
        from app.models.course import Course
        from app.models.schedule import Schedule
        from app.models.enrollment import Enrollment
        from app.models.attendance import Attendance
        from datetime import time, date, datetime
        from app.services.student_service import process_local_images
        from app.services.enrollment_service import assign_to_course
        import os

        # Orden de limpieza actualizado
        db.session.query(Attendance).delete()
        db.session.query(Enrollment).delete()
        db.session.query(Schedule).delete()
        db.session.query(Course).delete()
        db.session.query(Student).delete()
        db.session.query(Teacher).delete()
        db.session.query(User).delete()
        db.session.commit()
        print("Existing data cleared.")
        
        project_root = os.path.dirname(os.path.abspath(app.root_path))
        dataset_base_path = os.path.join(project_root, '../datasets/epcc_photos')
        
        students_data = [
            { 'cui': '20210001', 'first_name': 'Luciana Julissa', 'last_name': 'Huaman Coaquira', 'email': 'lhuaman@unsa.edu.pe', 'image_folder': os.path.join(dataset_base_path, 'luciana_pics') },
            { 'cui': '20210002', 'first_name': 'Nelzon Jorge', 'last_name': 'Apaza Apaza', 'email': 'napaza@unsa.edu.pe', 'image_folder': os.path.join(dataset_base_path, 'nelzon_pics') },
            { 'cui': '20210003', 'first_name': 'Kevin Joaquin', 'last_name': 'Chambi Tapia', 'email': 'kchambi@unsa.edu.pe', 'image_folder': os.path.join(dataset_base_path, 'kevin_pics') },
            { 'cui': '20210004', 'first_name': 'Braulio Nayap', 'last_name': 'Maldonado Casilla', 'email': 'bmaldonado@unsa.edu.pe', 'image_folder': os.path.join(dataset_base_path, 'braulio_pics') },
            { 'cui': '20210005', 'first_name': 'Paul Antony', 'last_name': 'Parizaca Mozo', 'email': 'pparizaca@unsa.edu.pe', 'image_folder': os.path.join(dataset_base_path, 'paul_pics') }
        ]
        
        students_to_add = []
        try:
            # 1. Crear Usuarios y Perfiles (Estudiantes y Profesores)
            print("Creating users and profiles...")
            
            # Crear Estudiantes con sus cuentas de Usuario
            for s_data in students_data:
                user_student = User(email=s_data['email'], role=UserRole.STUDENT)
                user_student.set_password('123456')
                new_student = Student(cui=s_data['cui'], first_name=s_data['first_name'], last_name=s_data['last_name'], user=user_student)
                db.session.add(user_student)
                db.session.add(new_student)
                students_to_add.append(new_student)
            
            # Crear Profesor Alvaro Mamani con su cuenta de Usuario
            user_teacher = User(email='amamani@unsa.edu.pe', role=UserRole.TEACHER)
            user_teacher.set_password('123456')
            teacher_alvaro = Teacher(first_name='Alvaro Henry', last_name='Mamani Aliaga', user=user_teacher)
            db.session.add(user_teacher)
            db.session.add(teacher_alvaro)
            
            db.session.commit()
            print(f"{len(students_to_add)} student users and 1 teacher user (Alvaro Henry Mamani Aliaga) created.")

            # 2. Procesar imágenes de cada estudiante
            for student in students_to_add:
                s_data = next((d for d in students_data if d['cui'] == student.cui), None)
                if not s_data: continue
                image_folder = s_data['image_folder']
                if not os.path.isdir(image_folder):
                    print(f"WARNING: Folder not found for {student.id}: {image_folder}")
                    continue
                image_paths = [os.path.join(image_folder, f) for f in os.listdir(image_folder) if f.lower().endswith(('.jpg', '.jpeg', '.png'))]
                if image_paths:
                    success = process_local_images(image_paths, student.id)
                    if success: print(f"Embeddings processed for {student.id}")
                    else: print(f"Failed to process embeddings for {student.id}")
                else:
                    print(f"WARNING: No images found in {image_folder} for {student.id}")

            # 3. Crear Cursos y asignarlo al profesor
            course_cloud = Course(course_name='Cloud Computing', course_code='1705265', semester='10', teacher_id=teacher_alvaro.id)
            courses_to_add = [
                course_cloud,
                Course(course_name='Trabajo Interdisciplinar 3', course_code='1705267', semester='10'),
                Course(course_name='Internet de las Cosas', course_code='1705268', semester='10'),
                Course(course_name='Robotica (E)', course_code='1705269', semester='10'),
                Course(course_name='Topicos en Ciberserguridad (E)', course_code='1705270', semester='10')
            ]
            db.session.add_all(courses_to_add)
            db.session.commit()
            print(f"{len(courses_to_add)} courses created. Cloud Computing assigned to {teacher_alvaro.first_name}.")

            # 4. Crear Horarios (para Cloud Computing)
            schedules_to_add = [
                Schedule(course_id=course_cloud.id, day_of_week=2, start_time=time(12, 20), end_time=time(14, 0), location='Aula 301'),
                Schedule(course_id=course_cloud.id, day_of_week=3, start_time=time(12, 20), end_time=time(14, 0), location='Aula 301'),
                Schedule(course_id=course_cloud.id, day_of_week=1, start_time=time(12, 20), end_time=time(14, 0), location='Laboratorio 2')
            ]
            db.session.add_all(schedules_to_add)
            db.session.commit()
            print(f"{len(schedules_to_add)} schedules for Cloud Computing created.")

            # 5.A Matricular estudiantes en Cloud Computing
            enrollments_to_add = []
            for s in students_to_add:
                success = assign_to_course(s.id, course_cloud.id)
                if success:
                    enrollment = Enrollment(student_id=s.id, course_id=course_cloud.id)
                    enrollments_to_add.append(enrollment)
                    db.session.add(enrollment)
                    print(f"Embedding for student {s.id} assigned successfully — ready to enroll.")
                else:
                    print(f"Skipping enrollment for student {s.id}: embedding assignment failed.")
            if enrollments_to_add:
                db.session.commit()
                print(f"{len(enrollments_to_add)} students enrolled in Cloud Computing (local DB).")
            else:
                print("No enrollments were added — all embedding assignments failed.")
            
            # 5.B Matricular estudiantes en Trabajo Interdisciplinar 3
            course_ti3 = Course.query.filter_by(course_code='1705267').first()
            enrollments_ti3 = []
            for s in students_to_add:
                success = assign_to_course(s.id, course_ti3.id)
                if success:
                    enrollment = Enrollment(student_id=s.id, course_id=course_ti3.id)
                    enrollments_ti3.append(enrollment)
                    db.session.add(enrollment)
                    print(f"Embedding for student {s.id} assigned successfully — ready to enroll in TI3.")
                else:
                    print(f"Skipping enrollment for student {s.id} in TI3: embedding assignment failed.")
            if enrollments_ti3:
                db.session.commit()
                print(f"{len(enrollments_ti3)} students enrolled in Trabajo Interdisciplinar 3 (local DB).")
            else:
                print("No enrollments were added for TI3 — all embedding assignments failed.")

            # 6.A Registrar Asistencia en Cloud Computing
            attendance_records = [
                # 2 de Sep, 2025
                Attendance(student_id=students_to_add[0].id, course_id=course_cloud.id, attendance_date=date(2025, 9, 2), status='presente', check_in_time=datetime(2025, 9, 2, 12, 21)),
                Attendance(student_id=students_to_add[1].id, course_id=course_cloud.id, attendance_date=date(2025, 9, 2), status='presente', check_in_time=datetime(2025, 9, 2, 12, 22)),
                Attendance(student_id=students_to_add[2].id, course_id=course_cloud.id, attendance_date=date(2025, 9, 2), status='presente', check_in_time=datetime(2025, 9, 2, 12, 23)),
                Attendance(student_id=students_to_add[3].id, course_id=course_cloud.id, attendance_date=date(2025, 9, 2), status='presente', check_in_time=datetime(2025, 9, 2, 12, 24)),
                Attendance(student_id=students_to_add[4].id, course_id=course_cloud.id, attendance_date=date(2025, 9, 2), status='presente', check_in_time=datetime(2025, 9, 2, 12, 24)),
                # 3 de Sep, 2025
                Attendance(student_id=students_to_add[0].id, course_id=course_cloud.id, attendance_date=date(2025, 9, 3), status='presente', check_in_time=datetime(2025, 9, 3, 12, 25)),
                Attendance(student_id=students_to_add[1].id, course_id=course_cloud.id, attendance_date=date(2025, 9, 3), status='ausente', check_in_time=datetime(2025, 9, 3, 12, 40)),
                Attendance(student_id=students_to_add[2].id, course_id=course_cloud.id, attendance_date=date(2025, 9, 3), status='ausente', check_in_time=datetime(2025, 9, 3, 14, 1)),
                Attendance(student_id=students_to_add[3].id, course_id=course_cloud.id, attendance_date=date(2025, 9, 3), status='presente', check_in_time=datetime(2025, 9, 3, 12, 27)),
                Attendance(student_id=students_to_add[4].id, course_id=course_cloud.id, attendance_date=date(2025, 9, 3), status='presente', check_in_time=datetime(2025, 9, 3, 12, 27)),
            ]
            db.session.add_all(attendance_records)
            db.session.commit()
            print(f"{len(attendance_records)} attendance records created.")

            # 6.B Registrar Asistencia en Trabajo Interdisciplinar 3
            course_ti3 = Course.query.filter_by(course_code='1705267').first()
            attendance_ti3_records = [
                # 8 de Sep, 2025 (sin cambios, ya estaba bien)
                Attendance(student_id=students_to_add[0].id, course_id=course_ti3.id, attendance_date=date(2025, 9, 8), status='presente', check_in_time=datetime(2025, 9, 8, 10, 5)),
                Attendance(student_id=students_to_add[1].id, course_id=course_ti3.id, attendance_date=date(2025, 9, 8), status='presente', check_in_time=datetime(2025, 9, 8, 10, 10)),
                Attendance(student_id=students_to_add[2].id, course_id=course_ti3.id, attendance_date=date(2025, 9, 8), status='ausente', check_in_time=datetime(2025, 9, 8, 10, 30)),
                Attendance(student_id=students_to_add[3].id, course_id=course_ti3.id, attendance_date=date(2025, 9, 8), status='presente', check_in_time=datetime(2025, 9, 8, 10, 15)),
                Attendance(student_id=students_to_add[4].id, course_id=course_ti3.id, attendance_date=date(2025, 9, 8), status='presente', check_in_time=datetime(2025, 9, 8, 10, 15)),
                
                # 15 de Sep, 2025 (minutos corregidos)
                Attendance(student_id=students_to_add[0].id, course_id=course_ti3.id, attendance_date=date(2025, 9, 15), status='presente', check_in_time=datetime(2025, 9, 15, 10, 7)),
                Attendance(student_id=students_to_add[1].id, course_id=course_ti3.id, attendance_date=date(2025, 9, 15), status='ausente', check_in_time=datetime(2025, 9, 15, 10, 12)),
                Attendance(student_id=students_to_add[2].id, course_id=course_ti3.id, attendance_date=date(2025, 9, 15), status='presente', check_in_time=datetime(2025, 9, 15, 10, 15)),
                Attendance(student_id=students_to_add[3].id, course_id=course_ti3.id, attendance_date=date(2025, 9, 15), status='presente', check_in_time=datetime(2025, 9, 15, 10, 8)),
                Attendance(student_id=students_to_add[4].id, course_id=course_ti3.id, attendance_date=date(2025, 9, 15), status='presente', check_in_time=datetime(2025, 9, 15, 10, 8)),
                
                # 22 de Sep, 2025 (minutos corregidos)
                Attendance(student_id=students_to_add[0].id, course_id=course_ti3.id, attendance_date=date(2025, 9, 22), status='presente', check_in_time=datetime(2025, 9, 22, 10, 50)),
                Attendance(student_id=students_to_add[1].id, course_id=course_ti3.id, attendance_date=date(2025, 9, 22), status='presente', check_in_time=datetime(2025, 9, 22, 10, 55)),
                Attendance(student_id=students_to_add[2].id, course_id=course_ti3.id, attendance_date=date(2025, 9, 22), status='presente', check_in_time=datetime(2025, 9, 22, 10, 0)), # Era 60
                Attendance(student_id=students_to_add[3].id, course_id=course_ti3.id, attendance_date=date(2025, 9, 22), status='presente', check_in_time=datetime(2025, 9, 22, 10, 5)), # Era 65
                Attendance(student_id=students_to_add[4].id, course_id=course_ti3.id, attendance_date=date(2025, 9, 22), status='presente', check_in_time=datetime(2025, 9, 22, 10, 5)), # Era 65
                
                # 29 de Sep, 2025 (sin cambios, ya estaba bien)
                Attendance(student_id=students_to_add[0].id, course_id=course_ti3.id, attendance_date=date(2025, 9, 29), status='presente', check_in_time=datetime(2025, 9, 29, 10, 20)),
                Attendance(student_id=students_to_add[1].id, course_id=course_ti3.id, attendance_date=date(2025, 9, 29), status='presente', check_in_time=datetime(2025, 9, 29, 10, 25)),
                Attendance(student_id=students_to_add[2].id, course_id=course_ti3.id, attendance_date=date(2025, 9, 29), status='presente', check_in_time=datetime(2025, 9, 29, 10, 30)),
                Attendance(student_id=students_to_add[3].id, course_id=course_ti3.id, attendance_date=date(2025, 9, 29), status='presente', check_in_time=datetime(2025, 9, 29, 10, 35)),
                Attendance(student_id=students_to_add[4].id, course_id=course_ti3.id, attendance_date=date(2025, 9, 29), status='presente', check_in_time=datetime(2025, 9, 29, 10, 35)),
            ]
            db.session.add_all(attendance_ti3_records)
            db.session.commit()
            print(f"{len(attendance_ti3_records)} attendance records for TI3 created.")

            print("\nSample data inserted successfully!")

        except Exception as e:
            db.session.rollback()
            print(f"An error occurred: {e}")

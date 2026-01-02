# attendance-mcsv/app/__init__.py
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from flask_cors import CORS
from config import Config
import os

db = SQLAlchemy()
ma = Marshmallow()

def create_app(config_class=Config):
    """Fábrica para crear y configurar la instancia de la aplicación Flask."""
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    ma.init_app(app)

    CORS(app, 
         resources={r"/*": {"origins": "*"}}, 
         supports_credentials=True,
         allow_headers=["Authorization", "Content-Type"])
    
    # Iniciar el scheduler en el contexto de la app
    if not app.debug or os.getenv("WERKZEUG_RUN_MAIN") == "true":
        # Solo en producción o sin debugger 
        from app.scheduler import run_scheduler
        import threading
        scheduler_thread = threading.Thread(target=run_scheduler, args=(app,), daemon=True)
        scheduler_thread.start()
        app.logger.info("Background scheduler started.")

    # Importar y registrar los Blueprints (grupos de rutas)
    from app.routes.student_routes import students_bp
    from app.routes.course_routes import courses_bp
    from app.routes.schedule_routes import schedules_bp
    from app.routes.enrollment_routes import enrollments_bp
    from app.routes.attendance_routes import attendance_bp
    from app.routes.auth_routes import auth_bp
    from app.routes.unknown_face_routes import unknown_face_bp, captures_bp

    app.register_blueprint(students_bp)
    app.register_blueprint(courses_bp)
    app.register_blueprint(schedules_bp)
    app.register_blueprint(enrollments_bp)
    app.register_blueprint(attendance_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(unknown_face_bp)
    app.register_blueprint(captures_bp)

    # Registrar comandos CLI personalizados
    register_commands(app)

    return app

def register_commands(app):
    """Registra comandos CLI como 'flask init-db'."""
    @app.cli.command("init-db")
    def init_db():
        from app.models import user, student, course, schedule, enrollment, attendance, teacher
        db.create_all()
        print("Database initialized and all tables created successfully.")

    @app.cli.command("drop-db")
    def drop_db():
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
            { 'cui': '20210005', 'first_name': 'Paul Antony', 'last_name': 'Parizaca Mozo', 'email': 'pparizaca@unsa.edu.pe', 'image_folder': os.path.join(dataset_base_path, 'paul_pics') },
            { 'cui': '20210006', 'first_name': 'Sergio Daniel', 'last_name': 'Mogollon Caceres', 'email': 'smogollon@unsa.edu.pe', 'image_folder': os.path.join(dataset_base_path, 'sergio_pics') },
            { 'cui': '20210007', 'first_name': 'Leon Felipe', 'last_name': 'Davis Coropuna', 'email': 'ldavis@unsa.edu.pe', 'image_folder': os.path.join(dataset_base_path, 'leon_pics') },
            { 'cui': '20210008', 'first_name': 'Avelino', 'last_name': 'Lupo Condori', 'email': 'alupo@unsa.edu.pe', 'image_folder': os.path.join(dataset_base_path, 'avelino_pics') },
            { 'cui': '20210009', 'first_name': 'Victor Alejandro', 'last_name': 'Quicaño Miranda', 'email': 'vquicano@unsa.edu.pe', 'image_folder': os.path.join(dataset_base_path, 'alejandro_pics') }
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
            
            # Crear Profesora Yessenia Yari con su cuenta de Usuario
            user_teacher_yessenia = User(email='yyari@unsa.edu.pe', role=UserRole.TEACHER)
            user_teacher_yessenia.set_password('123456')
            teacher_yessenia = Teacher(first_name='Yessenia Deysi', last_name='Yari Ramos', user=user_teacher_yessenia)
            db.session.add(user_teacher_yessenia)
            db.session.add(teacher_yessenia)

            db.session.commit()
            print(f"{len(students_to_add)} students and 2 teachers created.")

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
            course_ti3 = Course(course_name='Trabajo Interdisciplinar 3', course_code='1705267', semester='10', teacher_id=teacher_yessenia.id)
            courses_to_add = [
                course_cloud,
                course_ti3,
                Course(course_name='Internet de las Cosas', course_code='1705268', semester='10'),
                Course(course_name='Robotica (E)', course_code='1705269', semester='10'),
                Course(course_name='Topicos en Ciberserguridad (E)', course_code='1705270', semester='10'),
                Course(course_name='Trabajo de Investigacion', course_code='1705271', semester='10')
            ]
            db.session.add_all(courses_to_add)
            db.session.commit()
            print(f"{len(courses_to_add)} courses created. Cloud Computing assigned to {teacher_alvaro.first_name}.")

            # 4. Crear Horarios (para Cloud Computing)
            schedules_to_add = [
                # Cloud Computing (Lun, Mar, Mie)
                Schedule(course_id=course_cloud.id, day_of_week=2, start_time=time(12, 20), end_time=time(14, 0), location='Aula 301'),
                Schedule(course_id=course_cloud.id, day_of_week=3, start_time=time(12, 20), end_time=time(14, 0), location='Aula 301'),
                Schedule(course_id=course_cloud.id, day_of_week=1, start_time=time(12, 20), end_time=time(14, 0), location='Laboratorio 2'),

                # TI3 (Lun, Vie)
                Schedule(course_id=course_ti3.id, day_of_week=1, start_time=time(14, 0), end_time=time(15, 40), location='Aula 202'),
                Schedule(course_id=course_ti3.id, day_of_week=5, start_time=time(10, 40), end_time=time(12, 20), location='Aula 202'),
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
            print(f"Error inserting data: {e}")
            
    @app.cli.command("test-db")
    def test_db():
        """
        Limpia la BD e inserta datos masivos desde el dataset att_faces_png.
        Configurado inicialmente para 10 personas (s1-s10).
        """
        from app.models.user import User, UserRole
        from app.models.teacher import Teacher
        from app.models.student import Student
        from app.models.course import Course
        from app.models.schedule import Schedule
        from app.models.enrollment import Enrollment
        from app.models.attendance import Attendance
        from datetime import time, date, datetime, timedelta
        from app.services.student_service import process_local_images
        from app.services.enrollment_service import assign_to_course
        import os
        import random

        TOTAL_FOLDERS_TO_PROCESS = 50 
        
        TARGET_IMAGES = ['front.jpg', 'left.jpg', 'right.jpg']
        
        print(f"--- INICIANDO TEST-DB (Procesando {TOTAL_FOLDERS_TO_PROCESS} estudiantes) ---")

        try:
            db.session.query(Attendance).delete()
            db.session.query(Enrollment).delete()
            db.session.query(Schedule).delete()
            db.session.query(Course).delete()
            db.session.query(Student).delete()
            db.session.query(Teacher).delete()
            db.session.query(User).delete()
            db.session.commit()
            print("Existing data cleared.")
        except Exception as e:
            db.session.rollback()
            print(f"Error clearing data (tables might not exist): {e}")
            return

        project_root = os.path.dirname(os.path.abspath(app.root_path))
        dataset_base_path = os.path.join(project_root, '../datasets/dataset_faces_color')

        try:
            print("Creating teachers...")
            user_t1 = User(email='profesor1@unsa.edu.pe', role=UserRole.TEACHER)
            user_t1.set_password('123456')
            teacher1 = Teacher(first_name='Alvaro', last_name='Mamani', user=user_t1)
            
            user_t2 = User(email='profesor2@unsa.edu.pe', role=UserRole.TEACHER)
            user_t2.set_password('123456')
            teacher2 = Teacher(first_name='Yessenia', last_name='Yari', user=user_t2)

            db.session.add_all([user_t1, teacher1, user_t2, teacher2])
            db.session.commit()

            students_created = []
            print(f"Processing folders s1_color to s{TOTAL_FOLDERS_TO_PROCESS}_color...")
            
            for i in range(1, TOTAL_FOLDERS_TO_PROCESS + 1):
                folder_name = f"s{i}_color"
                folder_path = os.path.join(dataset_base_path, folder_name)
                
                # Datos ficticios basados en el índice
                cui = f"2025{i:04d}" # ej: 20250001
                email = f"student_s{i}@unsa.edu.pe"
                first_name = f"Person"
                last_name = f"S{i}"

                # Crear Usuario y Estudiante
                user_s = User(email=email, role=UserRole.STUDENT)
                user_s.set_password('123456')
                student_s = Student(cui=cui, first_name=first_name, last_name=last_name, user=user_s)
                
                db.session.add(user_s)
                db.session.add(student_s)
                db.session.flush()
                
                # Procesar Imágenes específicas
                if os.path.isdir(folder_path):
                    valid_images = []
                    for img_name in TARGET_IMAGES:
                        full_path = os.path.join(folder_path, img_name)
                        if os.path.exists(full_path):
                            valid_images.append(full_path)
                    
                    if len(valid_images) > 0:
                        success = process_local_images(valid_images, student_s.id)
                        if success:
                            print(f" [OK] s{i}: {len(valid_images)} images processed.")
                            students_created.append(student_s)
                        else:
                            print(f" [ERR] s{i}: Failed to generate embeddings.")
                    else:
                        print(f" [WARN] s{i}: No matching images found ({TARGET_IMAGES}).")
                else:
                    print(f" [WARN] Folder not found: {folder_path}")

            db.session.commit()
            print(f"Total students created with embeddings: {len(students_created)}")

            # 4. Crear Cursos (Para los porcentajes)
            print("Creating courses...")
            # Curso A: 100% estudiantes
            course_100 = Course(course_name='Curso General (100%)', course_code='C100', semester='10', teacher_id=teacher1.id)
            # Curso B: 75% estudiantes
            course_75 = Course(course_name='Curso Electivo I (75%)', course_code='C075', semester='10', teacher_id=teacher1.id)
            # Curso C: 50% estudiantes
            course_50 = Course(course_name='Curso Electivo II (50%)', course_code='C050', semester='10', teacher_id=teacher2.id)
            # Curso D: 25% estudiantes
            course_25 = Course(course_name='Seminario Tesis (25%)', course_code='C025', semester='10', teacher_id=teacher2.id)

            all_courses = [course_100, course_75, course_50, course_25]
            db.session.add_all(all_courses)
            db.session.commit()

            # Crear Horarios ficticios para cada curso (necesario para consistencia)
            for c in all_courses:
                sch = Schedule(course_id=c.id, day_of_week=1, start_time=time(8,0), end_time=time(10,0), location='Aula Virtual')
                db.session.add(sch)
            db.session.commit()

            # 5. Matrícula Porcentual
            total_qty = len(students_created)
            
            groups = [
                (course_100, students_created),                                      # 100%
                (course_75,  students_created[:int(total_qty * 0.75)]),              # 75%
                (course_50,  students_created[:int(total_qty * 0.50)]),              # 50%
                (course_25,  students_created[:int(total_qty * 0.25)])               # 25%
            ]

            print("Enrolling students...")
            for course_obj, student_group in groups:
                count = 0
                for s in student_group:
                    if assign_to_course(s.id, course_obj.id):
                        enroll = Enrollment(student_id=s.id, course_id=course_obj.id)
                        db.session.add(enroll)
                        count += 1
                print(f" -> {course_obj.course_name}: {count} students enrolled.")
            
            db.session.commit()

            # 6. Generar Asistencia Histórica
            print("Generating attendance records...")
            base_date = date.today()
            days_back = base_date.weekday()
            last_monday = base_date - timedelta(days=days_back)
            
            attendance_dates = [
                last_monday - timedelta(weeks=3),
                last_monday - timedelta(weeks=2),
                last_monday - timedelta(weeks=1),
                last_monday
            ]

            attendance_records = []
            
            for course_obj, student_group in groups:
                for cls_date in attendance_dates:
                    for s in student_group:
                        # Lógica de simulación: 80% probabilidad de asistencia
                        is_present = random.random() < 0.8 
                        status = 'presente' if is_present else 'ausente'
                        # Hora check-in aleatoria entre 8:00 y 8:15 si vino
                        if is_present:
                            check_in = datetime.combine(cls_date, time(8, random.randint(0, 15)))
                        else:
                            check_in = None

                        att = Attendance(
                            student_id=s.id,
                            course_id=course_obj.id,
                            attendance_date=cls_date,
                            status=status,
                            check_in_time=check_in
                        )
                        attendance_records.append(att)

            db.session.add_all(attendance_records)
            db.session.commit()
            print(f"Generated {len(attendance_records)} attendance records.")
            print("\n--- TEST-DB COMPLETED SUCCESSFULLY ---")
    
        except Exception as e:
            db.session.rollback()
            print(f"An error occurred in test: {e}")

    @app.cli.command("bench-fps")
    def bench_fps():
        """Experimento B: Mide tiempos desglosados (Pipeline vs Matching)."""
        import requests
        import os
        import time
        
        API_URL = "http://localhost:4000/benchmark/process" 
        COURSE_ID_PARA_TEST = "56a2bd8d-a990-4c8b-a2b1-eac2911cf271" 
        
        scenarios = [1, 1, 5, 10, 20, 30, 40, 50]
        
        print("\n" + "="*105)
        print(f"{'N':<5} | {'TOTAL (s)':<12} | {'PIPELINE (s)':<15} | {'MATCHING (s)':<15} | {'FPS':<8} | {'FACES'}")
        print("="*105)

        project_root = os.path.dirname(os.path.abspath(__file__))
        
        is_warmup = True 

        for n in scenarios:
            filename = f"test_scene_{n}_students.jpg"
            if not os.path.exists(filename):
                print(f"{n:<5} | Archivo no encontrado: {filename}")
                continue

            files = {'image': (filename, open(filename, 'rb'), 'image/jpeg')}
            data = {'course_id': COURSE_ID_PARA_TEST}
            
            try:
                resp = requests.post(API_URL, files=files, data=data)
                
                if resp.status_code == 200:
                    json_data = resp.json()
                    
                    total = json_data.get('total_inference_time', 0)
                    pipe = json_data.get('pipeline_time', 0)
                    match = json_data.get('matching_time', 0)
                    count = json_data.get('face_count', 0)
                    fps = 1.0 / total if total > 0 else 0
                    
                    if is_warmup:
                        print(f"[WARM] Calentando motor con N={n}... (Tiempo: {total:.4f}s)")
                        is_warmup = False
                        continue

                    print(f"{n:<5} | {total:.4f} s     | {pipe:.4f} s        | {match:.6f} s       | {fps:.2f}     | {count}")
                else:
                    print(f"{n:<5} | ERROR {resp.status_code}")
                    
            except Exception as e:
                print(f"{n:<5} | ERROR CONEXION: {e}")

        print("="*105 + "\n")
        
    @app.cli.command("bench-exp-c")
    def bench_exp_c():
        """
        Experimento C: Robustez y Falsos Positivos vs Tamaño de Población (N).
        Prueba una imagen con 50 rostros contra cursos con 12, 25, 37 y 50 alumnos.
        """
        import requests
        import os
        from collections import Counter

        API_URL = "http://localhost:4000/benchmark/process"
        
        COURSES = [
            {"label": "N=12 (Baja)",   "id": "b0d29f9b-3311-48a0-a838-3ab333a07e65", "expected_hits": 12},
            {"label": "N=25 (Media)",  "id": "7d9eeb2a-d229-4f4e-afbc-63d7160a1fac", "expected_hits": 25},
            {"label": "N=37 (Alta)",   "id": "7635b82d-560f-4f0c-874b-f24055b6648a", "expected_hits": 37},
            {"label": "N=50 (Full)",   "id": "56a2bd8d-a990-4c8b-a2b1-eac2911cf271", "expected_hits": 50},
        ]
        
        TEST_IMAGE = "test_scene_50_students.jpg"

        if not os.path.exists(TEST_IMAGE):
            print(f"[ERROR] No se encuentra la imagen {TEST_IMAGE}. Ejecuta primero el generador de collage.")
            return

        print("\n" + "="*110)
        print(f"{'ESCENARIO (BD)':<15} | {'ROSTROS':<8} | {'IDENTIFICADOS':<15} | {'DESCONOCIDOS':<12} | {'FALSOS POSITIVOS?':<18} | {'DUPLICADOS'}")
        print("="*110)

        files = {'image': (TEST_IMAGE, open(TEST_IMAGE, 'rb'), 'image/jpeg')}
        
        for scenario in COURSES:
            c_label = scenario["label"]
            c_id = scenario["id"]
            expected = scenario["expected_hits"]
            
            files_payload = {'image': (TEST_IMAGE, open(TEST_IMAGE, 'rb'), 'image/jpeg')}
            data_payload = {'course_id': c_id}

            try:
                resp = requests.post(API_URL, files=files_payload, data=data_payload)
                
                if resp.status_code != 200:
                    print(f"{c_label:<15} | Error API: {resp.status_code} - {resp.text}")
                    continue

                result = resp.json()
                faces = result.get("results", [])
                total_detected = len(faces)
                
                identified_names = []
                unknown_count = 0
                
                for face in faces:
                    identity = face["identity"]
                    if identity == "Unknown":
                        unknown_count += 1
                    else:
                        identified_names.append(identity)

                count_identified = len(identified_names)
                
                fp_count = max(0, count_identified - expected)
                
                fp_text = f"{fp_count}"
                if fp_count > 0:
                    fp_text += " (!)"

                name_counts = Counter(identified_names)
                duplicates = [name for name, count in name_counts.items() if count > 1]
                
                dup_text = "Ninguno"
                if duplicates:
                    dup_text = f"{len(duplicates)} Casos"

                print(f"{c_label:<15} | {total_detected:<8} | {count_identified:<15} | {unknown_count:<12} | {fp_text:<18} | {dup_text}")

            except Exception as e:
                print(f"{c_label:<15} | EXCEPCIÓN: {e}")

        print("="*110 + "\n")
        print("NOTA INTERPRETATIVA:")
        print(" - IDENTIFICADOS: Debería ser cercano al N del curso (si el modelo es perfecto).")
        print(" - DESCONOCIDOS: El resto de personas en la foto (50 - N).")
        print(" - FALSOS POSITIVOS: Si Identificados > N esperado, el sistema aceptó impostores.")
        print(" - DUPLICADOS: Si dice 'Casos', el sistema asignó el mismo nombre a 2 personas distintas en la foto.")
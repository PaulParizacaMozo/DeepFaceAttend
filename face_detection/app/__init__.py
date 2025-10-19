from flask import Flask
import config
from .models import face_model as face_analyzer
# from .models import face_detection, face_embedding
from .services import database_service

def create_app_2():
    app = Flask(__name__)
    app.config.from_object(config)

    print("Initializing application resources...")
    known_db = database_service.load_known_faces_from_csv("students")
    face_model = face_analyzer.load_model()

    # 🔹 Nueva parte: convertir a matriz NumPy
    known_matrix, known_labels = database_service.prepare_vectorized_db(known_db)

    app.face_model = face_model
    # app.face_detector = face_detection.detect_and_align_faces  # función callable
    # app.face_recognizer = face_embedding.load_arcface_model()  # modelo instanciado
    app.known_db = known_db
    app.known_matrix = known_matrix
    app.known_labels = known_labels
    print("Application resources loaded successfully.")

    from .routes.processing_routes import processing_bp
    from .routes.recognition_routes import recognition_bp

    app.register_blueprint(processing_bp)
    app.register_blueprint(recognition_bp)

    return app

def create_app():
    app = Flask(__name__)
    app.config.from_object(config)

    print("Initializing application resources...")
    face_model = face_analyzer.load_model()
    known_db = database_service.load_known_faces_from_db()

    app.face_model = face_model
    app.known_db = known_db
    print("Application resources loaded successfully.")

    # --- Register Blueprints ---
    from .routes.processing_routes import processing_bp
    from .routes.recognition_routes import recognition_bp

    app.register_blueprint(processing_bp)
    app.register_blueprint(recognition_bp)

    return app

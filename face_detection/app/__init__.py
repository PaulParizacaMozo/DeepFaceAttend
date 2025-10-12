from flask import Flask
import config
from .models import face_model as face_analyzer
from .services import database_service

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
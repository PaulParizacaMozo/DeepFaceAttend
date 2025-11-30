import insightface
from insightface.app import FaceAnalysis

def load_model():
    print("Cargando modelo de análisis facial...")
    model = FaceAnalysis(allowed_modules=['detection', 'recognition'])
    model.prepare(ctx_id=0, det_size=(640, 640))
    print("Modelo cargado exitosamente.")
    return model
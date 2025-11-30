import cv2
import numpy as np
import torch
import os
import time # Solo para el print de carga

# Dependencias de Detección y Reconocimiento
try:
    from retinaface import RetinaFace
except ImportError:
    print("Error: Biblioteca 'retinaface-pytorch' no encontrada.")
    print("Por favor, instálala con: pip install retinaface-pytorch")
    exit()

try:
    from .arcface import Arcface
except ImportError:
    print("Error: No se pudo importar 'arcface.py'.")
    print("Asegúrate de que 'arcface.py' e 'iresnet.py' estén en el mismo directorio.")
    exit()


# --- 1. CLASE DE DATOS PARA LA CARA ---

class CustomFace:
    def __init__(self, det_score, embedding, bbox, landmarks):
        self.det_score = det_score   # Puntuación de confianza de la detección
        self.embedding = embedding   # Vector de embedding (NumPy array)
        self.bbox = bbox             # Bounding box [x1, y1, x2, y2]
        self.landmarks = landmarks   # Puntos clave faciales (dict)

# --- 2. FUNCIONES DE ALINEAMIENTO Y PREPROCESAMIENTO ---
def align_and_transform_face(image, landmarks):
    TARGET_FACE_SIZE = (112, 112)
    ref_points = np.array([
        [38.2946, 51.6963], [73.5318, 51.5014], [56.0252, 71.7366],
        [41.5493, 92.3655], [70.7299, 92.2041]
    ], dtype=np.float32)
    
    detected_points = np.array([
        landmarks['left_eye'], landmarks['right_eye'], landmarks['nose'],
        landmarks['mouth_left'], landmarks['mouth_right']
    ], dtype=np.float32)
    
    transform_matrix = cv2.estimateAffine2D(detected_points, ref_points)[0]
    aligned_face = cv2.warpAffine(image, transform_matrix, TARGET_FACE_SIZE, borderMode=cv2.BORDER_REPLICATE)
    return aligned_face

def preprocess_face_image(face_image_array, device):
    # 1. Normalización: Escala los valores de píxeles de [0, 255] a [-1, 1]
    img_normalized = (face_image_array.astype(np.float32) - 127.5) / 128.0
    # 2. Transposición: Cambia el formato de (H, W, C) a (C, H, W) como espera PyTorch
    img_transposed = np.transpose(img_normalized, (2, 0, 1))
    # 3. Conversión a Tensor: Convierte el array de NumPy a un tensor de PyTorch
    input_tensor = torch.from_numpy(img_transposed).to(device).unsqueeze(0)
    return input_tensor


# --- 3. CLASE PRINCIPAL DEL MODELO ---

class CustomFaceAnalysis:
    def __init__(self, arcface_model_path):
        print("Cargando modelo ArcFace personalizado...")
        if not os.path.exists(arcface_model_path):
            print(f"Error: Archivo del modelo no encontrado en '{arcface_model_path}'")
            raise FileNotFoundError(f"No se encontró el modelo en {arcface_model_path}")
            
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        
        try:
            # Cargar el modelo de reconocimiento (Arcface)
            self.recognition_model = Arcface(backbone='iresnet50', mode='predict')
            self.recognition_model.load_state_dict(torch.load(arcface_model_path, map_location=self.device), strict=False)
            self.recognition_model.to(self.device)
            self.recognition_model.eval()
            print(f"Modelo ArcFace cargado exitosamente en {self.device}")
            print("Preparando el detector RetinaFace...")
            _ = RetinaFace.detect_faces(np.zeros((640, 640, 3), dtype=np.uint8))
            print("Detector (RetinaFace) listo.")
            
        except Exception as e:
            print(f"Error al cargar los modelos: {e}")
            raise

    @torch.no_grad()  # Desactiva el cálculo de gradientes para inferencia
    def get(self, frame):
        results = []
        # 1. Detección de caras con RetinaFace
        try:
            faces_data = RetinaFace.detect_faces(frame)
            if not isinstance(faces_data, dict):
                return []
        except Exception as e:
            print(f"Error durante la detección con RetinaFace: {e}")
            return []

        # 2. Procesar cada cara detectada
        for face_id, face_info in faces_data.items():
            try:
                score = face_info['score']
                landmarks = face_info['landmarks']
                bbox = face_info['facial_area'] # [x1, y1, x2, y2]
                aligned_face = align_and_transform_face(frame, landmarks)
                input_tensor = preprocess_face_image(aligned_face, self.device)
                embedding_tensor = self.recognition_model(input_tensor)
                embedding_vector = embedding_tensor.cpu().numpy().flatten()
                face_obj = CustomFace(
                    det_score=score,
                    embedding=embedding_vector,
                    bbox=bbox,
                    landmarks=landmarks
                )
                results.append(face_obj)
            except Exception as e:
                print(f"Error procesando la cara {face_id}: {e}")
                continue 
                
        return results

# --- 4. FUNCIÓN DE CARGA PÚBLICA ---

def load_model(model_path="ArcFace_iResNet50_CASIA_FaceV5.pth"):
    print("Cargando pipeline de análisis facial personalizado (RetinaFace + ArcFace)...")
    start_time = time.perf_counter()
    base_dir = os.path.abspath(os.path.dirname(__file__))
    full_model_path = os.path.join(base_dir, model_path)
    model = CustomFaceAnalysis(arcface_model_path=full_model_path)
    end_time = time.perf_counter()
    print(f"Pipeline personalizado cargado exitosamente en {end_time - start_time:.2f} segundos.")
    return model
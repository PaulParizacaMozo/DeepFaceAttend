import cv2
import requests
import time

# URL de tu servicio backend
SERVICE_URL = 'http://localhost:4000/process_frame'

def start_camera_feed():
    cap = cv2.VideoCapture(0) # 0 para la cámara web por defecto
    if not cap.isOpened():
        print("Error: No se pudo abrir la cámara.")
        return
    print("Cámara iniciada. Presiona 'q' para salir.")

    while True:
        ret, frame = cap.read()
        if not ret:
            print("Error al capturar el fotograma.")
            break

        # Muestra el video en una ventana (opcional)
        cv2.imshow('Camera Feed', frame)
        _, img_encoded = cv2.imencode('.jpg', frame)
        
        # Preparar el archivo para enviar
        files = {'image': ('frame.jpg', img_encoded.tobytes(), 'image/jpeg')}
        try:
            response = requests.post(SERVICE_URL, files=files, timeout=5)
            if response.status_code == 200:
                print(f"Servidor respondió: {response.json()}")
            else:
                print(f"Error del servidor: {response.status_code}")
        except requests.exceptions.RequestException as e:
            print(f"Error de conexión con el servidor: {e}")
        time.sleep(1) 
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    cap.release()
    cv2.destroyAllWindows()
    print("Cámara detenida.")

if __name__ == '__main__':
    start_camera_feed()
# client.py

import cv2
import requests
import time
import config

def start_camera_feed():
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Error: No se pudo abrir la cámara.")
        return
    print("Cámara iniciada. Presiona 'q' para salir.")

    while True:
        ret, frame = cap.read()
        if not ret:
            print("Error al capturar el fotograma.")
            break

        cv2.imshow('Camera Feed', frame)
        _, img_encoded = cv2.imencode('.jpg', frame)
        files = {'image': ('frame.jpg', img_encoded.tobytes(), 'image/jpeg')}

        try:
            # Usar la URL desde el archivo de configuración
            response = requests.post(config.SERVICE_URL, files=files, timeout=5)
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
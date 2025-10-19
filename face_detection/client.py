# client.py

import cv2
import requests
import time
import config
import threading

def send_frame_to_server(frame):
    try:
        _, img_encoded = cv2.imencode('.jpg', frame)
        files = {'image': ('frame.jpg', img_encoded.tobytes(), 'image/jpeg')}
        
        print("\nSending frame to server...")
        response = requests.post(config.SERVICE_URL, files=files, timeout=10)
        
        if response.status_code == 200:
            print(f"Server response: {response.json()}")
        else:
            print(f"Server error: {response.status_code}")
            
    except requests.exceptions.RequestException as e:
        print(f"Connection error: {e}")

def start_camera_feed():
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Error: Could not open camera.")
        return
        
    print("Camera started. Press 'q' to exit.")
    
    last_send_time = time.time()
    send_interval = 5  # Intervalo de 30 segundos

    while True:
        ret, frame = cap.read()
        if not ret:
            print("Error capturing frame.")
            break
        
        cv2.imshow('Real-time Camera Feed', frame)

        current_time = time.time()
        if current_time - last_send_time >= send_interval:
            last_send_time = current_time
            frame_copy = frame.copy()
            thread = threading.Thread(target=send_frame_to_server, args=(frame_copy,))
            thread.start()

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()
    print("Camera stopped.")

if __name__ == '__main__':
    start_camera_feed()
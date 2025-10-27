import cv2

CAMERA_INDEX = "http://192.168.1.46:8080/video" # 0, 1, ...
cap = cv2.VideoCapture(CAMERA_INDEX)

if not cap.isOpened():
    print("Error: No se pudo abrir la cámara.")
    exit()

print("Cámara abierta. Presiona 'q' en la ventana para salir.")

while True:
    ret, frame = cap.read()

    if not ret:
        print("Error: No se pudo leer el frame. Saliendo...")
        break

    cv2.imshow("Mi Camara", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

print("Cerrando la cámara y las ventanas.")
cap.release()
cv2.destroyAllWindows()
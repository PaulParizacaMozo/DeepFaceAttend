import cv2

def encontrar_camaras_disponibles():
    index = 0
    camaras_disponibles = ["http://192.168.1.46:8080/video"]
    
    print("Buscando cámaras...")

    while True:
        cap = cv2.VideoCapture(index)
        
        if not cap.isOpened():
            break
        else:
            print(f"Cámara encontrada en el índice: {index}")
            camaras_disponibles.append(index)
            cap.release()
        
        index += 1
        if index >= 10:
            break

    return camaras_disponibles

if __name__ == "__main__":
    camaras = encontrar_camaras_disponibles()
    
    if not camaras:
        print("No se encontró ninguna cámara conectada.")
    else:
        print(f"\nResumen: Cámaras disponibles en los índices: {camaras}")
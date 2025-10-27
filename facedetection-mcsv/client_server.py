import cv2
import requests
import time
import threading
from flask import Flask, request, jsonify

# --- Configuración de Endpoints ---
PROCESS_URL = "http://127.0.0.1:4000/process_frame" # Servidor de procesamiento (Puerto 4000)
ATTENDANCE_URL = "http://127.0.0.1:5000/attendance/" # Servidor de toma de asistencia (Puerto 5000)
CAMERA_INDEX = 0 # Índice de la cámara a usar

# --- Recursos Globales Compartidos ---
global_camera = None  # Objeto VideoCapture
global_frame = None  # El último frame capturado
global_frame_lock = threading.Lock()  # Lock para proteger el global_frame
global_job_running = False  # Flag para evitar trabajos duplicados
global_job_lock = threading.Lock()  # Lock para proteger el flag

# --- Inicialización de Flask ---
app = Flask(__name__)

# --- 1. Hilo de la Cámara (Siempre encendida) ---
def run_camera():
    global global_frame, global_camera
    print("[INFO] Hilo de la cámara iniciado.")
    while True:
        ret, frame = global_camera.read()
        if not ret:
            print("[ERROR] No se pudo capturar frame de la cámara. Reintentando...")
            time.sleep(1)
            continue
        with global_frame_lock:
            global_frame = frame.copy()

        cv2.imshow("Camara en vivo", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):  # Presiona 'q' para cerrar
            break

        time.sleep(0.03)

# --- 2. Helper: Enviar Frame para Procesar (Puerto 4000) ---
def process_frame_on_server(frame, schedule_id):
    try:
        _, img_encoded = cv2.imencode('.jpg', frame)
        files = {'image': ('frame.jpg', img_encoded.tobytes(), 'image/jpeg')}
        payload = {'schedule_id': schedule_id}
        print(f"[JOB] Enviando frame a 5000 (Schedule: {schedule_id})...")
        response = requests.post(PROCESS_URL, files=files, data=payload, timeout=10)
        if response.status_code == 200:
            data = response.json()
            return data.get('recognized_faces', [])
        else:
            print(f"[JOB] Error del servidor 5000: {response.status_code}")
            return None
    except requests.exceptions.RequestException as e:
        print(f"[JOB] Error de conexión con el servidor 5000: {e}")
        return None

# --- 3. Helper: Enviar Asistencia (Puerto 5000) ---
def process_recognitions(recognized_faces, scheduler_id):
    if not recognized_faces:
        return

    print(f"[JOB] Procesando {len(recognized_faces)} caras para el curso {scheduler_id}.")
    for face in recognized_faces:
        student_id = face.get('identity')
        if student_id and student_id != 'Unknown':
            payload = {
                'student_id': student_id,
                'schedule_id': scheduler_id
            }
            try:
                print(f"[JOB] Enviando asistencia para {student_id} a {ATTENDANCE_URL}...")
                requests.post(ATTENDANCE_URL, json=payload, timeout=5)
            except requests.exceptions.RequestException as e:
                print(f"[JOB] Error de conexión con servidor de asistencia: {e}")
        else:
            print(f"[JOB] Identidad 'Unknown' o inválida, omitiendo.")

# --- 4. Hilo del Trabajo de Captura (Iniciado por el Endpoint) ---
def capture_job(scheduler_id, duration_min, interval_sec):
    global global_job_running
    print(f"[JOB] Iniciado: Horario={scheduler_id}, Duración={duration_min} min, Intervalo={interval_sec} sec.")
    try:
        end_time = time.time() + duration_min * 60
        while time.time() < end_time:
            current_frame_copy = None
            with global_frame_lock:
                if global_frame is not None:
                    current_frame_copy = global_frame.copy()
            if current_frame_copy is None:
                print("[JOB] Esperando el primer frame de la cámara...")
                time.sleep(1)
                continue
            recognized_faces = process_frame_on_server(current_frame_copy, scheduler_id)
            if recognized_faces:
                proc_thread = threading.Thread(target=process_recognitions, args=(recognized_faces, scheduler_id))
                proc_thread.start()
            else:
                print("[JOB] No se recibieron caras del servidor de 5000.")
            print(f"[JOB] Esperando {interval_sec} segundos para la próxima captura...")
            time.sleep(interval_sec)
    except Exception as e:
        print(f"[JOB] Error fatal en el hilo del trabajo: {e}")
    finally:
        with global_job_lock:
            global_job_running = False
        print(f"[JOB] Finalizado: Horario={scheduler_id}.")

# --- 5. Endpoint de Flask (Puerto 6000) ---
@app.route('/start_capture', methods=['POST'])
def start_capture_route():
    global global_job_running
    data = request.json
    try:
        scheduler_id = data['scheduler_id']
        duration = int(data['duration'])
        interval = int(data['interval'])
    except KeyError as e:
        return jsonify({"error": f"Dato faltante: {e}"}), 400
    except ValueError:
        return jsonify({"error": "Tipos de datos inválidos para 'duration' o 'interval'"}), 400

    with global_job_lock:
        if global_job_running:
            return jsonify({"error": "Un trabajo de captura ya está en progreso."}), 409  # 409 Conflict

        global_job_running = True
    
    job_thread = threading.Thread(target=capture_job, args=(scheduler_id, duration, interval))
    job_thread.start()

    return jsonify({"status": "Trabajo de captura iniciado.", "data": data}), 202

if __name__ == '__main__':
    global_camera = cv2.VideoCapture(CAMERA_INDEX)
    if not global_camera.isOpened():
        print(f"[ERROR] No se pudo abrir la cámara (índice {CAMERA_INDEX}).")
        exit()
    print("[INFO] Iniciando hilo de la cámara...")
    cam_thread = threading.Thread(target=run_camera, daemon=True)
    cam_thread.start()
    print(f"[INFO] Iniciando servidor Flask en http://0.0.0.0:6000")
    app.run(host='0.0.0.0', port=6000)
    global_camera.release()
    print("[INFO] Servidor detenido, cámara liberada.")

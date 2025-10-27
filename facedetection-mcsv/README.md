# **Microservicio de Análisis Facial**

Este proyecto es un **microservicio especializado en Python y Flask**, diseñado para ser el motor de IA en un sistema más grande. Su única responsabilidad es manejar las operaciones de procesamiento facial más pesadas: la generación de embeddings a partir de imágenes y el reconocimiento facial en tiempo real.

## **Características**

- **Arquitectura de Microservicio**: Centraliza la lógica de IA, permitiendo que otros servicios (como un backend de gestión de estudiantes) deleguen el procesamiento pesado.
- **API de Procesamiento de Embeddings**: Ofrece un endpoint para registrar nuevos perfiles faciales. Recibe un conjunto de imágenes y un ID, y devuelve la ruta al archivo de embeddings generado.
- **API de Reconocimiento en Tiempo Real**: Proporciona un endpoint optimizado para recibir un fotograma de video, identificar rostros conocidos y devolver su identidad al instante.
- **Modelo de Alta Precisión**: Utiliza `insightface` para garantizar una detección y un análisis facial de alta calidad.

---

## **Instalación y Configuración del Entorno**

Sigue estos pasos para configurar el entorno de trabajo usando Conda.

### **1. Crear el Entorno Virtual**

Crea un nuevo entorno de Conda con Python 3.9 para mantener las dependencias aisladas.

```bash
python3 -m venv venv
```

### **2. Activar el Entorno**

Cada vez que trabajes en el proyecto, activa el entorno con el siguiente comando:

```bash
source venv/bin/activate
```

### **3. Instalar Dependencias de Python**

Instala todas las librerías necesarias para el proyecto con un solo comando:

<!-- ```bash
pip install Flask retina-face insightface onnxruntime opencv-python numpy requests pandas
``` -->

```bash
pip install -r requirements.txt
```

## **API Endpoints**

Este microservicio expone dos endpoints principales, cada uno con una responsabilidad clara.

### **1. Procesamiento de Embeddings**

- **Ruta**: `POST /process-images`
- **Propósito**: Este endpoint está diseñado para ser consumido por **otro microservicio** (por ejemplo, un backend de gestión de estudiantes). Su función es recibir un conjunto de imágenes y un ID único (como un CUI de estudiante).
- **Funcionamiento**:
  1.  Recibe los datos en formato `multipart/form-data`.
  2.  Procesa cada imagen para detectar rostros y extraer sus embeddings.
  3.  Guarda los embeddings de alta calidad en un archivo `.csv`.
  4.  Devuelve una respuesta JSON con el `status` y la **ruta (`filepath`)** donde se almacenó el archivo de embeddings.
- **Caso de uso**: Cuando un nuevo estudiante es creado en el sistema principal, ese sistema llama a este endpoint para generar y almacenar el perfil facial del estudiante.

### **2. Reconocimiento en Tiempo Real**

- **Ruta**: `POST /process_frame`
- **Propósito**: Este endpoint está optimizado para ser usado por un **cliente en tiempo real**, como un script (`control.py`) que captura video desde una cámara.
- **Funcionamiento**:
  1.  Recibe una única imagen (un fotograma del video).
  2.  Detecta todos los rostros en el fotograma.
  3.  Compara cada rostro detectado con la base de datos de perfiles conocidos.
  4.  Devuelve una respuesta JSON con una lista de los rostros reconocidos (`recognized_faces`), incluyendo su identidad y el nivel de confianza.
- **Caso de uso**: Un programa de control de asistencia lo utiliza para enviar fotogramas de una cámara y recibir de vuelta los IDs de los estudiantes presentes para marcar su asistencia.

---

## **Cómo Iniciar y Probar el Sistema**

### **Paso 1: Iniciar el Microservicio**

A diferencia de una aplicación monolítica, el único paso para usar este servicio es iniciarlo. Los otros componentes del sistema se encargarán de consumir sus endpoints.

- Abre una terminal, activa el entorno (`conda activate backend_facial`) y ejecuta:
  ```bash
  python run.py
  ```

El servidor se iniciará y esperará conexiones en el puerto 4000. **Deja esta terminal abierta** para que el servicio permanezca disponible.

### **Paso 2: Probar el Reconocimiento con la Cámara (Opcional)**

Para verificar que el endpoint de reconocimiento en tiempo real funciona correctamente, puedes usar el script `client.py`. Este script simula una aplicación de asistencia activando tu cámara y enviando los fotogramas al microservicio.

- Abre una **segunda terminal**, activa el entorno (`conda activate backend_facial`) y ejecuta:
  ```bash
  python client.py
  ```

Se abrirá una ventana mostrando el video de tu cámara. Si una persona registrada se pone frente a ella, verás la respuesta de reconocimiento del servidor directamente en esta terminal.

# **Backend de Registro y Reconocimiento Facial**

Este proyecto implementa un servicio backend en Flask diseñado para procesar fotogramas de video en tiempo real. El sistema detecta rostros, extrae sus características (embeddings) y los guarda en una base de datos para su posterior reconocimiento en un sistema de control de asistencia.

## **Características**

- **Detección de Rostros**: Utiliza el modelo `insightface` para una detección precisa.
- **Extracción de Embeddings**: Genera un vector de 512 dimensiones para cada rostro detectado.
- **Base de Datos Persistente**: Guarda las imágenes de los rostros y sus embeddings en una carpeta y un archivo CSV, respectivamente.
- **Arquitectura Cliente-Servidor**: El backend (`app.py`) procesa los datos enviados por un cliente (`client.py`) que controla la cámara.

## **Instalación y Configuración del Entorno**

Sigue estos pasos para configurar el entorno de trabajo usando Conda.

### **1. Crear el Entorno Virtual**

Crea un nuevo entorno de Conda con Python 3.9 para mantener las dependencias aisladas.

```bash
conda create --name backend_facial python=3.9
```

### **2. Activar el Entorno**

Cada vez que trabajes en el proyecto, activa el entorno con el siguiente comando:

```bash
conda activate backend_facial
```

### **3. Instalar Dependencias de Python**

Instala todas las librerías necesarias para el proyecto con un solo comando:

```bash
pip install Flask retina-face insightface onnxruntime opencv-python numpy requests pandas
```

### **4. Solucionar Compatibilidad (Importante para Linux)**

La librería `insightface` a veces requiere una versión más reciente de `libstdc++`. Este comando la instala dentro de tu entorno Conda para evitar errores de importación.

```bash
conda install -c conda-forge libstdcxx-ng
```

---

## **Cómo Usar el Sistema** ▶️

El sistema tiene dos componentes que deben ejecutarse en terminales separadas: el **servidor** y el **cliente**.

### **Paso 1: Iniciar el Servidor Backend**

El servidor es el cerebro del sistema. Se encarga de recibir las imágenes y procesarlas.

- **Para registrar una nueva persona**, asegúrate de modificar la variable `PERSON_NAME` dentro del archivo `app.py`.
- Abre una terminal, activa el entorno (`conda activate backend_facial`) y ejecuta:

```bash
python app.py
```

El servidor se iniciará y esperará conexiones en el puerto 4000.

### **Paso 2: Iniciar el Cliente de la Cámara**

El cliente activa la cámara, captura fotogramas y los envía al servidor para ser procesados.

- Abre una **segunda terminal**, activa el entorno (`conda activate backend_facial`) y ejecuta:

```bash
python client.py
```

Se abrirá una ventana mostrando la imagen de la cámara y el proceso de detección comenzará. ¡Mira la terminal del servidor para ver cómo se guardan los rostros\!

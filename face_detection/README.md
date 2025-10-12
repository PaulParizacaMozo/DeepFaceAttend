# **Backend de Registro y Reconocimiento Facial**

Este proyecto implementa un servicio backend en Flask diseñado para procesar fotogramas de video en tiempo real. El sistema detecta rostros, extrae sus características (embeddings) y los guarda en una base de datos para su posterior reconocimiento.

## **Características**

- **API de Registro**: Un endpoint para registrar nuevas personas enviando su nombre y un conjunto de imágenes.
- **API de Reconocimiento**: Un endpoint que recibe un fotograma y devuelve la identidad de las personas reconocidas.
- **Detección Precisa**: Utiliza el robusto modelo `insightface` para la detección y análisis facial.
- **Base de Datos Persistente**: Utiliza SQLite para gestionar los perfiles de las personas y archivos CSV para almacenar los embeddings.
- **Arquitectura Modular**: El código está organizado en módulos para facilitar su mantenimiento y escalabilidad.

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

## **Cómo Usar el Sistema**

El flujo de trabajo consta de 3 pasos: iniciar el servidor, registrar a las personas y, finalmente, iniciar el cliente de reconocimiento.

### **Paso 1: Iniciar el Servidor Backend**

El servidor es el cerebro del sistema. Debe estar siempre en ejecución para poder registrar y reconocer personas.

- Abre una terminal, activa el entorno (`conda activate backend_facial`) y ejecuta:
  ```bash
  python app.py
  ```

El servidor se iniciará y esperará conexiones en el puerto 4000. **Deja esta terminal abierta.**

### **Paso 2: Registrar Personas en la Base de Datos**

Antes de que el sistema pueda reconocer a alguien, primero necesita saber cómo es esa persona. Este paso envía un nombre y un conjunto de imágenes al servidor para crear un perfil en la base de datos.

- **Prepara tus imágenes**: Crea una carpeta con varias fotos del rostro de la persona que quieres registrar (ej. `./kevin/`).
- Abre una **nueva terminal** y usa el siguiente comando `curl` para enviar los datos.

```bash
curl -X POST http://localhost:4000/register \
-F 'name=kevin' \
-F 'images=@./kevin/kevin_right.png' \
-F 'images=@./kevin/kevin_left.png' \
-F 'images=@./kevin/kevin_front.png'
```

**¿Cómo funciona este comando?**

- `curl -X POST ...`: Realiza una petición POST al endpoint `/register` de tu servidor.
- `-F 'name=kevin'`: Envía un campo de formulario llamado `name` con el valor `kevin`.
- `-F 'images=@./kevin/...'`: El flag `-F` se usa para adjuntar archivos. La clave debe ser `images` para cada archivo, y el `@` le indica a `curl` que cargue el contenido del archivo especificado en la ruta.

Repite este paso para cada persona que desees registrar en el sistema.

### **Paso 3: Iniciar el Reconocimiento en Tiempo Real**

Una vez que has registrado al menos una persona, ya puedes iniciar el cliente para que el sistema comience a reconocerla.

- Abre una **tercera terminal** (o usa la del paso 2), activa el entorno (`conda activate backend_facial`) y ejecuta:
  ```bash
  python client.py
  ```

Se abrirá una ventana mostrando la imagen de la cámara. Cuando una persona registrada se ponga frente a ella, verás en la terminal del cliente la identidad reconocida.

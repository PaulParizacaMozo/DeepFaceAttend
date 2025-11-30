import { useState, type FormEvent, type ChangeEvent } from "react";
import { useNavigate } from "react-router-dom";
import api from "../services/api";
import unsaBgURL from "../assets/unsa_bg2.avif";
import { useAuth } from "../hooks/useAuth";

// Definimos los tipos de fotos requeridas
type PhotoType = "front" | "right" | "left";

interface PhotoState {
  file: File | null;
  preview: string | null;
}

const UpdateBiometrics = () => {
  const { user } = useAuth(); // Obtener usuario para el envío
  // --- Estados de las 3 Fotos ---
  const [photos, setPhotos] = useState<Record<PhotoType, PhotoState>>({
    front: { file: null, preview: null },
    right: { file: null, preview: null },
    left: { file: null, preview: null },
  });

  // Estados de UI
  const [error, setError] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const navigate = useNavigate();

  // --- Manejo de Imagen ---
  const handleImageChange = (
    e: ChangeEvent<HTMLInputElement>,
    type: PhotoType
  ) => {
    if (e.target.files && e.target.files[0]) {
      const file = e.target.files[0];
      setPhotos((prev) => ({
        ...prev,
        [type]: {
          file,
          preview: URL.createObjectURL(file),
        },
      }));
      setError("");
    }
  };

  const removeImage = (type: PhotoType) => {
    setPhotos((prev) => ({
      ...prev,
      [type]: { file: null, preview: null },
    }));
  };

  // --- Submit Final ---
  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    setError("");
    setIsLoading(true);

    if (!photos.front.file || !photos.right.file || !photos.left.file) {
      setError("Por favor suba las 3 fotografías requeridas antes de enviar.");
      setIsLoading(false);
      return;
    }

    // Preparar FormData
    const formData = new FormData();

    // NOTA: El backend (Python) espera recibir una lista bajo la key 'images'
    // para procesar iterativamente. Agregamos las 3 con el mismo nombre.
    formData.append("images", photos.front.file);
    formData.append("images", photos.right.file);
    formData.append("images", photos.left.file);

    // Agregamos el ID del usuario para que el backend sepa a quién actualizar
    if (user?.id) {
      formData.append("user_id", user.id);
    }

    try {
      // Usamos un endpoint hipotético para procesar las imagenes y actualizar el booleano
      // Asegúrate de tener esta ruta configurada en tu backend (ej. en student_routes)
      await api.post("/students/upload-embeddings", formData, {
        headers: {
          "Content-Type": "multipart/form-data",
        },
      });

      alert("¡Datos actualizados correctamente!");

      // REDIRECCIÓN AL DASHBOARD
      // Como ahora el booleano será true, el Dashboard dejará pasar al usuario.
      navigate("/dashboard");
    } catch (err: any) {
      console.error(err);
      const errorMessage =
        err.response?.data?.message ||
        "Error al procesar las imágenes. Asegúrese de que su rostro sea visible.";
      setError(errorMessage);
    } finally {
      setIsLoading(false);
    }
  };

  // Helper para renderizar cada caja de upload
  const renderUploadBox = (type: PhotoType, label: string) => {
    const photoData = photos[type];

    return (
      <div className="flex flex-col gap-2">
        <label className="block text-sm font-medium text-gray-700">
          {label}
        </label>
        <div className="relative flex-1 min-h-[160px] rounded-lg border-2 border-dashed border-gray-300 hover:bg-gray-50 transition-colors flex flex-col items-center justify-center p-4">
          {photoData.preview ? (
            <div className="relative w-full h-full flex items-center justify-center">
              <img
                src={photoData.preview}
                alt={`${type} view`}
                className="max-h-32 w-auto object-contain rounded-md shadow-sm"
              />
              <button
                type="button"
                onClick={() => removeImage(type)}
                className="absolute -top-3 -right-3 bg-red-100 text-red-600 rounded-full p-1.5 shadow-sm hover:bg-red-200 transition-colors"
              >
                <svg
                  xmlns="http://www.w3.org/2000/svg"
                  viewBox="0 0 20 20"
                  fill="currentColor"
                  className="w-4 h-4"
                >
                  <path d="M6.28 5.22a.75.75 0 00-1.06 1.06L8.94 10l-3.72 3.72a.75.75 0 101.06 1.06L10 11.06l3.72 3.72a.75.75 0 101.06-1.06L11.06 10l3.72-3.72a.75.75 0 00-1.06-1.06L10 8.94 6.28 5.22z" />
                </svg>
              </button>
            </div>
          ) : (
            <div className="text-center w-full">
              <svg
                className="mx-auto h-10 w-10 text-gray-400"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
                aria-hidden="true"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={1.5}
                  d="M6.827 6.175A2.31 2.31 0 015.186 7.23c-.38.054-.757.112-1.134.175C2.999 7.58 2.25 8.507 2.25 9.574V18a2.25 2.25 0 002.25 2.25h15A2.25 2.25 0 0021.75 18V9.574c0-1.067-.75-1.994-1.802-2.169a47.865 47.865 0 00-1.134-.175 2.31 2.31 0 01-1.64-1.055l-.822-1.316a2.192 2.192 0 00-1.736-1.039 48.774 48.774 0 00-5.232 0 2.192 2.192 0 00-1.736 1.039l-.821 1.316z"
                />
              </svg>
              <div className="mt-2 text-sm text-gray-600">
                <label
                  htmlFor={`file-upload-${type}`}
                  className="relative cursor-pointer rounded-md font-medium text-primary hover:text-primary/80 focus-within:outline-none"
                >
                  <span>Subir foto</span>
                  <input
                    id={`file-upload-${type}`}
                    name={`file-upload-${type}`}
                    type="file"
                    accept="image/*"
                    className="sr-only"
                    onChange={(e) => handleImageChange(e, type)}
                  />
                </label>
              </div>
            </div>
          )}
        </div>
      </div>
    );
  };

  return (
    <div className="relative min-h-screen w-full overflow-hidden">
      {/* Capas de fondo */}
      <div
        className="absolute inset-0 bg-cover bg-center"
        style={{ backgroundImage: `url(${unsaBgURL})` }}
      ></div>
      <div className="absolute inset-0 bg-gray-400/60 backdrop-blur-sm"></div>

      <div className="relative flex min-h-screen items-center justify-center p-4">
        {/* Contenedor Principal Centrado */}
        <div className="w-full max-w-4xl transition-all duration-500 bg-white/95 rounded-2xl shadow-2xl ring-1 ring-black/5 overflow-hidden">
          <div className="p-8 sm:p-10">
            {/* Header */}
            <div className="text-center mb-8">
              <h2 className="text-3xl font-bold tracking-tight text-gray-900">
                Actualice sus datos
              </h2>
              <p className="mt-3 text-base text-gray-600">
                Para completar su registro biométrico, por favor suba su imagen
                frontal, lateral derecho y lateral izquierdo.
              </p>
            </div>

            <form onSubmit={handleSubmit} className="space-y-8">
              {/* Grid de 3 Fotos */}
              <div className="grid grid-cols-1 md:grid-cols-3 gap-6 animate-fadeIn">
                {renderUploadBox("left", "Lateral Izquierdo")}
                {renderUploadBox("front", "Frontal")}
                {renderUploadBox("right", "Lateral Derecho")}
              </div>

              {/* Mensajes de Error */}
              {error && (
                <div className="bg-red-50 border border-red-200 rounded-lg p-3">
                  <p className="text-center text-sm text-red-600 font-medium animate-pulse">
                    {error}
                  </p>
                </div>
              )}

              {/* Botón Enviar */}
              <div className="pt-2 flex justify-center">
                <button
                  type="submit"
                  disabled={isLoading}
                  className="w-full sm:w-1/2 flex justify-center rounded-lg bg-primary px-4 py-3 text-base font-semibold text-white shadow-lg hover:bg-opacity-90 transition-all transform hover:-translate-y-0.5 active:translate-y-0 disabled:opacity-50 disabled:cursor-not-allowed disabled:transform-none"
                >
                  {isLoading ? (
                    <span className="flex items-center gap-2">
                      <svg
                        className="animate-spin h-5 w-5 text-white"
                        xmlns="http://www.w3.org/2000/svg"
                        fill="none"
                        viewBox="0 0 24 24"
                      >
                        <circle
                          className="opacity-25"
                          cx="12"
                          cy="12"
                          r="10"
                          stroke="currentColor"
                          strokeWidth="4"
                        ></circle>
                        <path
                          className="opacity-75"
                          fill="currentColor"
                          d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
                        ></path>
                      </svg>
                      Enviando...
                    </span>
                  ) : (
                    "Enviar Datos"
                  )}
                </button>
              </div>
            </form>

            <div className="mt-6 text-center">
              {/* Opción de Cancelar: Puedes quitarla si es obligatorio */}
              <button
                type="button"
                onClick={() => navigate("/login")} // Si cancela, mejor ir al login que al dashboard bloqueado
                className="text-sm text-gray-500 hover:text-gray-700 hover:underline"
              >
                Cancelar y salir
              </button>
            </div>
          </div>
        </div>
      </div>

      <footer className="absolute bottom-4 right-6 text-xs text-gray-100/80">
        <p>Plataforma desarrollada para la UNSA</p>
      </footer>
    </div>
  );
};

export default UpdateBiometrics;

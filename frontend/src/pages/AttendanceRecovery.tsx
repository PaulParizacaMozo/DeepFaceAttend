import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import Header from "../components/Header";
import api from "../services/api";
import { useAuth } from "../hooks/useAuth";

interface DetectedCourse {
  id: string;
  course_name: string;
  course_code: string;
  semester: string;
}

interface Match {
  id: number;
  course_id: string;
  course_name: string;
  schedule_id: string;
  detected_at: string;
  image_path: string;
  similarity: number;
  resolved: boolean;
  student_id: string | null;
}

interface ApiResponse {
  detected_courses: DetectedCourse[];
  detected_courses_count: number;
  matched_count: number;
  matches: Match[];
  status: string;
  student_id: string;
  threshold: number;
}

const AttendanceRecovery = () => {
  const navigate = useNavigate();
  const { user } = useAuth();

  // --- Estados de Datos (API) ---
  const [apiData, setApiData] = useState<ApiResponse | null>(null);
  const [loadingData, setLoadingData] = useState(true);

  // --- Estados de UI ---
  const [step, setStep] = useState<1 | 2>(1);
  const [selectedCourses, setSelectedCourses] = useState<Set<string>>(
    new Set()
  );
  const [selectedMatchIds, setSelectedMatchIds] = useState<Set<number>>(
    new Set()
  );
  const [isSubmitting, setIsSubmitting] = useState(false);

  useEffect(() => {
    const fetchRecoveryData = async () => {
      if (!user?.id) return;

      try {
        setLoadingData(true);
        const idRes = await api.get(`/students/get-id/${user.id}`);
        const studentId = idRes.data.student_id;

        const response = await api.post("/unknown-faces/resolve", {
          student_id: studentId,
          threshold: 0.3,
        });

        setApiData(response.data);
      } catch (err) {
        console.error("Error cargando datos de recuperación:", err);
        alert(
          "No se pudieron cargar los datos de asistencia. Intente nuevamente."
        );
      } finally {
        setLoadingData(false);
      }
    };

    fetchRecoveryData();
  }, [user]);

  const getImageUrl = (serverPath: string) => {
    if (!serverPath) return "";
    if (serverPath.startsWith("http")) return serverPath;
    const normalizedPath = serverPath.replace(/\\/g, "/");
    const marker = "captures";
    const index = normalizedPath.lastIndexOf(marker);
    if (index !== -1) {
      const relativePath = normalizedPath.substring(index);
      return `http://localhost:5000/${relativePath}`;
    }
    return serverPath;
  };

  // --- PASO 1: Selección de Cursos ---
  const toggleCourse = (courseId: string) => {
    const newSelection = new Set(selectedCourses);
    if (newSelection.has(courseId)) {
      newSelection.delete(courseId);
    } else {
      newSelection.add(courseId);
    }
    setSelectedCourses(newSelection);
  };

  const handleContinue = () => {
    if (selectedCourses.size === 0) {
      alert("Por favor selecciona al menos un curso.");
      return;
    }
    setStep(2);
  };

  // --- PASO 2: Selección de Caras (Matches) ---
  const toggleMatchSelection = (matchId: number, scheduleUniqueKey: string) => {
    if (!apiData) return;

    const newSelection = new Set(selectedMatchIds);

    // 1. Si ya está seleccionada esta cara, la quitamos
    if (newSelection.has(matchId)) {
      newSelection.delete(matchId);
      setSelectedMatchIds(newSelection);
      return;
    }

    // 2. Lógica de Exclusividad: Solo 1 cara por BLOQUE HORARIO
    const matchToSelect = apiData.matches.find((m) => m.id === matchId);

    if (matchToSelect) {
      const dateToSelect = matchToSelect.detected_at.split("T")[0]; // "YYYY-MM-DD"

      apiData.matches.forEach((otherMatch) => {
        const otherDate = otherMatch.detected_at.split("T")[0];
        // Si es el mismo horario Y el mismo día
        if (
          otherMatch.schedule_id === matchToSelect.schedule_id &&
          otherDate === dateToSelect &&
          newSelection.has(otherMatch.id)
        ) {
          newSelection.delete(otherMatch.id);
        }
      });
    }

    // 3. Agregamos la nueva selección
    newSelection.add(matchId);
    setSelectedMatchIds(newSelection);
  };

  const handleSubmit = async () => {
    if (!apiData || selectedMatchIds.size === 0) return;

    setIsSubmitting(true);

    try {
      const studentId = apiData.student_id;

      // 1. Filtrar los objetos match seleccionados
      const selectedMatches = apiData.matches.filter((m) =>
        selectedMatchIds.has(m.id)
      );

      // --- PASO A: MATRÍCULA ---
      const uniqueCourseIds = Array.from(
        new Set(selectedMatches.map((m) => m.course_id))
      );
      await Promise.all(
        uniqueCourseIds.map(async (courseId) => {
          try {
            await api.post("/enrollments", {
              student_id: studentId,
              course_id: courseId,
            });
          } catch (error) {
            console.warn(`Info matrícula ${courseId}:`, error);
          }
        })
      );

      // --- PASO B y C: ASISTENCIA Y RESOLUCIÓN ---
      await Promise.all(
        selectedMatches.map(async (match) => {
          try {
            // 1. Preparar Fecha y Hora
            // match.detected_at viene como "2025-11-30T05:12:25.617364"
            const [datePart, timeFull] = match.detected_at.split("T");
            const timePart = timeFull.split(".")[0];

            // 2. Registrar Asistencia Manual
            await api.post("/attendance/manual", {
              student_id: studentId,
              schedule_id: match.schedule_id,
              date: datePart,
              time: timePart,
            });
          } catch (error: any) {
            if (error.response?.status !== 409) {
              console.error(
                `Error marcando asistencia para match ${match.id}`,
                error
              );
            }
          }

          // 3. Marcar rostro como Resuelto (Resolve Finish)
          try {
            await api.post(`/unknown-faces/${match.id}/resolve-finish`);
          } catch (resolveError) {
            console.error(
              `Error finalizando resolución match ${match.id}`,
              resolveError
            );
          }
        })
      );

      // Éxito
      alert(
        `Se han regularizado exitosamente ${selectedMatchIds.size} registros.`
      );
      navigate("/dashboard");
    } catch (globalError) {
      console.error(
        "Error crítico en el proceso de regularización:",
        globalError
      );
      alert(
        "Ocurrió un error inesperado al procesar. Por favor verifica tu historial de asistencia."
      );
    } finally {
      setIsSubmitting(false);
    }
  };

  const getGroupedMatches = () => {
    if (!apiData) return {};
    const grouped: Record<string, any[]> = {};

    // 1. Filtrar matches de los cursos seleccionados
    const activeMatches = apiData.matches.filter((m) =>
      selectedCourses.has(m.course_id)
    );

    activeMatches.forEach((match) => {
      if (!grouped[match.course_id]) {
        grouped[match.course_id] = [];
      }
      const dateObj = new Date(match.detected_at);
      const dateStr = dateObj.toLocaleDateString();
      const timeStr = dateObj.toLocaleTimeString([], {
        hour: "2-digit",
        minute: "2-digit",
      });
      const groupKey = `${match.schedule_id}_${dateStr}`;
      let group = grouped[match.course_id].find((g) => g.key === groupKey);
      if (!group) {
        group = {
          key: groupKey,
          schedule_id: match.schedule_id,
          date: dateStr,
          schedule_name: `Clase ${timeStr}`,
          matches: [],
        };
        grouped[match.course_id].push(group);
      }
      group.matches.push(match);
    });
    return grouped;
  };
  const groupedData = getGroupedMatches();

  if (loadingData) {
    return (
      <div className="min-h-screen bg-gray-100 flex items-center justify-center">
        <div className="text-center">
          <svg
            className="animate-spin h-10 w-10 text-primary mx-auto mb-4"
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
          <p className="text-gray-600 font-medium">
            Cargando datos de reconocimiento...
          </p>
        </div>
      </div>
    );
  }

  if (!apiData) {
    return (
      <div className="min-h-screen bg-gray-100 flex items-center justify-center">
        <p className="text-red-500">
          Error al cargar datos. Por favor recarga la página.
        </p>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-100">
      <Header
        title="Recuperación de Asistencia"
        showBackButton={true}
        onBack={() => (step === 1 ? navigate("/dashboard") : setStep(1))}
      />

      <main className="max-w-5xl mx-auto py-6 px-4 sm:px-6 lg:px-8">
        {/* Barra de Progreso */}
        <div className="mb-8 flex justify-center items-center">
          <div
            className={`flex items-center gap-2 ${
              step === 1 ? "text-primary font-bold" : "text-gray-500"
            }`}
          >
            <span className="w-8 h-8 rounded-full border-2 flex items-center justify-center border-current">
              1
            </span>
            <span>Cursos</span>
          </div>
          <div className="w-16 h-1 bg-gray-300 mx-4"></div>
          <div
            className={`flex items-center gap-2 ${
              step === 2 ? "text-primary font-bold" : "text-gray-500"
            }`}
          >
            <span className="w-8 h-8 rounded-full border-2 flex items-center justify-center border-current">
              2
            </span>
            <span>Identificación</span>
          </div>
        </div>

        {/* --- PASO 1: SELECCIONAR CURSOS --- */}
        {step === 1 && (
          <div className="animate-fadeIn">
            <h2 className="text-xl font-semibold text-gray-800 mb-4">
              Seleccione los cursos a regularizar
            </h2>
            {apiData.detected_courses.length > 0 ? (
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {apiData.detected_courses.map((course) => {
                  const isSelected = selectedCourses.has(course.id);
                  return (
                    <div
                      key={course.id}
                      onClick={() => toggleCourse(course.id)}
                      className={`cursor-pointer bg-white rounded-xl p-6 shadow-sm border-2 transition-all duration-200 flex flex-col justify-between h-32 ${
                        isSelected
                          ? "border-primary ring-1 ring-primary"
                          : "border-transparent hover:border-gray-300"
                      }`}
                    >
                      <div className="flex justify-between items-start">
                        <div>
                          <h3 className="font-bold text-gray-900">
                            {course.course_name}
                          </h3>
                          <p className="text-sm text-gray-500">
                            {course.course_code}
                          </p>
                        </div>
                        <div
                          className={`w-6 h-6 rounded-full border-2 flex items-center justify-center ${
                            isSelected
                              ? "bg-primary border-primary"
                              : "border-gray-300"
                          }`}
                        >
                          {isSelected && (
                            <svg
                              className="w-4 h-4 text-white"
                              fill="none"
                              viewBox="0 0 24 24"
                              stroke="currentColor"
                            >
                              <path
                                strokeLinecap="round"
                                strokeLinejoin="round"
                                strokeWidth={3}
                                d="M5 13l4 4L19 7"
                              />
                            </svg>
                          )}
                        </div>
                      </div>
                    </div>
                  );
                })}
              </div>
            ) : (
              <div className="text-center py-10 bg-white rounded-lg border border-dashed">
                <p className="text-gray-500">
                  No se encontraron cursos con asistencias pendientes.
                </p>
              </div>
            )}

            <div className="mt-8 flex justify-end">
              <button
                onClick={handleContinue}
                disabled={selectedCourses.size === 0}
                className="bg-primary text-white px-8 py-3 rounded-lg font-semibold shadow-md hover:bg-opacity-90 transition-all disabled:opacity-50 disabled:cursor-not-allowed"
              >
                Continuar
              </button>
            </div>
          </div>
        )}

        {/* --- PASO 2: IDENTIFICACIÓN DE ROSTROS --- */}
        {step === 2 && (
          <div className="animate-fadeIn space-y-8">
            <div className="bg-blue-50 border border-blue-200 p-4 rounded-lg flex gap-3">
              <svg
                xmlns="http://www.w3.org/2000/svg"
                fill="none"
                viewBox="0 0 24 24"
                strokeWidth={1.5}
                stroke="currentColor"
                className="w-6 h-6 text-blue-600 flex-shrink-0"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  d="M11.25 11.25l.041-.02a.75.75 0 011.063.852l-.708 2.836a.75.75 0 001.063.853l.041-.021M21 12a9 9 0 11-18 0 9 9 0 0118 0zm-9-3.75h.008v.008H12V8.25z"
                />
              </svg>
              <div>
                <h3 className="font-bold text-blue-800 text-sm">
                  Instrucciones
                </h3>
                <p className="text-sm text-blue-700">
                  Selecciona tu rostro en cada bloque horario para validar tu
                  asistencia. Los datos están agrupados por curso.
                </p>
              </div>
            </div>

            {Object.keys(groupedData).length > 0 ? (
              // ITERAMOS POR CURSOS (Agrupación)
              Object.entries(groupedData).map(([courseId, scheduleGroups]) => {
                const courseInfo = apiData.detected_courses.find(
                  (c) => c.id === courseId
                );

                return (
                  <div
                    key={courseId}
                    className="bg-white rounded-xl shadow-md overflow-hidden border border-gray-200"
                  >
                    {/* ENCABEZADO DEL CURSO */}
                    <div className="bg-gray-100 px-6 py-4 border-b border-gray-200 flex justify-between items-center">
                      <div>
                        <h2 className="text-xl font-bold text-gray-800">
                          {courseInfo?.course_name || "Curso Desconocido"}
                        </h2>
                        <p className="text-sm text-gray-500 font-medium">
                          Código: {courseInfo?.course_code}
                        </p>
                      </div>
                      <span className="text-xs font-semibold bg-primary/10 text-primary px-3 py-1 rounded-full">
                        {scheduleGroups.reduce(
                          (acc, g) => acc + g.matches.length,
                          0
                        )}{" "}
                        Matches
                      </span>
                    </div>

                    {/* LISTA DE HORARIOS DENTRO DEL CURSO */}
                    <div className="divide-y divide-gray-100">
                      {scheduleGroups.map((group: any) => (
                        <div key={group.key} className="p-6">
                          <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center mb-4 gap-2">
                            <div className="flex items-center gap-2">
                              <div className="bg-primary w-2 h-8 rounded-full"></div>
                              <div>
                                <h3 className="font-bold text-gray-800">
                                  {group.date}
                                </h3>
                                <p className="text-xs text-gray-500">
                                  {group.schedule_name}
                                </p>
                              </div>
                            </div>
                          </div>

                          {/* GRILLA DE CARAS (MATCHES) */}
                          <div className="grid grid-cols-2 sm:grid-cols-4 md:grid-cols-6 gap-4">
                            {group.matches.map((match: Match) => {
                              const isSelected = selectedMatchIds.has(match.id);

                              return (
                                <div
                                  key={match.id}
                                  onClick={() =>
                                    toggleMatchSelection(match.id, group.key)
                                  }
                                  className={`relative aspect-square cursor-pointer rounded-lg overflow-hidden border-2 transition-all duration-200 group ${
                                    isSelected
                                      ? "border-primary ring-2 ring-primary ring-opacity-50"
                                      : "border-gray-100 hover:border-gray-300"
                                  }`}
                                >
                                  {/* IMAGEN DE LA API */}
                                  <img
                                    src={getImageUrl(match.image_path)}
                                    alt="Rostro detectado"
                                    className="w-full h-full object-cover transition-transform duration-300 group-hover:scale-110"
                                    onError={(e) => {
                                      (e.target as HTMLImageElement).src =
                                        "https://via.placeholder.com/150?text=Error+Img";
                                    }}
                                  />

                                  {isSelected && (
                                    <div className="absolute inset-0 bg-primary/40 flex items-center justify-center backdrop-blur-[1px]">
                                      <div className="bg-primary text-white rounded-full p-1 shadow-lg transform scale-110">
                                        <svg
                                          xmlns="http://www.w3.org/2000/svg"
                                          viewBox="0 0 20 20"
                                          fill="currentColor"
                                          className="w-5 h-5"
                                        >
                                          <path
                                            fillRule="evenodd"
                                            d="M16.704 4.153a.75.75 0 01.143 1.052l-8 10.5a.75.75 0 01-1.127.075l-4.5-4.5a.75.75 0 011.06-1.06l3.894 3.893 7.48-9.817a.75.75 0 011.05-.143z"
                                            clipRule="evenodd"
                                          />
                                        </svg>
                                      </div>
                                    </div>
                                  )}
                                </div>
                              );
                            })}
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                );
              })
            ) : (
              <div className="text-center py-12 bg-white rounded-xl border border-dashed border-gray-300">
                <p className="text-gray-500 text-lg">
                  No hay registros pendientes de regularización para los cursos
                  seleccionados.
                </p>
              </div>
            )}

            <div className="mt-8 flex justify-end gap-4">
              <button
                onClick={() => setStep(1)}
                className="px-6 py-3 rounded-lg border border-gray-300 text-gray-700 font-medium hover:bg-gray-50 transition-colors"
              >
                Volver a cursos
              </button>
              <button
                onClick={handleSubmit}
                disabled={isSubmitting || selectedMatchIds.size === 0}
                className="bg-primary text-white px-8 py-3 rounded-lg font-semibold shadow-md hover:bg-opacity-90 transition-all disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
              >
                {isSubmitting ? "Procesando..." : "Enviar Solicitud"}
              </button>
            </div>
          </div>
        )}
      </main>
    </div>
  );
};

export default AttendanceRecovery;

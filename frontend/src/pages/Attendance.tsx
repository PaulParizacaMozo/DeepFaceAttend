import { useEffect, useState, useCallback } from "react";
import { useParams } from "react-router-dom";
import type { Student, Course, AttendanceRecord } from "../types";
import { useAuth } from "../hooks/useAuth";
import { usePolling } from "../hooks/usePolling";
import api from "../services/api";

// Componentes modularizados
import AttendanceHeader from "../components/attendance/AttendanceHeader";
import AttendanceControls from "../components/attendance/AttendanceControls";
import AttendanceTable from "../components/attendance/AttendanceTable";

// Utilidades
import {
  isScheduleActive,
  generateSemesterDates,
} from "../utils/attendanceHelpers";

// --- Componente Principal ---
const Attendance = () => {
  const { courseCode } = useParams<{ courseCode: string }>();
  const { user } = useAuth();

  const [students, setStudents] = useState<Student[]>([]);
  const [course, setCourse] = useState<Course | null>(null);
  const [attendance, setAttendance] = useState<{
    [studentId: string]: { [date: string]: string };
  }>({});
  const [attendanceDates, setAttendanceDates] = useState<string[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [isTakingAttendance, setIsTakingAttendance] = useState(false);
  const [lastUpdate, setLastUpdate] = useState<Date>(new Date());

  // Función para cargar datos de asistencia
  const fetchAttendanceData = useCallback(async (courseId: string) => {
    try {
      const attendanceRes = await api.post("/attendance/search", {
        course_id: courseId,
      });

      const attendanceMap: { [studentId: string]: { [date: string]: string } } =
        {};
      attendanceRes.data.forEach((record: AttendanceRecord) => {
        if (!attendanceMap[record.student_id]) {
          attendanceMap[record.student_id] = {};
        }
        attendanceMap[record.student_id][record.attendance_date] =
          record.status;
      });

      setAttendance(attendanceMap);
      setLastUpdate(new Date());
    } catch (err) {
      console.error("Error fetching attendance data:", err);
      // No mostramos error al usuario para actualizaciones automáticas
    }
  }, []);

  // Función para cargar todos los datos iniciales
  const fetchAllData = useCallback(async () => {
    if (!courseCode) return;

    try {
      setLoading(true);
      const courseRes = await api.get(`/courses/${courseCode}`);
      const courseData = courseRes.data;
      const courseId = courseData.id;

      const [studentsRes, enrollmentsRes] = await Promise.all([
        api.get("/students"),
        api.get("/enrollments"),
      ]);

      const formattedCourse: Course = {
        id: courseData.id,
        title: courseData.course_name,
        code: courseData.course_code,
        schedules: courseData.schedules,
      };

      setCourse(formattedCourse);

      if (formattedCourse.schedules && formattedCourse.schedules.length > 0) {
        const daysOfWeek = formattedCourse.schedules.map((s) => s.day_of_week);
        setAttendanceDates(
          generateSemesterDates("2025-09-01", "2026-01-20", [
            ...new Set(daysOfWeek),
          ])
        );
      }

      const enrollmentsForCourse = enrollmentsRes.data.filter(
        (e: any) => e.course_id === courseId
      );
      const studentIdsForCourse = new Set(
        enrollmentsForCourse.map((e: any) => e.student_id)
      );
      setStudents(
        studentsRes.data.filter((s: Student) => studentIdsForCourse.has(s.id))
      );

      // Cargar datos de asistencia inicial
      await fetchAttendanceData(courseId);
      setError(null);
    } catch (err) {
      console.error("Error fetching data:", err);
      setError("No se pudo cargar la información.");
    } finally {
      setLoading(false);
    }
  }, [courseCode, fetchAttendanceData]);

  // Efecto para carga inicial
  useEffect(() => {
    fetchAllData();
  }, [fetchAllData]);

  // Configurar polling para actualizaciones automáticas
  const pollingCallback = useCallback(async () => {
    if (course?.id) {
      await fetchAttendanceData(course.id);
    }
  }, [course?.id, fetchAttendanceData]);

  usePolling(
    pollingCallback,
    10000, // 10 segundos
    !!course?.id // Solo habilitar si hay un curso cargado
  );

  const handleTakeAttendance = async () => {
    const activeSchedule = course?.schedules?.find(isScheduleActive);
    if (!activeSchedule) {
      alert("No hay una clase en sesión en este momento.");
      return;
    }

    setIsTakingAttendance(true);
    try {
      const response = await api.post(
        `/schedules/${activeSchedule.id}/start-attendance`
      );
      alert(response.data.message);

      // Actualizar inmediatamente después de tomar asistencia
      if (course?.id) {
        await fetchAttendanceData(course.id);
      }
    } catch (err: any) {
      const errorMessage = err.response?.data?.message || "Ocurrió un error.";
      alert(`Error: ${errorMessage}`);
    } finally {
      setIsTakingAttendance(false);
    }
  };

  const activeSchedule = course?.schedules?.find(isScheduleActive);

  return (
    <div className="min-h-screen bg-gray-100 pb-12">
      <AttendanceHeader courseTitle={course?.title || "Cargando..."} />
      {/* Agrega padding top para version mobile y web */}
      <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pt-36 sm:pt-28 lg:pt-24">
        {/* Indicador de actualización automática */}
        <div className="text-sm text-gray-500 mb-2 text-center">
          <div className="inline-flex items-center gap-2 bg-green-50 px-3 py-1 rounded-full">
            <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
            <span>Actualización automática activa</span>
            <span className="text-gray-400">•</span>
            <span>Última actualización: {lastUpdate.toLocaleTimeString()}</span>
          </div>
        </div>

        {user && course && (
          <AttendanceControls
            course={course}
            students={students}
            attendanceDates={attendanceDates}
            attendance={attendance}
            user={user}
            loading={loading}
            activeSchedule={activeSchedule}
            isTakingAttendance={isTakingAttendance}
            onTakeAttendance={handleTakeAttendance}
          />
        )}

        <div className="bg-white rounded-2xl shadow-lg overflow-hidden">
          <AttendanceTable
            students={students}
            attendanceDates={attendanceDates}
            attendance={attendance}
            loading={loading}
            error={error}
          />
        </div>
      </main>
    </div>
  );
};

export default Attendance;

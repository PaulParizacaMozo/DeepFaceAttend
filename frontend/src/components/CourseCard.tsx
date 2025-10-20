import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import type { Course, Schedule } from '../types';
import api from '../services/api';

interface CourseCardProps {
  course: Course;
  userRole?: 'student' | 'teacher';
}

// Función de utilidad para verificar si un horario está activo
const isScheduleActive = (schedule: Schedule): boolean => {
  const now = new Date();
  const dayMap = [7, 1, 2, 3, 4, 5, 6]; // Mapea getDay() (Dom=0) a nuestro formato (Lun=1)
  const currentDay = dayMap[now.getDay()];
  
  if (schedule.day_of_week !== currentDay) return false;

  const [startHour, startMinute] = schedule.start_time.split(':').map(Number);
  const [endHour, endMinute] = schedule.end_time.split(':').map(Number);

  const startTime = new Date();
  startTime.setHours(startHour, startMinute, 0, 0);

  const endTime = new Date();
  endTime.setHours(endHour, endMinute, 0, 0);

  return now >= startTime && now <= endTime;
};

const dayNames: { [key: number]: string } = { 1: 'Lun', 2: 'Mar', 3: 'Mié', 4: 'Jue', 5: 'Vie', 6: 'Sáb', 7: 'Dom' };

const CourseCard = ({ course, userRole }: CourseCardProps) => {
  const navigate = useNavigate();
  const [loadingStates, setLoadingStates] = useState<{ [key: string]: boolean }>({});
  // Estado para forzar la re-renderización cada minuto y actualizar el estado del botón
  const [, setTime] = useState(new Date());

  useEffect(() => {
    // Este efecto actualiza el componente cada minuto para que el botón
    // "Iniciar" aparezca o desaparezca en tiempo real según la hora.
    const timer = setInterval(() => setTime(new Date()), 60000); 
    return () => clearInterval(timer);
  }, []);

  const handleStartAttendance = async (scheduleId: string) => {
    setLoadingStates(prev => ({ ...prev, [scheduleId]: true }));
    try {
      const response = await api.post(`/schedules/${scheduleId}/start-attendance`);
      alert(response.data.message);
    } catch (err: any) {
      const errorMessage = err.response?.data?.message || err.response?.data?.error || "Ocurrió un error.";
      alert(`Error: ${errorMessage}`);
    } finally {
      setLoadingStates(prev => ({ ...prev, [scheduleId]: false }));
    }
  };

  return (
    <div className="bg-white rounded-2xl shadow-lg p-6 flex flex-col justify-between">
      <div>
        <h3 className="text-xl font-bold text-gray-800 mb-2">{course.title}</h3>
        <p className="text-sm text-gray-500 font-mono mb-4">{course.code}</p>

        {/* Sección de Horarios solo visible para Profesores */}
        {userRole === 'teacher' && course.schedules && (
          <div className="space-y-3 mb-4">
            <h4 className="font-semibold text-gray-600 text-sm border-b pb-2 mb-2">Horarios:</h4>
            {course.schedules.map(schedule => {
              const isActive = isScheduleActive(schedule);
              return (
                <div key={schedule.id} className="flex justify-between items-center bg-gray-50 p-2 rounded-lg">
                  <div>
                    <p className="font-medium text-gray-800">
                      {dayNames[schedule.day_of_week]}: {schedule.start_time.slice(0, 5)} - {schedule.end_time.slice(0, 5)}
                    </p>
                    <p className="text-xs text-gray-500">{schedule.location}</p>
                  </div>
                  {isActive && (
                    <button
                      className="bg-green-600 text-white text-xs font-bold py-2 px-3 rounded-lg hover:bg-green-700 transition-colors disabled:bg-gray-400"
                      onClick={() => handleStartAttendance(schedule.id)}
                      disabled={loadingStates[schedule.id]}
                    >
                      {loadingStates[schedule.id] ? 'Iniciando...' : 'Iniciar'}
                    </button>
                  )}
                </div>
              );
            })}
          </div>
        )}
      </div>

      <button
        className="w-full bg-primary text-white font-semibold py-2 px-4 rounded-lg hover:bg-opacity-90 transition-colors mt-2"
        onClick={() => navigate(`/attendance/${course.code}`)}
      >
        Ver Registro de Asistencia
      </button>
    </div>
  );
};

export default CourseCard;
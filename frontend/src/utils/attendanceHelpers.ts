import type { Schedule } from "../types";


// --- Funciones de utilidad implementadas localmente ---
export const isScheduleActive = (schedule: Schedule): boolean => {
  const now = new Date();
  const dayMap = [7, 1, 2, 3, 4, 5, 6]; // Domingo=7, Lunes=1, ..., Sábado=6
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

export const generateSemesterDates = (start: string, end: string, daysOfWeek: number[]): string[] => {
  const dates: string[] = [];
  const currentDate = new Date(`${start}T00:00:00Z`);
  const endDate = new Date(`${end}T00:00:00Z`);
  
  while (currentDate <= endDate) {
    const day = currentDate.getUTCDay() === 0 ? 7 : currentDate.getUTCDay();
    if (daysOfWeek.includes(day)) {
      dates.push(currentDate.toISOString().split('T')[0]);
    }
    currentDate.setUTCDate(currentDate.getUTCDate() + 1);
  }
  
  return dates;
};

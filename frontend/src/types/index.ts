export interface Schedule {
  id: string;
  day_of_week: number;
  start_time: string;
  end_time: string;
  location: string;
}

export interface Course {
  id: string;
  title: string; // course_name en el backend
  code: string;  // course_code en el backend
  schedules?: Schedule[];
}

export interface Student {
  id: string;
  cui: string;
  first_name: string;
  last_name: string;
  filepath_embeddings: string;
}

export interface AttendanceRecord {
  id: string;
  student_id: string;
  course_id: string;
  attendance_date: string; // Formato 'YYYY-MM-DD'
  status: 'presente' | 'tarde' | 'ausente';
}

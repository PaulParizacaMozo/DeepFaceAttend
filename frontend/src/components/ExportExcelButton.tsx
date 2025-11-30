import * as XLSX from 'xlsx';
import type { Student, Course } from '../types';


// Definimos un tipo simple para el usuario
type User = {
  first_name: string;
  last_name: string;
} | null;

interface ExportExcelButtonProps {
  course: Course | null;
  students: Student[];
  attendanceDates: string[];
  attendance: { [studentId: string]: { [date: string]: string } };
  user: User; // Lo mantenemos por consistencia, aunque no se usa aquí
  loading: boolean;
}

// Mapeo de meses (puedes moverlo a un archivo utils/dates.ts)
const monthAbbreviations: { [key: string]: string } = {
  '01': 'ene', '02': 'feb', '03': 'mar', '04': 'abr',
  '05': 'may', '06': 'jun', '07': 'jul', '08': 'ago',
  '09': 'sep', '10': 'oct', '11': 'nov', '12': 'dic',
};

const ExportExcelButton = ({ course, students, attendanceDates, attendance, loading }: ExportExcelButtonProps) => {

  const handleDownloadExcel = () => {
    if (!course || !students.length) return;

    // 1. Preparar la Cabecera (Head)
    // Usamos un formato "dd/mmm" para las fechas, ej: "05/sep"
    const headDates = attendanceDates.map(date => {
      const [_, month, day] = date.split('-');
      return `${day}/${monthAbbreviations[month]}`;
    });
    const header = ['CUI', 'Apellidos y Nombres', ...headDates];

    // 2. Preparar el Cuerpo (Body)
    const body = students.map(student => {
      const studentAttendance = attendance[student.id] || {};
      const attendanceRow = attendanceDates.map(date => {
        const status = studentAttendance[date];
        if (status === 'presente') return 'P';
        if (status === 'tarde') return 'T';
        if (status === 'ausente') return 'A';
        return '-';
      });
      return [
        student.cui,
        `${student.last_name}, ${student.first_name}`,
        ...attendanceRow
      ];
    });

    // 3. Combinar cabecera y cuerpo
    const dataToExport = [header, ...body];

    // 4. Crear la Hoja de Cálculo (Worksheet)
    const ws = XLSX.utils.aoa_to_sheet(dataToExport);

    // 5. (Opcional pero recomendado) Definir anchos de columna
    const colWidths = [
      { wch: 15 }, // CUI
      { wch: 30 }, // Apellidos y Nombres
      // Ajustar todas las columnas de fecha a un ancho de 5
      ...headDates.map(() => ({ wch: 5 }))
    ];
    ws['!cols'] = colWidths;

    // 6. Crear el Libro (Workbook) y añadir la hoja
    const wb = XLSX.utils.book_new();
    XLSX.utils.book_append_sheet(wb, ws, 'Asistencia');

    // 7. Generar y descargar el archivo
    const fileName = `Asistencia_${course.code}_${new Date().toISOString().split('T')[0]}.xlsx`;
    XLSX.writeFile(wb, fileName);
  };

  return (
    <button
      onClick={handleDownloadExcel}
      disabled={loading}
      className="bg-primary-light text-white font-semibold py-2 px-5 rounded-lg hover:bg-primary-light disabled:bg-gray-400 cursor-pointer scale-95 hover:scale-100 transition-transform"
    >
      Descargar Excel
    </button>
  );
};

export default ExportExcelButton;
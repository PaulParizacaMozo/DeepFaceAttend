import jsPDF from 'jspdf';
import autoTable from 'jspdf-autotable';
import type { Student, Course } from '../types';

// Definimos un tipo simple para el usuario, basado en lo que usamos
type User = {
  first_name: string;
  last_name: string;
} | null;

interface ExportPDFButtonProps {
  course: Course | null;
  students: Student[];
  attendanceDates: string[];
  attendance: { [studentId: string]: { [date: string]: string } };
  user: User;
  loading: boolean;
}

const ExportPDFButton = ({ course, students, attendanceDates, attendance, user, loading }: ExportPDFButtonProps) => {

  const handleDownloadPDF = () => {
    if (!course || !students.length) return;

    // 1. Inicializar el documento PDF en vertical (retrato)
    const doc = new jsPDF({ orientation: 'portrait' });

    // 2. Título principal y Metadatos
    doc.setFontSize(16);
    doc.text(`Registro de Asistencia: ${course.title}`, 14, 17);
    doc.setFontSize(10);
    doc.text(`Profesor: ${user?.first_name} ${user?.last_name}`, 14, 23);
    doc.text(`Fecha de descarga: ${new Date().toLocaleDateString()}`, doc.internal.pageSize.width - 14, 23, { align: 'right' });

    // 3. Agrupar las fechas por mes
    const datesByMonth = attendanceDates.reduce((acc, date) => {
      const monthKey = date.substring(0, 7); // "2025-09"
      if (!acc[monthKey]) {
        acc[monthKey] = [];
      }
      acc[monthKey].push(date);
      return acc;
    }, {} as { [key: string]: string[] });

    let startY = 35; // Posición vertical inicial para la primera tabla

    // 4. Iterar sobre cada mes y crear una tabla
    for (const monthKey of Object.keys(datesByMonth).sort()) {
      const monthDates = datesByMonth[monthKey];
      
      // Formatear el título del mes (ej. "Septiembre 2025")
      const monthDate = new Date(`${monthKey}-02T00:00:00Z`); // Usar día 2 para evitar problemas de zona horaria
      const monthName = monthDate.toLocaleDateString('es-ES', { month: 'long', year: 'numeric', timeZone: 'UTC' });
      const capitalizedMonthName = monthName.charAt(0).toUpperCase() + monthName.slice(1);

      // Revisar si la tabla cabe en la página actual, si no, agregar una nueva
      if (startY > doc.internal.pageSize.height - 40) { // Margen inferior de 40
        doc.addPage();
        startY = 20; // Resetear Y en la nueva página
      }

      // Dibujar el título del mes
      doc.setFontSize(12);
      doc.setFont('helvetica', 'bold');
      doc.text(capitalizedMonthName, 14, startY);
      startY += 8; // Espacio después del título del mes

      // 5. Preparar Cabecera (Head) para este mes (solo días)
      const headDates = monthDates.map(date => date.split('-')[2]); // "01", "02", etc.
      const head = [['CUI', 'Apellidos y Nombres', ...headDates]];

      // 6. Preparar Cuerpo (Body) para este mes
      const body = students.map(student => {
        const studentAttendance = attendance[student.id] || {};
        const attendanceRow = monthDates.map(date => {
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

      // 7. Estilos de columna para este mes
      const dateColumnStyles: { [key: number]: any } = {};
      monthDates.forEach((_, index) => {
        dateColumnStyles[index + 2] = { halign: 'center', cellWidth: 8 }; // Ancho fijo de 8
      });

      // 8. Generar la tabla del mes
      autoTable(doc, {
        head: head,
        body: body,
        startY: startY, // Posición de inicio de esta tabla
        styles: { fontSize: 8, cellPadding: 1.5, overflow: 'linebreak' },
        headStyles: {
          fillColor: [45, 52, 54],
          textColor: 255,
          fontStyle: 'bold',
          halign: 'center',
        },
        columnStyles: {
          0: { cellWidth: 20, fontStyle: 'bold' },
          1: { cellWidth: 45 },
          ...dateColumnStyles,
        },
        didDrawCell: (data) => {
          if (data.section === 'body') {
            const cellText = data.cell.text[0];
            let color = [0, 0, 0]; // default (negro)
            if (cellText === 'P') color = [39, 174, 96]; // verde
            if (cellText === 'T') color = [243, 156, 18]; // amarillo
            if (cellText === 'A') color = [192, 57, 43]; // rojo
            if (cellText === '-') color = [149, 165, 166]; // gris
            doc.setTextColor(color[0], color[1], color[2]);
          }
        }
      });

      // 9. Actualizar la posición Y para la siguiente tabla
      startY = (doc as any).lastAutoTable.finalY + 15; // 15 de espacio entre tablas
    }

    // 10. Abrir el PDF en una nueva pestaña
    doc.output('dataurlnewwindow');
  };

  return (
    <button
      onClick={handleDownloadPDF}
      disabled={loading}
      className="bg-primary text-white font-semibold py-2 px-5 rounded-lg hover:bg-primary disabled:bg-gray-400 cursor-pointer scale-95 hover:scale-100 transition-transform"
    >
      Descargar PDF
    </button>
  );
};

export default ExportPDFButton;
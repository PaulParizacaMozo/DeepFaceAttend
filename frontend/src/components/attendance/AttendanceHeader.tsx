import { useNavigate } from 'react-router-dom';
import Header from '../Header';

interface AttendanceHeaderProps {
  courseTitle: string;
}

const AttendanceHeader = ({ courseTitle }: AttendanceHeaderProps) => {
  const navigate = useNavigate();
  
  return (
    <Header
      title={`Asistencia - ${courseTitle}`}
      showBackButton
      onBack={() => navigate('/dashboard')}
    />
  );
};

export default AttendanceHeader;
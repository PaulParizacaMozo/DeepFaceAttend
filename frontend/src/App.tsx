import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider } from './contexts/AuthContext';
import Login from './pages/Login';
import Register from './pages/Register';
import Dashboard from './pages/Dashboard';
import Attendance from './pages/Attendance';
import AttendanceStudent from './pages/AttendanceStudent.tsx';
import EditAttendance from './pages/EditAttendance'; 
import ProtectedRoute from './components/ProtectedRoute';

function App() {
  return (
    <Router>
      <AuthProvider>
        <Routes>
          <Route path="/login" element={<Login />} />
          <Route path="/register" element={<Register />} />
          
          <Route
            path="/dashboard"
            element={
              <ProtectedRoute>
                <Dashboard />
              </ProtectedRoute>
            }
          />

          {/* Ruta del Profesor: Ver/Tomar Asistencia */}
          <Route 
            path="/attendance/:courseCode" 
            element={<ProtectedRoute><Attendance /></ProtectedRoute>} 
          />

          {/* --- 2. AÑADIR RUTA: Editar Asistencia (Profesor) --- */}
          <Route 
            path="/attendance/:courseCode/edit" 
            element={<ProtectedRoute><EditAttendance /></ProtectedRoute>} 
          />
          
          {/* Ruta del Estudiante */}
          <Route 
            path="/my-attendance/:courseCode" 
            element={<ProtectedRoute><AttendanceStudent /></ProtectedRoute>} 
          />

          <Route
            path="/course/:courseId"
            element={<Navigate to="/dashboard" />}
          />

          {/* Redirección por defecto */}
          <Route path="*" element={<Navigate to="/login" />} />
        </Routes>
      </AuthProvider>
    </Router>
  );
}

export default App;
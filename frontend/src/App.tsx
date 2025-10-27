import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { AuthProvider } from './contexts/AuthContext';
import Login from './pages/Login';
import Register from './pages/Register';
import Dashboard from './pages/Dashboard';
import Attendance from './pages/Attendance';
import AttendanceStudent from './pages/AttendanceStudent.tsx';
import ProtectedRoute from './components/ProtectedRoute';
// import 'App.css';

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

          {/* Ruta del Profesor */}
          <Route 
            path="/attendance/:courseCode" 
            element={<ProtectedRoute><Attendance /></ProtectedRoute>} 
          />
          
          {/* --- 2. Añade la nueva ruta del Estudiante --- */}
          <Route 
            path="/my-attendance/:courseCode" 
            element={<ProtectedRoute><AttendanceStudent /></ProtectedRoute>} 
          />

          {/* <Route
            path="/course/:courseId"
            element={
              <ProtectedRoute>
                <Attendance />
              </ProtectedRoute>
            }
          /> */}

          {/* Redirige esta ruta antigua por si acaso */}
          <Route
            path="/course/:courseId"
            element={<Navigate to="/dashboard" />}
          />

          {/* <Route path="/attendance/:courseCode" element={<Attendance />} /> */}
          {/* Redirección por defecto a la página de login si no hay ruta */}
          <Route path="*" element={<Navigate to="/login" />} />
        </Routes>
      </AuthProvider>
    </Router>
  );
}

export default App;

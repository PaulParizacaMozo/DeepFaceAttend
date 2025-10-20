// src/pages/Register.tsx
import { useState, type FormEvent } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import api from '../services/api';
import unsaBgURL from '../assets/unsa_bg2.avif';

const Register = () => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [firstName, setFirstName] = useState('');
  const [lastName, setLastName] = useState('');
  const [role, setRole] = useState<'student' | 'teacher'>('student');
  const [cui, setCui] = useState('');
  
  const [error, setError] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const navigate = useNavigate();

  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    setError('');
    setIsLoading(true);

    const payload = {
      email,
      password,
      first_name: firstName,
      last_name: lastName,
      role,
      ...(role === 'student' && { cui }),
    };
    
    try {
      await api.post('/auth/register', payload);
      alert('¡Registro exitoso! Ahora puedes iniciar sesión.');
      navigate('/login');
    } catch (err: any) {
      const errorMessage = err.response?.data?.message || 'Error en el registro. Verifica tus datos.';
      setError(errorMessage);
    } finally {
      setIsLoading(false);
    }
  };

  const inputStyles = "block w-full appearance-none rounded-lg border border-gray-300 px-3 py-2.5 placeholder-gray-400 shadow-sm focus:border-primary focus:outline-none focus:ring-primary sm:text-sm";
  const labelStyles = "block text-sm font-medium text-gray-700";

  return (
    <div className="relative min-h-screen w-full">
      {/* Capas de fondo idénticas a Login */}
      <div className="absolute inset-0 bg-cover bg-center" style={{ backgroundImage: `url(${unsaBgURL})` }}></div>
      <div className="absolute inset-0 bg-gray-400/60 backdrop-blur-sm"></div>

      <div className="relative flex min-h-screen items-center justify-center p-4">
        <div className="w-full max-w-md space-y-6 rounded-2xl bg-white/90 p-6 shadow-2xl ring-1 ring-black/5 sm:p-10">
          <div className="text-center">
            <h2 className="text-3xl font-bold tracking-tight text-gray-900">Crear una Cuenta</h2>
            <p className="mt-2 text-sm text-gray-600">Ingresa tus datos para registrarte</p>
          </div>

          <form className="space-y-4" onSubmit={handleSubmit}>
            <div className="flex flex-col gap-4 sm:flex-row">
              <div className="w-full sm:w-1/2">
                <label htmlFor="first-name" className={labelStyles}>Nombres</label>
                <div className="mt-1"><input id="first-name" type="text" required value={firstName} onChange={(e) => setFirstName(e.target.value)} className={inputStyles} placeholder="Juan"/></div>
              </div>
              <div className="w-full sm:w-1/2">
                <label htmlFor="last-name" className={labelStyles}>Apellidos</label>
                <div className="mt-1"><input id="last-name" type="text" required value={lastName} onChange={(e) => setLastName(e.target.value)} className={inputStyles} placeholder="Perez"/></div>
              </div>
            </div>
            
            <div>
              <label htmlFor="email-address" className={labelStyles}>Correo Electrónico</label>
              <div className="mt-1"><input id="email-address" type="email" required value={email} onChange={(e) => setEmail(e.target.value)} className={inputStyles} placeholder="ejemplo@unsa.edu.pe"/></div>
            </div>
            <div>
              <label htmlFor="password" className={labelStyles}>Contraseña</label>
              <div className="mt-1"><input id="password" type="password" required value={password} onChange={(e) => setPassword(e.target.value)} className={inputStyles} placeholder="••••••••"/></div>
            </div>

            <div>
              <label className={labelStyles}>Soy</label>
              <div className="mt-2 flex items-center space-x-6">
                <label className="flex items-center text-sm font-medium text-gray-700 cursor-pointer">
                  <input type="radio" name="role" value="student" checked={role === 'student'} onChange={() => setRole('student')} className="h-4 w-4 text-primary focus:ring-primary border-gray-300"/>
                  <span className="ml-2">Estudiante</span>
                </label>
                <label className="flex items-center text-sm font-medium text-gray-700 cursor-pointer">
                  <input type="radio" name="role" value="teacher" checked={role === 'teacher'} onChange={() => setRole('teacher')} className="h-4 w-4 text-primary focus:ring-primary border-gray-300"/>
                  <span className="ml-2">Profesor</span>
                </label>
              </div>
            </div>
            
            {role === 'student' && (
              <div>
                <label htmlFor="cui" className={labelStyles}>CUI</label>
                <div className="mt-1"><input id="cui" type="text" required={role === 'student'} value={cui} onChange={(e) => setCui(e.target.value)} className={inputStyles} placeholder="20201234"/></div>
              </div>
            )}
            
            {error && <p className="text-center text-sm text-red-600">{error}</p>}

            <div>
              <button type="submit" disabled={isLoading} className="flex w-full justify-center rounded-lg bg-primary px-4 py-2.5 text-sm font-semibold text-white shadow-sm transition-colors hover:bg-opacity-90 focus:outline-none focus:ring-2 focus:ring-primary focus:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50">
                {isLoading ? 'Registrando...' : 'Crear Cuenta'}
              </button>
            </div>
          </form>

          <p className="text-center text-sm text-gray-600">
            ¿Ya tienes una cuenta?{' '}
            <Link to="/login" className="font-medium text-primary hover:underline">
              Inicia sesión
            </Link>
          </p>
        </div>
      </div>

       <footer className="absolute bottom-4 right-6 text-xs text-gray-100/80">
        <p>Plataforma desarrollada para la UNSA</p>
      </footer>
    </div>
  );
};

export default Register;
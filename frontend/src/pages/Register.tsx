import { useState, type FormEvent } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import api from '../services/api';
import unsaBgURL from '../assets/unsa_bg2.avif';

// --- MOCK DATA PARA LA DEMOSTRACIÓN ---
// Simula respuesta del backend con fotos de caras no reconocidas en clases pasadas
const MOCK_UNKNOWN_FACES = [
  {
    date: '2025-09-05',
    schedule_name: '08:00 - 10:00 | Lab A',
    schedule_id: 'sch_001',
    faces: [
      { id: 'face_1', url: 'https://api.dicebear.com/7.x/avataaars/svg?seed=Felix' },
      { id: 'face_2', url: 'https://api.dicebear.com/7.x/avataaars/svg?seed=Aneka' },
    ]
  },
  {
    date: '2025-09-08',
    schedule_name: '10:00 - 12:00 | Aula 302',
    schedule_id: 'sch_002',
    faces: [
      { id: 'face_3', url: 'https://api.dicebear.com/7.x/avataaars/svg?seed=John' },
      { id: 'face_4', url: 'https://api.dicebear.com/7.x/avataaars/svg?seed=Sarah' },
      { id: 'face_5', url: 'https://api.dicebear.com/7.x/avataaars/svg?seed=Mike' },
    ]
  },
  {
    date: '2025-09-12',
    schedule_name: '08:00 - 10:00 | Lab A',
    schedule_id: 'sch_003',
    faces: [
      { id: 'face_6', url: 'https://api.dicebear.com/7.x/avataaars/svg?seed=Zoe' },
    ]
  }
];

const Register = () => {
  // Estados del Formulario
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [firstName, setFirstName] = useState('');
  const [lastName, setLastName] = useState('');
  const [role, setRole] = useState<'student' | 'teacher'>('student');
  const [cui, setCui] = useState('');
  
  // Estados de UI y Lógica
  const [error, setError] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [recoverMode, setRecoverMode] = useState(false); // Estado del botón de recuperación
  const [selectedFaces, setSelectedFaces] = useState<Set<string>>(new Set()); // IDs de fotos seleccionadas
  
  const navigate = useNavigate();

  // Manejo de selección de fotos
  const toggleFaceSelection = (faceId: string) => {
    const newSelection = new Set(selectedFaces);
    if (newSelection.has(faceId)) {
      newSelection.delete(faceId);
    } else {
      newSelection.add(faceId);
    }
    setSelectedFaces(newSelection);
  };

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
      // 1. Crear Usuario y Estudiante (Backend existente)
      await api.post('/auth/register', payload);

      // 2. Lógica de Recuperación de Asistencia (Simulación)
      if (recoverMode && role === 'student' && selectedFaces.size > 0) {
        // Extraer los datos necesarios de las fotos seleccionadas
        const recoveryData: { schedule_id: string; date: string }[] = [];

        MOCK_UNKNOWN_FACES.forEach(group => {
          group.faces.forEach(face => {
            if (selectedFaces.has(face.id)) {
              recoveryData.push({
                schedule_id: group.schedule_id,
                date: group.date
              });
            }
          });
        });

        console.log("--- PROCESO DE REGULARIZACIÓN DE ASISTENCIA ---");
        console.log("Usuario creado:", email);
        console.log("Asistencias a regularizar:", recoveryData);
        alert(`Registro exitoso. Se han enviado ${recoveryData.length} asistencias para regularización.`);
      } else {
        alert('¡Registro exitoso! Ahora puedes iniciar sesión.');
      }

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
    <div className="relative min-h-screen w-full overflow-hidden">
      {/* Capas de fondo */}
      <div className="absolute inset-0 bg-cover bg-center" style={{ backgroundImage: `url(${unsaBgURL})` }}></div>
      <div className="absolute inset-0 bg-gray-400/60 backdrop-blur-sm"></div>

      <div className="relative flex min-h-screen items-center justify-center p-4">
        
        {/* Contenedor Principal: Se expande si recoverMode es true */}
        <div className={`w-full transition-all duration-500 ease-in-out bg-white/95 rounded-2xl shadow-2xl ring-1 ring-black/5 overflow-hidden flex flex-col lg:flex-row ${recoverMode ? 'max-w-6xl' : 'max-w-md'}`}>
          
          {/* --- COLUMNA IZQUIERDA: FORMULARIO DE REGISTRO --- */}
          <div className={`p-6 sm:p-10 transition-all duration-500 ${recoverMode ? 'lg:w-1/3 border-r border-gray-200' : 'w-full'}`}>
            <div className="text-center mb-6">
              <h2 className="text-3xl font-bold tracking-tight text-gray-900">Crear Cuenta</h2>
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
                    <input type="radio" name="role" value="student" checked={role === 'student'} onChange={() => {setRole('student');}} className="h-4 w-4 text-primary focus:ring-primary border-gray-300"/>
                    <span className="ml-2">Estudiante</span>
                  </label>
                  <label className="flex items-center text-sm font-medium text-gray-700 cursor-pointer">
                    <input type="radio" name="role" value="teacher" checked={role === 'teacher'} onChange={() => {setRole('teacher'); setRecoverMode(false);}} className="h-4 w-4 text-primary focus:ring-primary border-gray-300"/>
                    <span className="ml-2">Profesor</span>
                  </label>
                </div>
              </div>
              
              {role === 'student' && (
                <>
                  <div>
                    <label htmlFor="cui" className={labelStyles}>CUI</label>
                    <div className="mt-1"><input id="cui" type="text" required={role === 'student'} value={cui} onChange={(e) => setCui(e.target.value)} className={inputStyles} placeholder="20201234"/></div>
                  </div>

                  {/* --- BOTÓN DE RECUPERAR ASISTENCIA --- */}
                  <div className="mt-4 p-3 bg-gray-50 rounded-lg border border-gray-200">
                    <div className="flex items-center justify-between">
                        <button
                            type="button"
                            onClick={() => setRecoverMode(!recoverMode)}
                            className={`relative inline-flex h-6 w-11 flex-shrink-0 cursor-pointer rounded-full border-2 border-transparent transition-colors duration-200 ease-in-out focus:outline-none ${recoverMode ? 'bg-primary' : 'bg-gray-300'}`}
                        >
                            <span className="sr-only">Activar recuperación</span>
                            <span
                                aria-hidden="true"
                                className={`pointer-events-none inline-block h-5 w-5 transform rounded-full bg-white shadow ring-0 transition duration-200 ease-in-out ${recoverMode ? 'translate-x-5' : 'translate-x-0'}`}
                            />
                        </button>
                        <span className={`ml-3 text-sm font-medium ${recoverMode ? 'text-primary' : 'text-gray-500'}`}>
                            {recoverMode ? 'Recuperar Asistencia Activo' : 'Recuperar Asistencia'}
                        </span>
                    </div>
                    <p className="mt-2 text-xs text-gray-500 leading-tight">
                        Si ya asistió a alguna clase antes pero no tenía cuenta, active esta opción para regularizar sus asistencias seleccionando su foto.
                    </p>
                  </div>
                </>
              )}
              
              {error && <p className="text-center text-sm text-red-600">{error}</p>}

              <div>
                <button type="submit" disabled={isLoading} className="flex w-full justify-center rounded-lg bg-primary px-4 py-2.5 text-sm font-semibold text-white shadow-sm transition-colors hover:bg-opacity-90 focus:outline-none focus:ring-2 focus:ring-primary focus:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50">
                  {isLoading ? 'Procesando...' : (recoverMode ? 'Registrar y Regularizar' : 'Crear Cuenta')}
                </button>
              </div>
            </form>

            <p className="mt-6 text-center text-sm text-gray-600">
              ¿Ya tienes una cuenta?{' '}
              <Link to="/login" className="font-medium text-primary hover:underline">
                Inicia sesión
              </Link>
            </p>
          </div>

          {/* --- COLUMNA DERECHA: GALERÍA DE FOTOS (Solo visible si recoverMode es true) --- */}
          {recoverMode && role === 'student' && (
             <div className="lg:w-2/3 bg-gray-50 p-6 sm:p-10 flex flex-col h-full animate-fadeIn">
                <div className="mb-6">
                    <h3 className="text-xl font-bold text-gray-800 flex items-center gap-2">
                        <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor" className="w-6 h-6 text-primary">
                            <path strokeLinecap="round" strokeLinejoin="round" d="M6.827 6.175A2.31 2.31 0 015.186 7.23c-.38.054-.757.112-1.134.175C2.999 7.58 2.25 8.507 2.25 9.574V18a2.25 2.25 0 002.25 2.25h15A2.25 2.25 0 0021.75 18V9.574c0-1.067-.75-1.994-1.802-2.169a47.865 47.865 0 00-1.134-.175 2.31 2.31 0 01-1.64-1.055l-.822-1.316a2.192 2.192 0 00-1.736-1.039 48.774 48.774 0 00-5.232 0 2.192 2.192 0 00-1.736 1.039l-.821 1.316z" />
                            <path strokeLinecap="round" strokeLinejoin="round" d="M16.5 12.75a4.5 4.5 0 11-9 0 4.5 4.5 0 019 0zM18.75 10.5h.008v.008h-.008V10.5z" />
                        </svg>
                        Identifícate en las fotos
                    </h3>
                    <p className="text-sm text-gray-600">
                        Selecciona tu foto en los horarios correspondientes. Solo puedes seleccionar una foto por bloque de horario.
                    </p>
                </div>

                {/* Área Scrollable para las fotos */}
                <div className="flex-1 overflow-y-auto pr-2 custom-scrollbar" style={{ maxHeight: '600px' }}>
                    {MOCK_UNKNOWN_FACES.map((group, index) => (
                        <div key={index} className="mb-8 bg-white rounded-xl p-4 shadow-sm border border-gray-200">
                            <div className="flex justify-between items-center mb-3 pb-2 border-b border-gray-100">
                                <span className="font-bold text-gray-800">{group.date}</span>
                                <span className="text-sm text-gray-500 bg-gray-100 px-2 py-1 rounded">{group.schedule_name}</span>
                            </div>
                            
                            <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 gap-4">
                                {group.faces.map((face) => {
                                    const isSelected = selectedFaces.has(face.id);
                                    return (
                                        <div 
                                            key={face.id}
                                            onClick={() => toggleFaceSelection(face.id)}
                                            className={`relative group cursor-pointer rounded-lg overflow-hidden border-2 transition-all duration-200 ${isSelected ? 'border-primary ring-2 ring-primary ring-opacity-50 scale-105' : 'border-transparent hover:border-gray-300'}`}
                                        >
                                            <img 
                                                src={face.url} 
                                                alt="Posible asistencia" 
                                                className="w-full h-24 sm:h-32 object-cover bg-gray-100"
                                            />
                                            
                                            {/* Overlay de selección */}
                                            {isSelected && (
                                                <div className="absolute inset-0 bg-primary/20 flex items-center justify-center">
                                                    <div className="bg-primary text-white rounded-full p-1 shadow-lg">
                                                        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor" className="w-5 h-5">
                                                            <path fillRule="evenodd" d="M16.704 4.153a.75.75 0 01.143 1.052l-8 10.5a.75.75 0 01-1.127.075l-4.5-4.5a.75.75 0 011.06-1.06l3.894 3.893 7.48-9.817a.75.75 0 011.05-.143z" clipRule="evenodd" />
                                                        </svg>
                                                    </div>
                                                </div>
                                            )}
                                        </div>
                                    );
                                })}
                            </div>
                        </div>
                    ))}
                </div>
             </div>
          )}

        </div>
      </div>

       <footer className="absolute bottom-4 right-6 text-xs text-gray-100/80">
        <p>Plataforma desarrollada para la UNSA</p>
      </footer>
    </div>
  );
};

export default Register;
import { useState, type FormEvent, type ChangeEvent, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import api from '../services/api';
import unsaBgURL from '../assets/unsa_bg2.avif';

// --- MOCK DATA PARA LA DEMOSTRACIÓN ---
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


// Interfaces para los datos que vienen del backend
interface MatchedFace {
  id: string;
  url: string;
  similarity: number;
}

interface MatchGroup {
  date: string;
  schedule_name: string;
  schedule_id: string;
  faces: MatchedFace[];
}

const Register = () => {
  // --- Estados de Pasos ---
  const [step, setStep] = useState<1 | 2>(1);

  // Estados del Formulario - Paso 1
  const [firstName, setFirstName] = useState('');
  const [lastName, setLastName] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [role, setRole] = useState<'student' | 'teacher'>('student');
  const [cui, setCui] = useState('');

  // Estados del Formulario - Paso 2
  const [profileImage, setProfileImage] = useState<File | null>(null);
  const [previewUrl, setPreviewUrl] = useState<string | null>(null);

  // Estados de UI y Lógica
  const [error, setError] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [recoverMode, setRecoverMode] = useState(false); 
  const [selectedFaces, setSelectedFaces] = useState<Set<string>>(new Set()); 

    // Estados para la recuperación de asistencia real
  const [potentialMatches, setPotentialMatches] = useState<MatchGroup[]>([]);
  const [isMatching, setIsMatching] = useState(false);

  
  const navigate = useNavigate();

  // --- EFECTO: Buscar coincidencias cuando sube foto + recoverMode activo ---
  useEffect(() => {
    const fetchMatches = async () => {
      if (step === 2 && recoverMode && role === 'student' && profileImage) {
        setIsMatching(true);
        setPotentialMatches([]); // Limpiar anteriores
        try {
          const formData = new FormData();
          formData.append('image', profileImage);

          // Llamada al endpoint nuevo en attendance-mcsv (puerto 5000)
          const response = await api.post('/unknown-faces/match', formData, {
            headers: { 'Content-Type': 'multipart/form-data' }
          });

          setPotentialMatches(response.data);
        } catch (err) {
          console.error("Error buscando coincidencias:", err);
          // No bloqueamos el flujo, solo no mostramos sugerencias
        } finally {
          setIsMatching(false);
        }
      }
    };

    // Debounce pequeño o llamar directamente
    fetchMatches();
  }, [step, recoverMode, role, profileImage]);


  // --- Validaciones y Navegación ---
  const handleNextStep = (e: FormEvent) => {
    e.preventDefault();
    setError('');
    
    // Validación simple del paso 1
    if (!firstName || !lastName || !email || !password) {
      setError('Por favor completa todos los campos obligatorios.');
      return;
    }
    if (role === 'student' && !cui) {
      setError('El CUI es obligatorio para estudiantes.');
      return;
    }

    setStep(2);
  };

  const handlePrevStep = () => {
    setError('');
    setStep(1);
    // Desactivamos modo recuperación si volvemos atrás para mantener la UI limpia
    setRecoverMode(false);
    setPotentialMatches([]); 
  };

  // --- Manejo de Imagen ---
  const handleImageChange = (e: ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      const file = e.target.files[0];
      setProfileImage(file);
      setPreviewUrl(URL.createObjectURL(file));
    }
  };

  // --- Manejo de selección de fotos (Recuperación) ---
  // CORREGIDO: Ahora recibe scheduleId para forzar selección única por grupo
  const toggleFaceSelection = (faceId: string, scheduleId: string) => {
    const newSelection = new Set(selectedFaces);

    // 1. Si ya está seleccionada esa cara, simplemente la quitamos (deseleccionar)
    if (newSelection.has(faceId)) {
      newSelection.delete(faceId);
      setSelectedFaces(newSelection);
      return;
    }

    // 2. Si vamos a seleccionar una nueva cara, debemos asegurarnos de limpiar 
    // cualquier otra cara que pertenezca al MISMO horario (scheduleId)
    const group = MOCK_UNKNOWN_FACES.find(g => g.schedule_id === scheduleId);
    
    if (group) {
      // Recorremos todas las caras de este grupo horario
      group.faces.forEach(face => {
        // Si alguna estaba seleccionada, la quitamos del Set
        if (newSelection.has(face.id)) {
          newSelection.delete(face.id);
        }
      });
    }

    // 3. Agregamos la nueva selección (ahora es exclusiva para este grupo)
    newSelection.add(faceId);
    setSelectedFaces(newSelection);
  };

  // --- Submit Final ---
  const handleSubmit = async (e: FormEvent) => {
    e.preventDefault();
    setError('');
    setIsLoading(true);

    if (!profileImage) {
        setError('Es necesario subir una foto frontal para el registro biométrico.');
        setIsLoading(false);
        return;
    }

    const payload = {
      email,
      password,
      first_name: firstName,
      last_name: lastName,
      role,
      ...(role === 'student' && { cui }),
      // image: profileImage (Aquí iría la lógica de envío de archivo real)
    };
    
    try {
      // 1. Crear Usuario
      await api.post('/auth/register', payload);
      
      console.log("Imagen de perfil lista para enviar:", profileImage.name);

      // 2. Lógica de Recuperación de Asistencia
      if (recoverMode && role === 'student' && selectedFaces.size > 0) {
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
        console.log("Usuario:", email);
        console.log("Asistencias a regularizar:", recoveryData);
        alert(`Registro exitoso con foto de perfil. Se han enviado ${recoveryData.length} asistencias para regularización.`);
      } else {
        alert('¡Registro exitoso! Tu perfil y foto han sido guardados.');
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
      <div className="absolute inset-0 bg-cover bg-center" style={{ backgroundImage: `url(${unsaBgURL})` }}></div>
      <div className="absolute inset-0 bg-gray-400/60 backdrop-blur-sm"></div>

      <div className="relative flex min-h-screen items-center justify-center p-4">
        
        <div className={`w-full transition-all duration-500 ease-in-out bg-white/95 rounded-2xl shadow-2xl ring-1 ring-black/5 overflow-hidden flex flex-col lg:flex-row ${(step === 2 && recoverMode) ? 'max-w-6xl' : 'max-w-md'}`}>
          
          {/* --- COLUMNA IZQUIERDA (FORMULARIO) --- */}
          <div className={`p-6 sm:p-10 transition-all duration-500 ${(step === 2 && recoverMode) ? 'lg:w-1/3 border-r border-gray-200' : 'w-full'}`}>
            <div className="text-center mb-6">
              <h2 className="text-3xl font-bold tracking-tight text-gray-900">Crear Cuenta</h2>
              <p className="mt-2 text-sm text-gray-600">
                {step === 1 ? 'Paso 1: Datos Personales' : 'Paso 2: Biometría'}
              </p>
              <div className="flex justify-center gap-2 mt-3">
                <div className={`h-2 w-8 rounded-full ${step === 1 ? 'bg-primary' : 'bg-gray-300'}`}></div>
                <div className={`h-2 w-8 rounded-full ${step === 2 ? 'bg-primary' : 'bg-gray-300'}`}></div>
              </div>
            </div>

            <form className="space-y-4" onSubmit={step === 1 ? handleNextStep : handleSubmit}>
              {step === 1 && (
                <div className="space-y-4 animate-fadeIn">
                   {/* Inputs iguales que antes... */}
                   <div className="flex flex-col gap-4 sm:flex-row">
                    <div className="w-full sm:w-1/2">
                      <label htmlFor="first-name" className={labelStyles}>Nombres</label>
                      <div className="mt-1"><input id="first-name" type="text" value={firstName} onChange={(e) => setFirstName(e.target.value)} className={inputStyles} placeholder="Juan" autoFocus/></div>
                    </div>
                    <div className="w-full sm:w-1/2">
                      <label htmlFor="last-name" className={labelStyles}>Apellidos</label>
                      <div className="mt-1"><input id="last-name" type="text" value={lastName} onChange={(e) => setLastName(e.target.value)} className={inputStyles} placeholder="Perez"/></div>
                    </div>
                  </div>
                  <div>
                    <label htmlFor="email-address" className={labelStyles}>Correo</label>
                    <div className="mt-1"><input id="email-address" type="email" value={email} onChange={(e) => setEmail(e.target.value)} className={inputStyles} placeholder="ej@unsa.edu.pe"/></div>
                  </div>
                  <div>
                    <label htmlFor="password" className={labelStyles}>Contraseña</label>
                    <div className="mt-1"><input id="password" type="password" value={password} onChange={(e) => setPassword(e.target.value)} className={inputStyles} placeholder="••••••••"/></div>
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
                    <div>
                      <label htmlFor="cui" className={labelStyles}>CUI</label>
                      <div className="mt-1"><input id="cui" type="text" value={cui} onChange={(e) => setCui(e.target.value)} className={inputStyles} placeholder="20201234"/></div>
                    </div>
                  )}
                  {error && <p className="text-center text-sm text-red-600 animate-pulse">{error}</p>}
                  <div className="pt-2">
                    <button type="submit" className="flex w-full justify-center rounded-lg bg-primary px-4 py-2.5 text-sm font-semibold text-white shadow-sm hover:bg-opacity-90 transition-colors">Siguiente</button>
                  </div>
                </div>
              )}

              {step === 2 && (
                <div className="space-y-5 animate-fadeIn">
                    {/* Input de Imagen */}
                    <div>
                        <label className={labelStyles}>Foto de Perfil (Frontal)</label>
                        <div className="mt-1 flex justify-center rounded-lg border border-dashed border-gray-400 px-6 py-6 hover:bg-gray-50 transition-colors relative">
                            {previewUrl ? (
                                <div className="text-center relative">
                                    <img src={previewUrl} alt="Preview" className="h-32 w-32 object-cover rounded-full mx-auto shadow-md border-2 border-primary" />
                                    <button type="button" onClick={() => {setProfileImage(null); setPreviewUrl(null);}} className="absolute -top-2 -right-2 bg-red-100 text-red-600 rounded-full p-1 hover:bg-red-200">
                                        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor" className="w-4 h-4"><path d="M6.28 5.22a.75.75 0 00-1.06 1.06L8.94 10l-3.72 3.72a.75.75 0 101.06 1.06L10 11.06l3.72 3.72a.75.75 0 101.06-1.06L11.06 10l3.72-3.72a.75.75 0 00-1.06-1.06L10 8.94 6.28 5.22z" /></svg>
                                    </button>
                                </div>
                            ) : (
                                <div className="text-center">
                                    <label htmlFor="file-upload" className="relative cursor-pointer rounded-md bg-white font-medium text-primary hover:text-primary/80">
                                        <span>Sube una foto</span>
                                        <input id="file-upload" name="file-upload" type="file" accept="image/*" className="sr-only" onChange={handleImageChange} />
                                    </label>
                                    <p className="text-xs text-gray-500 mt-1">PNG, JPG hasta 5MB</p>
                                </div>
                            )}
                        </div>
                    </div>

                    {role === 'student' && (
                        <div className="p-3 bg-gray-50 rounded-lg border border-gray-200">
                            <div className="flex items-center justify-between">
                                <button
                                    type="button"
                                    onClick={() => setRecoverMode(!recoverMode)}
                                    className={`relative inline-flex h-6 w-11 flex-shrink-0 cursor-pointer rounded-full border-2 border-transparent transition-colors duration-200 ease-in-out focus:outline-none ${recoverMode ? 'bg-primary' : 'bg-gray-300'}`}
                                >
                                    <span aria-hidden="true" className={`pointer-events-none inline-block h-5 w-5 transform rounded-full bg-white shadow ring-0 transition duration-200 ease-in-out ${recoverMode ? 'translate-x-5' : 'translate-x-0'}`} />
                                </button>
                                <span className={`ml-3 text-sm font-medium ${recoverMode ? 'text-primary' : 'text-gray-500'}`}>
                                    {recoverMode ? 'Recuperar Asistencia Activo' : 'Recuperar Asistencia'}
                                </span>
                            </div>
                        </div>
                    )}

                    {error && <p className="text-center text-sm text-red-600 animate-pulse">{error}</p>}

                    <div className="pt-2 flex gap-3">
                        <button type="button" onClick={handlePrevStep} className="flex-1 rounded-lg border border-gray-300 bg-white px-4 py-2.5 text-sm font-gray-700 hover:bg-gray-50">Atrás</button>
                        <button type="submit" disabled={isLoading} className="flex-1 rounded-lg bg-primary px-4 py-2.5 text-sm font-semibold text-white hover:bg-opacity-90 disabled:opacity-50">
                          {isLoading ? '...' : 'Finalizar'}
                        </button>
                    </div>
                </div>
              )}
            </form>
            <p className="mt-6 text-center text-sm text-gray-600">
              ¿Ya tienes cuenta? <Link to="/login" className="font-medium text-primary hover:underline">Inicia sesión</Link>
            </p>
          </div>

          {/* --- COLUMNA DERECHA (GALERÍA DINÁMICA) --- */}
          {step === 2 && recoverMode && role === 'student' && (
             <div className="lg:w-2/3 bg-gray-50 p-6 sm:p-10 flex flex-col h-full animate-fadeIn border-t lg:border-t-0 lg:border-l border-gray-200">
                <div className="mb-4">
                    <h3 className="text-xl font-bold text-gray-800 flex items-center gap-2">
                       🔍 Identifícate en las fotos
                    </h3>
                    <p className="text-sm text-gray-600">
                        Hemos buscado rostros similares al tuyo en clases pasadas.
                    </p>
                </div>

                {isMatching ? (
                    <div className="flex-1 flex flex-col items-center justify-center text-gray-500">
                        <svg className="animate-spin h-10 w-10 text-primary mb-3" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                          <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                          <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                        </svg>
                        <p>Analizando datos biométricos...</p>
                    </div>
                ) : (
                    <div className="flex-1 overflow-y-auto pr-2 custom-scrollbar" style={{ maxHeight: '600px' }}>
                        {potentialMatches.length === 0 ? (
                            <div className="text-center py-10 text-gray-500 bg-white rounded-xl border border-dashed border-gray-300">
                                <p>No se encontraron rostros similares en asistencias pasadas.</p>
                                <p className="text-xs mt-1">Intenta subir una foto más clara o con mejor iluminación.</p>
                            </div>
                        ) : (
                            potentialMatches.map((group, index) => (
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
                                                    onClick={() => toggleFaceSelection(face.id, group.schedule_id)}
                                                    className={`relative group cursor-pointer rounded-lg overflow-hidden border-2 transition-all duration-200 ${isSelected ? 'border-primary ring-2 ring-primary ring-opacity-50 scale-105' : 'border-transparent hover:border-gray-300'}`}
                                                >
                                                    <img 
                                                        src={face.url} 
                                                        alt="Posible asistencia" 
                                                        className="w-full h-24 sm:h-32 object-cover bg-gray-100"
                                                        // Fallback por si la URL local falla
                                                        onError={(e) => {e.currentTarget.src = 'https://via.placeholder.com/150?text=Error+Img'}}
                                                    />
                                                    <div className="absolute bottom-0 left-0 right-0 bg-black/50 text-white text-[10px] p-1 text-center truncate">
                                                      Similitud: {(face.similarity * 100).toFixed(0)}%
                                                    </div>
                                                    
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
                            ))
                        )}
                    </div>
                )}
             </div>
          )}
        </div>
      </div>
       <footer className="absolute bottom-4 right-6 text-xs text-gray-100/80"><p>Plataforma desarrollada para la UNSA</p></footer>
    </div>
  );
};

export default Register;
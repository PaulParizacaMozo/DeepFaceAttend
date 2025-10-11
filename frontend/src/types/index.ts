// Define la estructura de un estudiante según tu backend
export interface Student {
  id: string;
  cui: string;
  first_name: string;
  last_name: string;
  filepath_embeddings: string;
}

// Define la estructura de un curso (para los datos de ejemplo)
export interface Course {
    title: string;
    code: string;
}
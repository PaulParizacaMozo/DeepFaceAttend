# ---- Etapa 1: Construcción (Build) ----
# Usamos una imagen de Node.js con Alpine (ligera)
FROM node:20-alpine AS build

# Establecemos el directorio de trabajo dentro del contenedor
WORKDIR /app

# Instalamos pnpm (basado en tu pnpm-lock.yaml)
RUN npm install -g pnpm

# Copiamos los archivos de definición de dependencias
COPY package.json pnpm-lock.yaml ./

# Instalamos las dependencias
RUN pnpm install --frozen-lockfile

# Copiamos todo el código fuente de la aplicación
COPY . .

# Ejecutamos el script de construcción (usualmente 'build' en Vite)
RUN pnpm run build

# ---- Etapa 2: Servidor (Serve) ----
# Usamos una imagen ligera de Nginx para servir los archivos estáticos
FROM nginx:1.25-alpine

# Copiamos los archivos estáticos construidos desde la etapa 'build'
# Vite construye en la carpeta 'dist' por defecto
COPY --from=build /app/dist /usr/share/nginx/html

# Copiamos el archivo de configuración de Nginx personalizado
# Este archivo es crucial para que el enrutamiento de React (SPA) funcione
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Exponemos el puerto 80 (el puerto por defecto de Nginx)
EXPOSE 80

# Comando por defecto para iniciar Nginx
CMD ["nginx", "-g", "daemon off;"]
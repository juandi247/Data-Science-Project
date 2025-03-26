# Imagen base con Python 3.11 (versión slim para menor tamaño)
FROM python:3.10-slim

# Establecer el directorio de trabajo
WORKDIR /app

# Instalar dependencias del sistema necesarias
RUN apt-get update && apt-get install -y \
    libgl1-mesa-glx \
    && rm -rf /var/lib/apt/lists/*

# Copiar solo el archivo de dependencias primero para optimizar la caché de Docker
COPY requirements.txt .  

# Instalar dependencias de Python
RUN pip install --no-cache-dir -r requirements.txt  

# Copiar el resto del código al contenedor
COPY . .  

# Definir variables de entorno para Flask
ENV FLASK_APP=app.py
ENV FLASK_ENV=production

# Exponer el puerto 8080 para que sea compatible con Cloud Run
EXPOSE 8080

# Comando para ejecutar la app con Gunicorn
ENTRYPOINT ["gunicorn", "-w", "4", "-b", "0.0.0.0:8080", "app:app"]

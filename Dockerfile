# Dockerfile para la aplicación FastAPI
FROM python:3.11-slim

# Crear usuario no-root para seguridad
RUN useradd -m -u 1000 appuser

# Establecer directorio de trabajo
WORKDIR /app

# Instalar dependencias del sistema necesarias (gcc, postgresql-client)
RUN apt-get update && apt-get install -y gcc libpq-dev && rm -rf /var/lib/apt/lists/*

# Copiar requirements.txt e instalar dependencias Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar código de la aplicación
COPY . .

# Cambiar ownership y usuario
RUN chown -R appuser:appuser /app
USER appuser

# Exponer puerto 8080
EXPOSE 8080

# Ejecutar aplicación con uvicorn
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]

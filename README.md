# Proyecto Docker Compose con FastAPI y Base de Datos

API CRUD desarrollada con FastAPI y Docker Compose, utilizando PostgreSQL como base de datos.

## Requisitos Previos

- Docker instalado
- Docker Compose instalado

## Instalación y Ejecución

### 1. Construir y ejecutar los contenedores

```bash
docker compose up --build
```

Este comando construirá la imagen de la aplicación y levantará ambos contenedores (aplicación y base de datos).

### 2. Verificar que los servicios están corriendo

```bash
docker compose ps
```

### 3. Ver los logs

```bash
# Ver todos los logs
docker compose logs

# Ver logs de un servicio específico
docker compose logs app
docker compose logs db
```

### 4. Detener los contenedores

```bash
docker compose down
```

### 5. Detener y eliminar volúmenes (elimina los datos)

```bash
docker compose down -v
```

## Endpoints de la API

Una vez que la aplicación esté corriendo, estará disponible en `http://localhost:8080`

| Método | Ruta | Descripción | Respuesta correcta |
|--------|------|-------------|--------------------|
| GET | `/estudiantes` | Lista todos los estudiantes | 200 |
| GET | `/estudiantes/{id}` | Obtiene un estudiante por ID | 200 |
| POST | `/estudiantes` | Crea un estudiante | 201 |
| DELETE | `/estudiantes/{id}` | Elimina un estudiante por ID | 204 (sin cuerpo) |

### Ejemplo de creación

```bash
curl -X POST http://localhost:8080/estudiantes \
  -H "Content-Type: application/json" \
  -d '{"nombre": "Lupe Lau Chu", "email": "lupelc@example.com", "edad": 25}'
```

Respuesta (201):

```json
{"id": 1, "nombre": "Lupe Lau Chu", "email": "lupelc@example.com", "edad": 25}
```

### Validación de datos

- `nombre`: obligatorio, mínimo 2 caracteres y sin números.
- `email`: obligatorio y con formato de email válido. No puede repetirse.
- `edad`: obligatoria, número entero entre 3 y 98.

### Control de errores

| Código | Cuándo ocurre |
|--------|---------------|
| 404 Not Found | El estudiante no existe (GET o DELETE con un ID inexistente) |
| 422 Unprocessable Entity | Datos inválidos en el POST: campo ausente, tipo incorrecto, email mal formado, nombre con números o edad fuera de rango |
| 400 Bad Request | Ya existe un estudiante con el mismo email |

Ejemplo de 404:

```json
{"detail": "Estudiante 9999 no encontrado"}
```

## Logging

La aplicación registra con `logging` (nivel INFO) las operaciones principales:
creación, lectura, listado y eliminación de estudiantes, además de los errores
(estudiante no encontrado, email duplicado). Los logs se ven con:

```bash
docker compose logs -f app
```

Formato: `fecha-módulo-NIVEL-mensaje`, por ejemplo
`2026-10-18 19:11:51,357-main-INFO-Estudiante registrado con ID:1`.

## Persistencia

PostgreSQL guarda sus datos en el volumen con nombre `my_database_volume`,
montado en `/var/lib/postgresql/data`. Los datos sobreviven a `docker compose down`
y solo se pierden con `docker compose down -v`.

## Red y conectividad

Los servicios `app` y `db` comparten la red `app-network`. La aplicación se conecta
a la base de datos usando el nombre del servicio como host (`db`) mediante la
variable de entorno `DATABASE_URL`, definida en `docker-compose.yml`.

## Documentación Interactiva

- **Swagger UI**: `http://localhost:8080/docs`
- **ReDoc**: `http://localhost:8080/redoc`

## Estructura del Proyecto

- `docker-compose.yml`: Configuración de servicios y red
- `Dockerfile`: Configuración de la imagen de la aplicación
- `main.py`: Código de la aplicación FastAPI
- `requirements.txt`: Dependencias de Python

## Notas

- Los datos de la base de datos persisten en un volumen de Docker
- Los contenedores se comunican a través de una red personalizada
- El puerto 8080 está expuesto al host para acceder a la API

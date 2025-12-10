# 🗄️ Guía de Base de Datos - ORISOD Voice Assistant

## 📋 Configuración de PostgreSQL

### 1. **Instalar PostgreSQL**

#### En Ubuntu/Debian:

```bash
sudo apt update
sudo apt install postgresql postgresql-contrib
```

#### En macOS:

```bash
brew install postgresql
brew services start postgresql
```

#### En Docker:

```bash
docker run --name orisod-postgres \
  -e POSTGRES_USER=orisod_user \
  -e POSTGRES_PASSWORD=orisod_password \
  -e POSTGRES_DB=orisod_calls \
  -p 5432:5432 \
  -d postgres:15
```

### 2. **Crear Base de Datos y Usuario**

```bash
# Conectar a PostgreSQL
sudo -u postgres psql

# Crear usuario
CREATE USER orisod_user WITH PASSWORD 'orisod_password';

# Crear base de datos
CREATE DATABASE orisod_calls OWNER orisod_user;

# Dar permisos
GRANT ALL PRIVILEGES ON DATABASE orisod_calls TO orisod_user;

# Salir
\q
```

### 3. **Configurar Variable de Entorno**

En tu archivo `.env`:

```env
DATABASE_URL=postgresql://orisod_user:orisod_password@localhost:5432/orisod_calls
```

**Para Dokploy**, agrega esta variable en el panel de Environment Variables.

---

## 🚀 Inicializar Base de Datos

### Opción 1: Automático (al iniciar la app)

La base de datos se inicializa automáticamente cuando inicias la aplicación:

```bash
uvicorn main:app --port 8000
```

### Opción 2: Manual

```bash
python init_db.py
```

---

## 📊 Esquema de la Tabla `calls`

| Columna           | Tipo        | Descripción                                |
| ----------------- | ----------- | ------------------------------------------ |
| `id`              | SERIAL      | ID autoincremental (Primary Key)           |
| `call_sid`        | VARCHAR     | Twilio Call SID (único)                    |
| `user_phone`      | VARCHAR     | Número de teléfono del usuario             |
| `start_time`      | TIMESTAMPTZ | Hora de inicio de la llamada               |
| `interaction_log` | JSON        | Log de interacciones (user/ai/timestamp)   |
| `status`          | VARCHAR     | Estado: "active", "completed", "failed"    |
| `duration`        | INTEGER     | Duración en segundos (nullable)            |
| `user_intent`     | VARCHAR     | Intención detectada del usuario (nullable) |

---

## 🔌 Endpoints de la API

### **GET /api/calls**

Obtener todas las llamadas (con paginación)

**Parámetros**:

- `skip`: Número de registros a saltar (default: 0)
- `limit`: Máximo de registros a retornar (default: 100)

**Ejemplo**:

```bash
curl http://localhost:8000/api/calls?skip=0&limit=10
```

**Respuesta**:

```json
{
  "calls": [
    {
      "id": 1,
      "call_sid": "CAxxxx",
      "user_phone": "+52XXXXXXXXXX",
      "start_time": "2025-12-10T00:00:00Z",
      "interaction_log": [
        {
          "user": "Hola",
          "ai": "¡Hola! Bienvenido a ORISOD...",
          "timestamp": 1733875200
        }
      ],
      "status": "completed",
      "duration": 120,
      "user_intent": "información_producto"
    }
  ],
  "total": 1
}
```

### **GET /api/calls/{call_id}**

Obtener una llamada específica por ID

**Ejemplo**:

```bash
curl http://localhost:8000/api/calls/1
```

### **GET /api/calls/sid/{call_sid}**

Obtener una llamada por Twilio Call SID

**Ejemplo**:

```bash
curl http://localhost:8000/api/calls/sid/CAxxxx
```

### **PUT /api/calls/{call_id}**

Actualizar una llamada

**Ejemplo**:

```bash
curl -X PUT http://localhost:8000/api/calls/1 \
  -H "Content-Type: application/json" \
  -d '{
    "status": "completed",
    "duration": 120,
    "user_intent": "compra"
  }'
```

### **DELETE /api/calls/{call_id}**

Eliminar una llamada

**Ejemplo**:

```bash
curl -X DELETE http://localhost:8000/api/calls/1
```

---

## 🧪 Probar los Endpoints

### 1. **Ver todas las llamadas**

```bash
curl http://localhost:8000/api/calls
```

### 2. **Crear una llamada de prueba** (desde Python)

```python
import requests

data = {
    "call_sid": "CA123456789",
    "user_phone": "+5212345678",
    "interaction_log": [
        {
            "user": "Hola",
            "ai": "¡Hola! ¿En qué puedo ayudarte?",
            "timestamp": 1733875200
        }
    ],
    "status": "active"
}

response = requests.post("http://localhost:8000/api/calls", json=data)
print(response.json())
```

---

## 📖 Documentación Interactiva

FastAPI genera documentación automática:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

---

## 🔧 Comandos Útiles de PostgreSQL

### Conectar a la base de datos:

```bash
psql -U orisod_user -d orisod_calls
```

### Ver todas las tablas:

```sql
\dt
```

### Ver estructura de la tabla calls:

```sql
\d calls
```

### Ver todas las llamadas:

```sql
SELECT * FROM calls;
```

### Contar llamadas:

```sql
SELECT COUNT(*) FROM calls;
```

### Ver llamadas recientes:

```sql
SELECT id, call_sid, user_phone, status, start_time
FROM calls
ORDER BY start_time DESC
LIMIT 10;
```

### Limpiar todas las llamadas:

```sql
TRUNCATE TABLE calls RESTART IDENTITY;
```

---

## 🐳 Docker Compose (Opcional)

Agregar PostgreSQL a tu `docker-compose.yml`:

```yaml
version: "3.8"

services:
  app:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://orisod_user:orisod_password@db:5432/orisod_calls
    depends_on:
      - db

  db:
    image: postgres:15
    environment:
      - POSTGRES_USER=orisod_user
      - POSTGRES_PASSWORD=orisod_password
      - POSTGRES_DB=orisod_calls
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data

volumes:
  postgres_data:
```

---

## 📊 Dashboard Frontend

Para usar estos endpoints en tu dashboard, ejemplo en TypeScript:

```typescript
// Obtener todas las llamadas
async function getCalls(): Promise<CallListResponse> {
  const response = await fetch("http://localhost:8000/api/calls");
  return response.json();
}

// Obtener una llamada específica
async function getCall(id: number): Promise<CallData> {
  const response = await fetch(`http://localhost:8000/api/calls/${id}`);
  return response.json();
}
```

---

## ⚠️ Troubleshooting

### Error: "could not connect to server"

```bash
# Verificar que PostgreSQL esté corriendo
sudo systemctl status postgresql

# Iniciar PostgreSQL
sudo systemctl start postgresql
```

### Error: "password authentication failed"

Verifica que las credenciales en `.env` coincidan con las de PostgreSQL.

### Error: "database does not exist"

```bash
sudo -u postgres createdb orisod_calls
```

---

**Versión**: 1.4.0 - Database Integration
**Fecha**: 2025-12-10

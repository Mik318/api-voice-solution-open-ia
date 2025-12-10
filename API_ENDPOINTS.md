# 📡 API Endpoints - ORISOD Voice Assistant

## 🎯 Base URL

```
http://localhost:8000
```

En producción (Dokploy):
```
https://tu-app.dokploy.com
```

---

## 🔌 Endpoints Disponibles

### **Dashboard API** (Prefijo: `/api`)

Todos los endpoints del dashboard están bajo el prefijo `/api` y tienen el tag `dashboard`.

---

### 1️⃣ **GET `/api/calls`**
Obtener lista de llamadas recientes con paginación

**Parámetros Query**:
- `skip` (int, opcional): Número de registros a saltar (default: 0)
- `limit` (int, opcional): Máximo de registros a retornar (default: 50)

**Ejemplo**:
```bash
curl http://localhost:8000/api/calls\?skip\=0\&limit\=10
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
          "ai": "¡Hola! Bienvenido...",
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

---

### 2️⃣ **GET `/api/calls/{call_id}`**
Obtener detalles de una llamada específica por ID

**Parámetros Path**:
- `call_id` (int): ID de la llamada

**Ejemplo**:
```bash
curl http://localhost:8000/api/calls/1
```

**Respuesta**: Objeto `CallData` (ver arriba)

---

### 3️⃣ **GET `/api/calls/sid/{call_sid}`**
Obtener una llamada específica por Twilio Call SID

**Parámetros Path**:
- `call_sid` (string): Twilio Call SID

**Ejemplo**:
```bash
curl http://localhost:8000/api/calls/sid/CAxxxx
```

**Respuesta**: Objeto `CallData`

---

### 4️⃣ **GET `/api/search`** 🆕
Buscar llamadas por número de teléfono

**Parámetros Query**:
- `phone` (string, requerido): Número de teléfono a buscar (búsqueda parcial)

**Ejemplo**:
```bash
curl http://localhost:8000/api/search\?phone\=5512345
```

**Respuesta**:
```json
{
  "calls": [...],
  "total": 5
}
```

---

### 5️⃣ **PUT `/api/calls/{call_id}`**
Actualizar información de una llamada

**Parámetros Path**:
- `call_id` (int): ID de la llamada

**Body**:
```json
{
  "status": "completed",
  "duration": 120,
  "user_intent": "compra",
  "interaction_log": [
    {
      "user": "Hola",
      "ai": "¡Hola!",
      "timestamp": 1733875200
    }
  ]
}
```

**Ejemplo**:
```bash
curl -X PUT http://localhost:8000/api/calls/1 \
  -H "Content-Type: application/json" \
  -d '{"status": "completed", "duration": 120}'
```

**Respuesta**: Objeto `CallData` actualizado

---

### 6️⃣ **DELETE `/api/calls/{call_id}`**
Eliminar una llamada de la base de datos

**Parámetros Path**:
- `call_id` (int): ID de la llamada

**Ejemplo**:
```bash
curl -X DELETE http://localhost:8000/api/calls/1
```

**Respuesta**:
```json
{
  "message": "Llamada 1 eliminada exitosamente"
}
```

---

### 7️⃣ **GET `/api/openapi.yaml`** 🆕
Descargar especificación OpenAPI en formato YAML

**Ejemplo**:
```bash
curl http://localhost:8000/api/openapi.yaml -o openapi.yaml
```

**Respuesta**: Archivo YAML con la especificación completa de la API

---

## 🔐 Webhooks de Twilio

### **POST `/outgoing-call`**
Webhook para llamadas salientes de Twilio

**Uso**: Configurar en Twilio como webhook para llamadas entrantes

---

### **WS `/media-stream`**
WebSocket para streaming de audio entre Twilio y OpenAI

**Uso**: Automático desde TwiML

---

### **POST `/recording-status`**
Callback para estado de grabaciones

**Uso**: Configurar en Twilio para notificaciones de grabación

---

## 📊 Documentación Interactiva

### **Swagger UI**
```
http://localhost:8000/docs
```

Interfaz interactiva para probar todos los endpoints

### **ReDoc**
```
http://localhost:8000/redoc
```

Documentación alternativa más detallada

---

## 🧪 Ejemplos de Uso

### **Frontend TypeScript**

```typescript
// Obtener todas las llamadas
async function getCalls(): Promise<CallListResponse> {
  const response = await fetch('http://localhost:8000/api/calls?limit=50');
  return response.json();
}

// Buscar por teléfono
async function searchCalls(phone: string): Promise<CallListResponse> {
  const response = await fetch(`http://localhost:8000/api/search?phone=${phone}`);
  return response.json();
}

// Obtener detalles de una llamada
async function getCallDetails(id: number): Promise<CallData> {
  const response = await fetch(`http://localhost:8000/api/calls/${id}`);
  return response.json();
}

// Actualizar llamada
async function updateCall(id: number, data: CallUpdate): Promise<CallData> {
  const response = await fetch(`http://localhost:8000/api/calls/${id}`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(data)
  });
  return response.json();
}
```

### **Python**

```python
import requests

# Obtener llamadas
response = requests.get('http://localhost:8000/api/calls', params={'limit': 50})
calls = response.json()

# Buscar por teléfono
response = requests.get('http://localhost:8000/api/search', params={'phone': '5512345'})
results = response.json()

# Actualizar llamada
response = requests.put(
    'http://localhost:8000/api/calls/1',
    json={'status': 'completed', 'duration': 120}
)
updated_call = response.json()
```

---

## 🔒 CORS

CORS está habilitado para todos los orígenes (`*`). 

**En producción**, configura orígenes específicos en `main.py`:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://tu-dashboard.com"],  # Cambiar esto
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

---

## ⚠️ Notas Importantes

1. **DATABASE_URL requerida**: Los endpoints `/api/*` requieren que `DATABASE_URL` esté configurada
2. **Paginación**: Usa `skip` y `limit` para manejar grandes volúmenes de datos
3. **Búsqueda**: El endpoint `/api/search` hace búsqueda parcial (LIKE)
4. **Async**: Todos los endpoints son asíncronos para mejor performance

---

**Versión**: 1.5.0 - API Router Refactor
**Fecha**: 2025-12-10

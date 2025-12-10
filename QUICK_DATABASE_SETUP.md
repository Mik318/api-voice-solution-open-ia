# ⚡ Quick Database Setup - ORISOD Voice Assistant

## 🎯 Opciones de Uso

### Opción 1: Sin Base de Datos (Solo Llamadas)
Si solo quieres probar las llamadas de voz sin guardar datos:

```bash
# NO agregues DATABASE_URL a tu .env
# La app funcionará normalmente pero sin endpoints de base de datos
uvicorn main:app --port 8000
```

**Verás este mensaje**:
```
⚠️  WARNING: DATABASE_URL not configured. Database features disabled.
⚠️  Skipping database initialization (DATABASE_URL not configured)
```

✅ **Funcionará**: Llamadas de voz, WebSocket, Twilio
❌ **No funcionará**: Endpoints `/api/calls/*`

---

### Opción 2: Con PostgreSQL (Completo)

#### **Paso 1: Iniciar PostgreSQL con Docker (Más Fácil)**

```bash
docker run --name orisod-postgres \
  -e POSTGRES_USER=orisod_user \
  -e POSTGRES_PASSWORD=orisod_password \
  -e POSTGRES_DB=orisod_calls \
  -p 5432:5432 \
  -d postgres:15
```

#### **Paso 2: Agregar a `.env`**

```env
DATABASE_URL=postgresql://orisod_user:orisod_password@localhost:5432/orisod_calls
```

#### **Paso 3: Iniciar la App**

```bash
pip install -r requirements.txt
uvicorn main:app --port 8000
```

**Verás**:
```
Initializing database...
Database initialized successfully!
```

✅ **Todo funcionará**: Llamadas + API de base de datos

---

## 🐳 Para Dokploy

### Sin Base de Datos
No agregues `DATABASE_URL` a las variables de entorno.

### Con Base de Datos

1. **Crear servicio PostgreSQL en Dokploy**
   - Tipo: PostgreSQL
   - Usuario: `orisod_user`
   - Password: `orisod_password`
   - Database: `orisod_calls`

2. **Agregar variable de entorno** en tu app:
   ```
   DATABASE_URL=postgresql://orisod_user:orisod_password@postgres-service:5432/orisod_calls
   ```

3. **Redeploy**

---

## 🧪 Verificar

### Sin Base de Datos:
```bash
curl http://localhost:8000/
# ✅ Debería funcionar

curl http://localhost:8000/api/calls
# ❌ Error 500 (esperado)
```

### Con Base de Datos:
```bash
curl http://localhost:8000/
# ✅ Funciona

curl http://localhost:8000/api/calls
# ✅ Funciona: {"calls": [], "total": 0}
```

---

## 📊 Documentación API

Si tienes la base de datos configurada:
- **Swagger**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

---

## ❓ FAQ

**P: ¿Puedo usar la app sin PostgreSQL?**
R: Sí, solo no tendrás los endpoints de API para guardar llamadas.

**P: ¿Cómo sé si la base de datos está configurada?**
R: Mira los logs al iniciar. Si ves el warning, no está configurada.

**P: ¿Puedo agregar la base de datos después?**
R: Sí, solo agrega `DATABASE_URL` a `.env` y reinicia la app.

---

**Recomendación**: Empieza sin base de datos para probar las llamadas, luego agrega PostgreSQL cuando necesites el dashboard.

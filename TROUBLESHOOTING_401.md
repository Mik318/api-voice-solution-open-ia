# 🔧 Solución al Error HTTP 401 - OpenAI Authentication

## ❌ Error que estás viendo

```
websockets.exceptions.InvalidStatus: server rejected WebSocket connection: HTTP 401
```

Este error significa que **OpenAI está rechazando la autenticación** de tu API key.

## ✅ Soluciones Paso a Paso

### 1️⃣ Verificar la API Key en Dokploy

**En tu panel de Dokploy:**

1. Ve a tu aplicación
2. Click en **"Environment Variables"** o **"Variables de Entorno"**
3. Verifica que `OPENAI_API_KEY` esté configurada correctamente

**Formato correcto:**
```env
OPENAI_API_KEY=sk-proj-xxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

**Checklist:**
- ✅ Debe empezar con `sk-` o `sk-proj-`
- ✅ No debe tener espacios antes o después
- ✅ Debe estar completa (no cortada)
- ✅ Debe ser una key activa y válida

### 2️⃣ Verificar Acceso a Realtime API

La **Realtime API** de OpenAI es una API especial que requiere:

1. **Ir a**: https://platform.openai.com/settings/organization/billing
2. **Verificar**:
   - ✅ Tienes créditos disponibles
   - ✅ Tu cuenta tiene acceso a la Realtime API
   - ✅ No estás en free tier (Realtime API requiere pago)

**Nota**: No todos los usuarios tienen acceso inmediato a Realtime API. Puede requerir:
- Tier de uso 1 o superior
- Haber gastado al menos $5 USD
- Cuenta verificada

### 3️⃣ Crear una Nueva API Key

Si tu key es antigua o no funciona:

1. Ve a: https://platform.openai.com/api-keys
2. Click en **"Create new secret key"**
3. Dale un nombre: `ORISOD Voice Assistant`
4. **Copia la key completa** (solo se muestra una vez)
5. Actualiza en Dokploy:
   ```env
   OPENAI_API_KEY=sk-proj-NUEVA_KEY_AQUI
   ```
6. **Redeploy** la aplicación

### 4️⃣ Verificar el Modelo

El modelo que estamos usando es:
```
gpt-4o-realtime-preview-2024-10-01
```

**Verifica que**:
- ✅ Tienes acceso a GPT-4
- ✅ Tienes acceso a modelos preview
- ✅ Tu organización permite Realtime API

### 5️⃣ Revisar los Logs en Dokploy

Después de redeploy, revisa los logs. Deberías ver:

**✅ Correcto:**
```
Connecting to OpenAI Realtime API (key: sk-proj-...)
Configuring OpenAI session for Spanish language support
Session updated successfully
```

**❌ Error:**
```
ERROR connecting to OpenAI: server rejected WebSocket connection: HTTP 401
❌ ERROR DE AUTENTICACIÓN (HTTP 401)
```

## 🧪 Probar la API Key Manualmente

Puedes probar tu API key con este comando:

```bash
curl https://api.openai.com/v1/models \
  -H "Authorization: Bearer TU_API_KEY_AQUI"
```

**Respuesta esperada**: Lista de modelos disponibles

**Si da error 401**: La API key no es válida

## 📋 Checklist Completo

Antes de continuar, verifica:

- [ ] La API key está en Dokploy sin espacios
- [ ] La API key empieza con `sk-` o `sk-proj-`
- [ ] Tienes créditos en tu cuenta de OpenAI
- [ ] Tu cuenta tiene acceso a Realtime API
- [ ] Has hecho redeploy después de cambiar la key
- [ ] Los logs muestran la key (primeros 8 caracteres)

## 🔄 Alternativa: Usar Modelo Diferente

Si no tienes acceso a Realtime API, puedes usar la rama `llama3` del proyecto original que usa un modelo diferente:

```bash
git checkout llama3
```

O contacta a OpenAI para solicitar acceso a Realtime API.

## 📞 Contactar a OpenAI

Si todo lo anterior falla:

1. Ve a: https://help.openai.com/
2. Describe tu problema:
   ```
   No puedo conectar a la Realtime API.
   Error: HTTP 401 Unauthorized
   Mi cuenta tiene créditos pero la conexión WebSocket falla.
   ```

## 🎯 Después de Solucionar

Una vez que tengas la API key correcta:

1. **Actualiza en Dokploy**:
   ```env
   OPENAI_API_KEY=sk-proj-tu-key-valida
   ```

2. **Redeploy** la aplicación

3. **Verifica los logs**:
   ```
   Connecting to OpenAI Realtime API (key: sk-proj-...)
   ```

4. **Prueba una llamada**

## 💡 Prevención

Para evitar este error en el futuro:

- ✅ Guarda tu API key en un lugar seguro
- ✅ No compartas tu API key públicamente
- ✅ Rota tus keys periódicamente
- ✅ Monitorea tu uso y créditos en OpenAI
- ✅ Configura límites de gasto en OpenAI

---

**¿Sigue sin funcionar?** Comparte los logs completos y te ayudo a diagnosticar el problema específico.

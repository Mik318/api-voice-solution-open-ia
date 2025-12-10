# Guía de Despliegue en Dokploy - ORISOD Enzyme® Voice Assistant

## 📋 Requisitos Previos

1. **Cuenta de Dokploy** activa
2. **Credenciales necesarias**:
   - OpenAI API Key (con acceso a Realtime API)
   - Twilio Account SID
   - Twilio Auth Token
   - Twilio Phone Number

## 🚀 Pasos para Desplegar en Dokploy

### 1. Crear Nueva Aplicación en Dokploy

1. Accede a tu panel de Dokploy
2. Clic en **"Create Application"** o **"Nueva Aplicación"**
3. Selecciona **"Git Repository"** como fuente
4. Conecta tu repositorio: `https://github.com/Mik318/api-voice-solution-open-ia.git`
5. Selecciona la rama: `master`

### 2. Configurar el Build

**Tipo de Aplicación**: Docker / Dockerfile

**Configuración de Build**:
- **Dockerfile Path**: `Dockerfile` (en la raíz del proyecto)
- **Build Context**: `.` (raíz del proyecto)
- **Port**: `8000`

### 3. Configurar Variables de Entorno

En la sección de **Environment Variables** de Dokploy, agrega:

```env
OPENAI_API_KEY=tu_api_key_de_openai
TWILIO_ACCOUNT_SID=tu_twilio_account_sid
TWILIO_AUTH_TOKEN=tu_twilio_auth_token
TWILIO_PHONE_NUMBER=tu_numero_de_twilio
PORT=8000
```

> **⚠️ IMPORTANTE**: NO incluyas `NGROK_URL` todavía. Lo configuraremos después del primer despliegue.

### 4. Desplegar la Aplicación

1. Clic en **"Deploy"** o **"Desplegar"**
2. Espera a que el build se complete (2-5 minutos)
3. Verifica que el estado sea **"Running"**

### 5. Configurar NGROK_URL

1. Copia la URL de tu aplicación en Dokploy
2. Agrega la variable de entorno:
   ```env
   NGROK_URL=https://tu-app.dokploy.com
   ```
3. **Redeploy** la aplicación

### 6. Configurar Webhooks de Twilio

1. Accede a [Consola de Twilio](https://console.twilio.com/)
2. Ve a **Phone Numbers** → **Active Numbers**
3. Selecciona tu número
4. En **"Voice & Fax"**:
   - Webhook: `https://tu-app.dokploy.com/outgoing-call`
   - HTTP POST
5. Guarda

## 🧪 Probar

```bash
curl -X POST "https://tu-app.dokploy.com/make-call" \
  -H "Content-Type: application/json" \
  -d '{"to_phone_number": "+52XXXXXXXXXX"}'
```

## 🐛 Troubleshooting

### Application not starting
- Verifica logs en Dokploy
- Asegúrate de que todas las variables estén configuradas

### OpenAI API key invalid
- Verifica que tengas acceso a Realtime API

### Twilio webhook failed
- Verifica que NGROK_URL use HTTPS
- Verifica webhooks en Twilio

---

**Repositorio**: https://github.com/Mik318/api-voice-solution-open-ia

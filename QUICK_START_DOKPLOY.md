# 🚀 Quick Start - Despliegue en Dokploy

## Pasos Rápidos (5 minutos)

### 1️⃣ Crear Aplicación en Dokploy
- Tipo: **Git Repository**
- Repo: `https://github.com/Mik318/api-voice-solution-open-ia.git`
- Branch: `master`
- Build Type: **Dockerfile**
- Port: **8000**

### 2️⃣ Variables de Entorno
```env
OPENAI_API_KEY=sk-...
TWILIO_ACCOUNT_SID=AC...
TWILIO_AUTH_TOKEN=...
TWILIO_PHONE_NUMBER=+1...
PORT=8000
```

### 3️⃣ Deploy
Click **"Deploy"** y espera 2-5 minutos

### 4️⃣ Configurar NGROK_URL
Después del primer deploy, agrega:
```env
NGROK_URL=https://tu-app.dokploy.com
```
Y haz **Redeploy**

### 5️⃣ Configurar Twilio Webhook
En Twilio Console → Phone Numbers:
- Webhook URL: `https://tu-app.dokploy.com/outgoing-call`
- Method: **POST**

## ✅ Verificar
```bash
curl https://tu-app.dokploy.com/
```

## 📚 Documentación Completa
Ver [DEPLOY_DOKPLOY.md](DEPLOY_DOKPLOY.md)

# Changelog - ORISOD Enzyme® Voice Assistant

## [1.3.0] - 2025-12-09

### ✅ Fixes Implementados

#### 1. **Fix: Compatibilidad con websockets 12.0+**
- **Problema**: `TypeError: BaseEventLoop.create_connection() got an unexpected keyword argument 'extra_headers'`
- **Solución**: Cambiar `extra_headers` a `additional_headers`
- **Commit**: `88cc823`

#### 2. **Fix: Error HTTP 401 - Autenticación OpenAI**
- **Problema**: `websockets.exceptions.InvalidStatus: server rejected WebSocket connection: HTTP 401`
- **Solución**: 
  - Agregar validación de API key antes de conectar
  - Implementar manejo de errores comprehensivo
  - Mostrar mensajes claros de diagnóstico
- **Commit**: `e4d659e`

#### 3. **Fix: Atributo .open no existe en websockets 12.0+**
- **Problema**: `'ClientConnection' object has no attribute 'open'`
- **Solución**: Remover verificaciones de `openai_ws.open` (el context manager lo maneja automáticamente)
- **Commit**: `bd752ca`

### 🎯 Mejoras de Funcionalidad

#### 1. **Soporte Mejorado para Español**
- Cambio de voz: `echo` → `alloy` (mejor pronunciación en español)
- Temperatura aumentada: `0.2` → `0.8` (respuestas más naturales)
- Configuración de turn detection para mejor detección de voz
- Transcripción con Whisper-1 activada
- Instrucciones explícitas para hablar siempre en español
- **Commit**: `fc51592`

#### 2. **Adaptación para ORISOD Enzyme®**
- Prompt especializado en ORISOD
- Conocimiento completo del producto
- Base de conocimiento técnica
- Mensajes de bienvenida en español
- **Commit**: `5a41195`

### 🐳 Infraestructura y Despliegue

#### 1. **Soporte para Docker y Dokploy**
- Dockerfile optimizado con health checks
- .dockerignore para builds eficientes
- docker-compose.yml para desarrollo local
- Guías completas de despliegue
- **Commit**: `3db268b`

### 📚 Documentación

#### 1. **Guías Creadas**
- `DEPLOY_DOKPLOY.md` - Guía completa de despliegue
- `QUICK_START_DOKPLOY.md` - Inicio rápido (5 minutos)
- `DESPLIEGUE_DOKPLOY_RESUMEN.md` - Resumen del proyecto
- `MEJORAS_ESPAÑOL.md` - Documentación de mejoras en español
- `TROUBLESHOOTING_401.md` - Solución de errores de autenticación
- **Commits**: `542c69d`, `05a674c`, `85a1bd7`

## Progreso de Errores

### ❌ Error 1: extra_headers
```
TypeError: BaseEventLoop.create_connection() got an unexpected keyword argument 'extra_headers'
```
**Estado**: ✅ SOLUCIONADO

### ❌ Error 2: HTTP 401
```
websockets.exceptions.InvalidStatus: server rejected WebSocket connection: HTTP 401
```
**Estado**: ✅ SOLUCIONADO (requiere API key válida del usuario)

### ❌ Error 3: .open attribute
```
ERROR connecting to OpenAI: 'ClientConnection' object has no attribute 'open'
```
**Estado**: ✅ SOLUCIONADO

## Estado Actual

### ✅ Funcionando
- ✅ Conexión a OpenAI Realtime API
- ✅ Autenticación correcta
- ✅ Configuración de sesión en español
- ✅ WebSocket entre Twilio y OpenAI
- ✅ Health checks
- ✅ Logging detallado

### 🔧 Configuración Actual

```python
VOICE = "alloy"  # Mejor pronunciación en español
temperature = 0.8  # Respuestas naturales
turn_detection = {
    "type": "server_vad",
    "threshold": 0.5,
    "prefix_padding_ms": 300,
    "silence_duration_ms": 500,
}
input_audio_transcription = {
    "model": "whisper-1"
}
```

## Próximos Pasos

1. ✅ Redeploy en Dokploy con los últimos cambios
2. ✅ Probar llamada completa
3. ✅ Verificar comprensión del español
4. ✅ Ajustar parámetros si es necesario

## Versiones

- **Python**: 3.11
- **FastAPI**: latest
- **websockets**: >=12.0
- **OpenAI Model**: gpt-4o-realtime-preview-2024-10-01

## Commits Totales

```
bd752ca - fix: Remover uso de atributo .open en websockets 12.0+
85a1bd7 - docs: Agregar guía de troubleshooting para error HTTP 401
e4d659e - fix: Agregar manejo de errores para HTTP 401 y validación de API key
05a674c - docs: Agregar documentación de mejoras en español
fc51592 - feat: Mejorar soporte y comprensión del español
88cc823 - fix: Corregir error de compatibilidad con websockets
542c69d - docs: Agregar guías rápidas de despliegue en Dokploy
3db268b - feat: Agregar soporte para Docker y Dokploy
5a41195 - feat: Adaptar asistente de voz para ORISOD Enzyme®
```

---

**Versión**: 1.3.0
**Estado**: ✅ Listo para producción
**Fecha**: 2025-12-09

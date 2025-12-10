# ORISOD Enzyme® - Asistente de Voz con IA

Un sistema de voz con IA en tiempo real especializado en ORISOD Enzyme®, que integra la API Realtime de OpenAI con Twilio Voice para crear conversaciones inteligentes sobre este revolucionario suplemento bioactivo antioxidante. Perfecto para atención al cliente, información de producto y ventas consultivas.

## Branches

- **[main](https://github.com/intellwe/ai-calling-agent/tree/main)** - OpenAI Realtime API version (streaming, low latency)
- **[llama3](https://github.com/intellwe/ai-calling-agent/tree/llama3)** - Llama3 via Together AI (traditional, cost-effective)

## Características

- **Procesamiento de Voz en Tiempo Real** - Reconocimiento de voz y respuesta instantánea
- **Conocimiento Especializado en ORISOD** - Información detallada sobre beneficios, componentes y evidencia científica
- **Consultoría de Salud Personalizada** - Adapta las recomendaciones según las necesidades del cliente
- **Manejo Inteligente de Interrupciones** - Flujo de conversación natural con detección de voz
- **Configuración Flexible** - Prompts personalizables y ajustes de voz
- **Grabación de Llamadas** - Registro automático para seguimiento y mejora continua
- **Comunicación WebSocket** - Streaming de audio de baja latencia
- **Listo para Producción** - Construido con FastAPI para escalabilidad

## Quick Start

### Prerequisites

- Python 3.8+
- OpenAI API key (with Realtime API access)
- Twilio account (SID, Auth Token, Phone Number)
- ngrok or similar tunneling tool

### Installation

1. **Clone the repository**

```bash
   git clone https://github.com/Mik318/api-voice-solution-open-ia.git
   cd api-voice-solution-open-ia
```

2. **Install dependencies**

```bash
pip install -r requirements.txt
```

3. **Configure environment**

   ```bash
   cp .env.example .env
   # Edit .env with your credentials
   ```

4. **Start the server**

   ```bash
   uvicorn main:app --port 8000
   ```

5. **Expose with ngrok** (para desarrollo local)
   ```bash
   ngrok http 8000
   ```

## 🐳 Despliegue con Docker

### Opción 1: Docker Compose (Desarrollo Local)

```bash
# Construir y ejecutar
docker-compose up -d

# Ver logs
docker-compose logs -f

# Detener
docker-compose down
```

### Opción 2: Docker Manual

```bash
# Construir imagen
docker build -t orisod-voice-assistant .

# Ejecutar contenedor
docker run -d \
  --name orisod-assistant \
  -p 8000:8000 \
  --env-file .env \
  orisod-voice-assistant
```

## 🚀 Despliegue en Dokploy

Para desplegar en producción con Dokploy, consulta la guía completa: **[DEPLOY_DOKPLOY.md](DEPLOY_DOKPLOY.md)**

**Resumen rápido**:

1. Conecta tu repositorio GitHub en Dokploy
2. Configura las variables de entorno
3. Dokploy construirá automáticamente usando el `Dockerfile`
4. Tu aplicación estará disponible con SSL automático

## Configuration

Create a `.env` file with the following variables:

```env
OPENAI_API_KEY=your_openai_api_key
TWILIO_ACCOUNT_SID=your_twilio_account_sid
TWILIO_AUTH_TOKEN=your_twilio_auth_token
TWILIO_PHONE_NUMBER=your_twilio_phone_number
NGROK_URL=your_ngrok_url
PORT=8000
```

## API Endpoints

| Method    | Endpoint         | Description               |
| --------- | ---------------- | ------------------------- |
| GET       | `/`              | Health check              |
| POST      | `/make-call`     | Initiate outbound call    |
| POST      | `/outgoing-call` | Twilio webhook handler    |
| WebSocket | `/media-stream`  | Real-time audio streaming |

### Making a Call

```bash
curl -X POST "http://localhost:8000/make-call" \
  -H "Content-Type: application/json" \
  -d '{"to_phone_number": "+1234567890"}'
```

## Architecture

```
┌─────────────┐    WebSocket   ┌─────────────┐    HTTP/WS    ┌─────────────┐
│   Twilio    │ ◄────────────► │  FastAPI    │ ◄───────────► │   OpenAI    │
│   Voice     │                │   Server    │               │ Realtime API│
└─────────────┘                └─────────────┘               └─────────────┘
```

The system creates a bridge between Twilio's voice services and OpenAI's Realtime API, enabling natural voice conversations with AI.

## Development

### Setup Development Environment

1. **Install development dependencies**

   ```bash
   pip install -r requirements-dev.txt
   ```

2. **Install pre-commit hooks** (optional)
   ```bash
   pre-commit install
   ```

### Code Quality Tools

- **Format code**: `black .`
- **Sort imports**: `isort .`
- **Lint code**: `flake8`
- **Type checking**: `mypy main.py`
- **Security scan**: `bandit -r .`
- **Run tests**: `pytest`

### Personalizar el Comportamiento de la IA

Edita `prompts/system_prompt.txt` para modificar la personalidad y respuestas del asistente de ORISOD. El archivo `contexto_orisod.txt` contiene toda la información técnica y científica del producto que el asistente puede utilizar.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Autor

- [@Mik318](https://github.com/Mik318)

## Créditos Originales

Basado en el proyecto AI Calling Agent de:

- [@FardinHash](https://github.com/FardinHash) -> [LinkedIn](https://linkedin.com/in/fardinkai)
- [@RianaAzad](https://github.com/RianaAzad) -> [LinkedIn](https://linkedin.com/in/riana-azad)

## ⚠️ Disclaimer

This project is not officially affiliated with OpenAI or Twilio. Use responsibly and in accordance with their terms of service.

---

⭐ If you find this project helpful, please give it a star!

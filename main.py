import asyncio
import base64
import json
import os
from typing import List

import websockets
from dotenv import load_dotenv
from fastapi import Depends, FastAPI, HTTPException, Request, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.websockets import WebSocketDisconnect
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from twilio.rest import Client
from twilio.twiml.voice_response import Connect, VoiceResponse

from database import get_db, init_db, create_call, update_call_interaction, finalize_call
from models import Call
from schemas import CallListResponse, CallResponse, CallUpdate
import api_routes

load_dotenv()


def load_prompt(file_name: str) -> str:
    """Load system prompt from file."""
    dir_path = os.path.dirname(os.path.realpath(__file__))
    prompt_path = os.path.join(dir_path, "prompts", f"{file_name}.txt")

    try:
        with open(prompt_path, "r", encoding="utf-8") as file:
            return file.read().strip()
    except FileNotFoundError:
        print(f"Could not find file: {prompt_path}")
        raise


OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
TWILIO_PHONE_NUMBER = os.getenv("TWILIO_PHONE_NUMBER")
NGROK_URL = os.getenv("NGROK_URL")
PORT = int(os.getenv("PORT", 8000))

SYSTEM_MESSAGE = load_prompt("system_prompt")
VOICE = "shimmer"  # Mejor voz femenina para español mexicano
LOG_EVENT_TYPES = [
    "response.content.done",
    "rate_limits.updated",
    "response.done",
    "input_audio_buffer.committed",
    "input_audio_buffer.speech_stopped",
    "input_audio_buffer.speech_started",
    "session.created",
    "conversation.item.input_audio_transcription.completed",
]

app = FastAPI(title="ORISOD Enzyme® Voice Assistant API", version="1.0.0")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://call-asist.sistems-mik3.com", "http://localhost:4500"],  # Configure this properly in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def startup_event():
    """Initialize database on startup."""
    print("Initializing database...")
    init_db()
    print("Database initialized successfully!")


if not OPENAI_API_KEY:
    raise ValueError("Missing the OpenAI API key. Please set it in the .env file.")

if not TWILIO_ACCOUNT_SID or not TWILIO_AUTH_TOKEN or not TWILIO_PHONE_NUMBER:
    raise ValueError("Missing Twilio configuration. Please set it in the .env file.")


@app.get("/")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "message": "ORISOD Enzyme® Voice Assistant is running!"}


class CallRequest(BaseModel):
    to_phone_number: str


@app.post("/make-call")
async def make_call(request: CallRequest):
    """Initiate an outbound call to the specified phone number."""
    if not request.to_phone_number:
        return {"error": "Phone number is required"}

    try:
        client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
        call = client.calls.create(
            url=f"{NGROK_URL}/outgoing-call",
            to=request.to_phone_number,
            from_=TWILIO_PHONE_NUMBER,
            record=True,
            recording_status_callback=f"{NGROK_URL}/recording-status",
            recording_status_callback_method="POST",
        )
        print(f"Call initiated with SID: {call.sid}")
        return {"call_sid": call.sid, "status": "success"}
    except Exception as e:
        print(f"Error initiating call: {e}")
        return {"error": str(e), "status": "failed"}


@app.get("/outgoing-call", operation_id="handle_outgoing_call_get")
async def handle_outgoing_call_get(request: Request):
    """Handle outgoing call webhook (GET) and return TwiML response."""
    response = VoiceResponse()
    # Conectar directamente al asistente de OpenAI sin mensaje inicial de Twilio
    connect = Connect()
    connect.stream(url=f"wss://{request.url.hostname}/media-stream")
    response.append(connect)
    return HTMLResponse(content=str(response), media_type="application/xml")


@app.post("/outgoing-call", operation_id="handle_outgoing_call_post")
async def handle_outgoing_call_post(request: Request):
    """Handle outgoing call webhook (POST) and return TwiML response."""
    response = VoiceResponse()
    # Conectar directamente al asistente de OpenAI sin mensaje inicial de Twilio
    connect = Connect()
    connect.stream(url=f"wss://{request.url.hostname}/media-stream")
    response.append(connect)
    return HTMLResponse(content=str(response), media_type="application/xml")


@app.api_route("/recording-status", methods=["POST"], operation_id="handle_recording_status")
async def handle_recording_status(request: Request):
    """Handle recording status updates from Twilio."""
    form_data = await request.form()
    recording_status = form_data.get("RecordingStatus")
    recording_sid = form_data.get("RecordingSid")
    call_sid = form_data.get("CallSid")
    recording_url = form_data.get("RecordingUrl")

    print(f"Recording Status Update: {recording_status} for Call {call_sid}")
    print(f"Recording SID: {recording_sid}, URL: {recording_url}")

    if recording_status == "completed":
        print(f"  Recording URL: {recording_url}")

    return {"status": "received"}


@app.websocket("/media-stream")
async def handle_media_stream(websocket: WebSocket):
    """Handle WebSocket connections between Twilio and OpenAI."""
    print("Client connected")
    await websocket.accept()

    # Verificar que la API key esté configurada
    if not OPENAI_API_KEY:
        print("ERROR: OPENAI_API_KEY no está configurada")
        await websocket.close(code=1008, reason="OpenAI API key not configured")
        return
    
    print(f"Connecting to OpenAI Realtime API (key: {OPENAI_API_KEY[:8]}...)")

    try:
        async with websockets.connect(
            "wss://api.openai.com/v1/realtime?model=gpt-4o-realtime-preview-2024-12-17",
            additional_headers={
                "Authorization": f"Bearer {OPENAI_API_KEY}",
                "OpenAI-Beta": "realtime=v1",
            },
        ) as openai_ws:
            await send_session_update(openai_ws)
            stream_sid = None
            session_id = None
            greeting_sent = False
            call_sid = None
            call_start_time = None
            
            # Buffer para acumular la conversación completa
            conversation_buffer = []
            current_user_text = None
            current_ai_text = None

            async def receive_from_twilio():
                """Receive audio data from Twilio and send it to the OpenAI Realtime API."""
                nonlocal stream_sid, greeting_sent, call_sid, call_start_time
                try:
                    async for message in websocket.iter_text():
                        data = json.loads(message)
                        if data["event"] == "media":
                            audio_append = {
                                "type": "input_audio_buffer.append",
                                "audio": data["media"]["payload"],
                            }
                            await openai_ws.send(json.dumps(audio_append))
                        elif data["event"] == "start":
                            stream_sid = data["start"]["streamSid"]
                            call_sid = data["start"]["callSid"]
                            
                            # Extract phone number from metadata if available
                            user_phone = data["start"].get("customParameters", {}).get("from", "unknown")
                            
                            print(f"Incoming stream has started {stream_sid}")
                            print(f"Call SID: {call_sid}, Phone: {user_phone}")
                            
                            # Create call record in database
                            import time
                            call_start_time = time.time()
                            create_call(call_sid, user_phone)
                            
                            # Enviar saludo inicial cuando el stream comienza
                            if not greeting_sent:
                                await send_initial_greeting(openai_ws)
                                greeting_sent = True
                except WebSocketDisconnect:
                    print("Client disconnected.")
                finally:
                    # Guardar la conversación completa en la base de datos
                    if call_sid and conversation_buffer:
                        print(f"💾 Saving complete conversation ({len(conversation_buffer)} interactions)")
                        update_call_interaction(call_sid, conversation_buffer)
                    
                    # Finalize call in database
                    if call_sid and call_start_time:
                        import time
                        duration = int(time.time() - call_start_time)
                        finalize_call(call_sid, duration=duration)

            async def send_to_twilio():
                """Receive events from the OpenAI Realtime API, send audio back to Twilio."""
                nonlocal stream_sid, session_id, current_user_text, current_ai_text, call_sid, conversation_buffer
                try:
                    async for openai_message in openai_ws:
                        response = json.loads(openai_message)
                        if response["type"] in LOG_EVENT_TYPES:
                            print(f"Received event: {response['type']}", response)
                        if response["type"] == "session.created":
                            session_id = response["session"]["id"]
                        if response["type"] == "session.updated":
                            print("Session updated successfully:", response)
                        
                        # Capture user transcription from the transcription completed event
                        if response["type"] == "conversation.item.input_audio_transcription.completed":
                            transcript = response.get("transcript", "")
                            if transcript:
                                current_user_text = transcript
                                print(f"📝 User said: {current_user_text}")
                        
                        # Capture AI response text from response.done event
                        if response["type"] == "response.done":
                            # Extract transcript from the assistant's message in the output
                            output = response.get("response", {}).get("output", [])
                            for item in output:
                                if item.get("role") == "assistant":
                                    content = item.get("content", [])
                                    for c in content:
                                        if c.get("type") == "audio" and "transcript" in c:
                                            current_ai_text = c["transcript"]
                                            print(f"🤖 AI responded: {current_ai_text}")
                                            break
                            
                            # Guardar el par de interacción en el buffer solo si tenemos ambos textos
                            if current_user_text and current_ai_text:
                                import time
                                timestamp = time.time()  # Usar timestamp en segundos (float)
                                
                                interaction = {
                                    "user": current_user_text,
                                    "ai": current_ai_text,
                                    "timestamp": timestamp
                                }
                                conversation_buffer.append(interaction)
                                print(f"✅ Buffered interaction #{len(conversation_buffer)}: user + ai")
                                
                                # Reset para la siguiente interacción
                                current_user_text = None
                                current_ai_text = None
                            elif current_ai_text and not current_user_text:
                                # Caso especial: saludo inicial de la IA (sin mensaje del usuario)
                                import time
                                timestamp = time.time()
                                
                                interaction = {
                                    "user": "",  # Usuario no dijo nada (es el saludo inicial)
                                    "ai": current_ai_text,
                                    "timestamp": timestamp
                                }
                                conversation_buffer.append(interaction)
                                print(f"✅ Buffered initial greeting #{len(conversation_buffer)}")
                                
                                # Reset
                                current_ai_text = None
                        
                        if response["type"] == "response.audio.delta" and response.get(
                            "delta"
                        ):
                            try:
                                audio_payload = base64.b64encode(
                                    base64.b64decode(response["delta"])
                                ).decode("utf-8")
                                audio_delta = {
                                    "event": "media",
                                    "streamSid": stream_sid,
                                    "media": {"payload": audio_payload},
                                }
                                await websocket.send_json(audio_delta)
                            except Exception as e:
                                print(f"Error processing audio data: {e}")
                        
                        if response["type"] == "input_audio_buffer.speech_started":
                            print("Speech started, interrupting AI response")

                            await websocket.send_json(
                                {"streamSid": stream_sid, "event": "clear"}
                            )

                            interrupt_message = {"type": "response.cancel"}
                            await openai_ws.send(json.dumps(interrupt_message))
                except Exception as e:
                    print(f"Error in send_to_twilio: {e}")
                finally:
                    # Guardar la conversación al terminar el stream de OpenAI
                    if call_sid and conversation_buffer:
                        print(f"💾 Saving complete conversation on stream end ({len(conversation_buffer)} interactions)")
                        update_call_interaction(call_sid, conversation_buffer)

            await asyncio.gather(receive_from_twilio(), send_to_twilio())
    
    except Exception as e:
        error_msg = str(e)
        print(f"ERROR connecting to OpenAI: {error_msg}")
        
        if "401" in error_msg or "Unauthorized" in error_msg:
            print("❌ ERROR DE AUTENTICACIÓN (HTTP 401)")
            print("Posibles causas:")
            print("1. La OPENAI_API_KEY no es válida")
            print("2. La API key no tiene acceso a Realtime API")
            print("3. La cuenta no tiene créditos suficientes")
            print("4. Verifica en: https://platform.openai.com/api-keys")
        
        await websocket.close(code=1011, reason=f"OpenAI connection failed: {error_msg}")
        raise



async def send_session_update(openai_ws):
    """Configure OpenAI session with audio settings and instructions."""
    session_update = {
        "type": "session.update",
        "session": {
            "input_audio_format": "g711_ulaw",
            "output_audio_format": "g711_ulaw",
            "voice": VOICE,
            "instructions": SYSTEM_MESSAGE,
            "modalities": ["text", "audio"],
            "temperature": 0.8,  # Mayor temperatura para respuestas más naturales
            "turn_detection": {
                "type": "server_vad",
                "threshold": 0.6,  # Umbral más alto para evitar falsos positivos
                "prefix_padding_ms": 400,  # Más padding para capturar inicio de palabras
                "silence_duration_ms": 700,  # Más tiempo de silencio para español mexicano
            },
            "input_audio_transcription": {
                "model": "whisper-1",
                "language": "es"  # Forzar español para mejor reconocimiento
            },
        },
    }
    print("Configuring OpenAI session for Mexican Spanish")
    await openai_ws.send(json.dumps(session_update))


async def send_initial_greeting(openai_ws):
    """Send an initial greeting to trigger immediate AI response in Spanish."""
    # Enviar un mensaje para que el asistente salude inmediatamente
    greeting_message = {
        "type": "conversation.item.create",
        "item": {
            "type": "message",
            "role": "user",
            "content": [
                {
                    "type": "input_text",
                    "text": "Hola, acabo de conectarme. Por favor salúdame y preséntate."
                }
            ]
        }
    }
    await openai_ws.send(json.dumps(greeting_message))
    
    # Solicitar una respuesta inmediata
    response_create = {
        "type": "response.create"
    }
    await openai_ws.send(json.dumps(response_create))
    print("Initial greeting sent to OpenAI")



# ============================================================================
# INCLUDE API ROUTER
# ============================================================================

# Include API routes from api_routes.py
app.include_router(api_routes.router)


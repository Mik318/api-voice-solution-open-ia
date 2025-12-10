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

from database import get_db, init_db
from models import Call
from schemas import CallListResponse, CallResponse, CallUpdate

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
VOICE = "alloy"  # Mejor pronunciación en español
LOG_EVENT_TYPES = [
    "response.content.done",
    "rate_limits.updated",
    "response.done",
    "input_audio_buffer.committed",
    "input_audio_buffer.speech_stopped",
    "input_audio_buffer.speech_started",
    "session.created",
]

app = FastAPI(title="ORISOD Enzyme® Voice Assistant API", version="1.0.0")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure this properly in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup_event():
    """Initialize database on startup."""
    print("Initializing database...")
    await init_db()
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


@app.api_route("/outgoing-call", methods=["GET", "POST"])
async def handle_outgoing_call(request: Request):
    """Handle outgoing call webhook and return TwiML response."""
    response = VoiceResponse()
    response.say("¡Hola! Gracias por contactar con ORISOD Enzyme.")
    response.pause(length=1)
    response.say("Por favor espera mientras te conecto con nuestro asistente especializado.")

    connect = Connect()
    connect.stream(url=f"wss://{request.url.hostname}/media-stream")
    response.append(connect)
    return HTMLResponse(content=str(response), media_type="application/xml")


@app.api_route("/recording-status", methods=["POST"])
async def handle_recording_status(request: Request):
    """Handle recording status updates from Twilio."""
    form_data = await request.form()
    recording_status = form_data.get("RecordingStatus")
    recording_sid = form_data.get("RecordingSid")
    call_sid = form_data.get("CallSid")
    recording_url = form_data.get("RecordingUrl")
    recording_duration = form_data.get("RecordingDuration")

    print(f"Recording status update:")
    print(f"  Call SID: {call_sid}")
    print(f"  Recording SID: {recording_sid}")
    print(f"  Status: {recording_status}")

    if recording_status == "completed":
        print(f"  Recording URL: {recording_url}")
        print(f"  Duration: {recording_duration} seconds")

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

            async def receive_from_twilio():
                """Receive audio data from Twilio and send it to the OpenAI Realtime API."""
                nonlocal stream_sid
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
                            print(f"Incoming stream has started {stream_sid}")
                except WebSocketDisconnect:
                    print("Client disconnected.")
                    # La conexión se cerrará automáticamente al salir del context manager
                    pass

            async def send_to_twilio():
                """Receive events from the OpenAI Realtime API, send audio back to Twilio."""
                nonlocal stream_sid, session_id
                try:
                    async for openai_message in openai_ws:
                        response = json.loads(openai_message)
                        if response["type"] in LOG_EVENT_TYPES:
                            print(f"Received event: {response['type']}", response)
                        if response["type"] == "session.created":
                            session_id = response["session"]["id"]
                        if response["type"] == "session.updated":
                            print("Session updated successfully:", response)
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
                        if response["type"] == "conversation.item.created":
                            print(f"conversation.item.created event: {response}")
                        if response["type"] == "input_audio_buffer.speech_started":
                            print("Speech started, interrupting AI response")

                            await websocket.send_json(
                                {"streamSid": stream_sid, "event": "clear"}
                            )

                            interrupt_message = {"type": "response.cancel"}
                            await openai_ws.send(json.dumps(interrupt_message))
                except Exception as e:
                    print(f"Error in send_to_twilio: {e}")

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
                "threshold": 0.5,
                "prefix_padding_ms": 300,
                "silence_duration_ms": 500,
            },
            "input_audio_transcription": {
                "model": "whisper-1"
            },
        },
    }
    print("Configuring OpenAI session for Spanish language support")
    await openai_ws.send(json.dumps(session_update))


# ============================================================================
# DATABASE API ENDPOINTS
# ============================================================================

@app.get("/api/calls", response_model=CallListResponse, tags=["Calls"])
async def get_calls(
    skip: int = 0,
    limit: int = 100,
    db: AsyncSession = Depends(get_db)
):
    """
    Get all calls from the database.
    
    - **skip**: Number of records to skip (for pagination)
    - **limit**: Maximum number of records to return
    """
    # Get total count
    count_query = select(Call)
    result = await db.execute(count_query)
    total = len(result.scalars().all())
    
    # Get paginated results
    query = select(Call).offset(skip).limit(limit).order_by(Call.start_time.desc())
    result = await db.execute(query)
    calls = result.scalars().all()
    
    return CallListResponse(calls=calls, total=total)


@app.get("/api/calls/{call_id}", response_model=CallResponse, tags=["Calls"])
async def get_call(call_id: int, db: AsyncSession = Depends(get_db)):
    """
    Get a specific call by ID.
    
    - **call_id**: The ID of the call to retrieve
    """
    query = select(Call).where(Call.id == call_id)
    result = await db.execute(query)
    call = result.scalar_one_or_none()
    
    if not call:
        raise HTTPException(status_code=404, detail=f"Call with id {call_id} not found")
    
    return call


@app.get("/api/calls/sid/{call_sid}", response_model=CallResponse, tags=["Calls"])
async def get_call_by_sid(call_sid: str, db: AsyncSession = Depends(get_db)):
    """
    Get a specific call by Twilio Call SID.
    
    - **call_sid**: The Twilio Call SID
    """
    query = select(Call).where(Call.call_sid == call_sid)
    result = await db.execute(query)
    call = result.scalar_one_or_none()
    
    if not call:
        raise HTTPException(status_code=404, detail=f"Call with SID {call_sid} not found")
    
    return call


@app.put("/api/calls/{call_id}", response_model=CallResponse, tags=["Calls"])
async def update_call(
    call_id: int,
    call_update: CallUpdate,
    db: AsyncSession = Depends(get_db)
):
    """
    Update a call's information.
    
    - **call_id**: The ID of the call to update
    - **call_update**: The fields to update
    """
    query = select(Call).where(Call.id == call_id)
    result = await db.execute(query)
    call = result.scalar_one_or_none()
    
    if not call:
        raise HTTPException(status_code=404, detail=f"Call with id {call_id} not found")
    
    # Update fields if provided
    if call_update.interaction_log is not None:
        call.interaction_log = [log.dict() for log in call_update.interaction_log]
    if call_update.status is not None:
        call.status = call_update.status
    if call_update.duration is not None:
        call.duration = call_update.duration
    if call_update.user_intent is not None:
        call.user_intent = call_update.user_intent
    
    await db.commit()
    await db.refresh(call)
    
    return call


@app.delete("/api/calls/{call_id}", tags=["Calls"])
async def delete_call(call_id: int, db: AsyncSession = Depends(get_db)):
    """
    Delete a call from the database.
    
    - **call_id**: The ID of the call to delete
    """
    query = select(Call).where(Call.id == call_id)
    result = await db.execute(query)
    call = result.scalar_one_or_none()
    
    if not call:
        raise HTTPException(status_code=404, detail=f"Call with id {call_id} not found")
    
    await db.delete(call)
    await db.commit()
    
    return {"message": f"Call {call_id} deleted successfully"}

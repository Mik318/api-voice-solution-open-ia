"""API routes for dashboard and call management."""
from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import Response
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

import yaml

from database import get_db
from models import Call
from schemas import CallListResponse, CallResponse, CallUpdate

# Prefijo /api para diferenciarlo de los webhooks
router = APIRouter(prefix="/api", tags=["dashboard"])


@router.get("/calls", response_model=CallListResponse)
async def get_calls(
    skip: int = 0,
    limit: int = 50,
    db: AsyncSession = Depends(get_db)
):
    """Obtener lista de llamadas recientes"""
    # Get total count
    count_query = select(Call)
    result = await db.execute(count_query)
    total = len(result.scalars().all())
    
    # Get paginated results
    query = select(Call).offset(skip).limit(limit).order_by(Call.start_time.desc())
    result = await db.execute(query)
    calls = result.scalars().all()
    
    return CallListResponse(calls=calls, total=total)


@router.get("/calls/{call_id}", response_model=CallResponse)
async def get_call_details(call_id: int, db: AsyncSession = Depends(get_db)):
    """Obtener detalles de una llamada específica"""
    query = select(Call).where(Call.id == call_id)
    result = await db.execute(query)
    call = result.scalar_one_or_none()
    
    if not call:
        raise HTTPException(status_code=404, detail="Llamada no encontrada")
    
    return call


@router.get("/calls/sid/{call_sid}", response_model=CallResponse)
async def get_call_by_sid(call_sid: str, db: AsyncSession = Depends(get_db)):
    """Obtener una llamada específica por Twilio Call SID"""
    query = select(Call).where(Call.call_sid == call_sid)
    result = await db.execute(query)
    call = result.scalar_one_or_none()
    
    if not call:
        raise HTTPException(status_code=404, detail=f"Llamada con SID {call_sid} no encontrada")
    
    return call


@router.get("/search", response_model=CallListResponse)
async def search_calls(phone: str, db: AsyncSession = Depends(get_db)):
    """Buscar llamadas por número de teléfono"""
    # Buscar coincidencias parciales
    query = select(Call).where(Call.user_phone.contains(phone)).order_by(Call.start_time.desc())
    result = await db.execute(query)
    calls = result.scalars().all()
    
    return CallListResponse(calls=calls, total=len(calls))


@router.put("/calls/{call_id}", response_model=CallResponse)
async def update_call(
    call_id: int,
    call_update: CallUpdate,
    db: AsyncSession = Depends(get_db)
):
    """Actualizar información de una llamada"""
    query = select(Call).where(Call.id == call_id)
    result = await db.execute(query)
    call = result.scalar_one_or_none()
    
    if not call:
        raise HTTPException(status_code=404, detail=f"Llamada con id {call_id} no encontrada")
    
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


@router.delete("/calls/{call_id}")
async def delete_call(call_id: int, db: AsyncSession = Depends(get_db)):
    """Eliminar una llamada de la base de datos"""
    query = select(Call).where(Call.id == call_id)
    result = await db.execute(query)
    call = result.scalar_one_or_none()
    
    if not call:
        raise HTTPException(status_code=404, detail=f"Llamada con id {call_id} no encontrada")
    
    await db.delete(call)
    await db.commit()
    
    return {"message": f"Llamada {call_id} eliminada exitosamente"}


@router.get("/openapi.yaml", tags=["Documentacion"])
async def get_openapi_yaml(request: Request):
    """Descargar OpenAPI en formato YAML"""
    openapi_dict = request.app.openapi()
    yaml_str = yaml.safe_dump(openapi_dict, sort_keys=False, allow_unicode=True)
    headers = {"Content-Disposition": 'attachment; filename="openapi.yaml"'}
    return Response(content=yaml_str, media_type="application/x-yaml", headers=headers)

"""API routes for dashboard and call management."""
from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import Response
from sqlalchemy.orm import Session
from typing import List

import yaml

from database import get_db
import models
from schemas import CallListResponse, CallResponse, CallUpdate

# Prefijo /api para diferenciarlo de los webhooks
router = APIRouter(prefix="/api", tags=["dashboard"])


@router.get("/calls")
def get_calls(skip: int = 0, limit: int = 50, db: Session = Depends(get_db)):
    """Obtener lista de llamadas recientes"""
    calls = db.query(models.Call).order_by(models.Call.id.desc()).offset(skip).limit(limit).all()
    total = db.query(models.Call).count()
    return {"calls": calls, "total": total}


@router.get("/calls/{call_id}")
def get_call_details(call_id: int, db: Session = Depends(get_db)):
    """Obtener detalles de una llamada específica"""
    call = db.query(models.Call).filter(models.Call.id == call_id).first()
    if not call:
        raise HTTPException(status_code=404, detail="Llamada no encontrada")
    return call


@router.get("/calls/sid/{call_sid}")
def get_call_by_sid(call_sid: str, db: Session = Depends(get_db)):
    """Obtener una llamada específica por Twilio Call SID"""
    call = db.query(models.Call).filter(models.Call.call_sid == call_sid).first()
    if not call:
        raise HTTPException(status_code=404, detail=f"Llamada con SID {call_sid} no encontrada")
    return call


@router.get("/search")
def search_calls(phone: str, db: Session = Depends(get_db)):
    """Buscar llamadas por número de teléfono"""
    # Buscar coincidencias parciales
    calls = db.query(models.Call).filter(models.Call.user_phone.contains(phone)).order_by(models.Call.id.desc()).all()
    total = len(calls)
    return {"calls": calls, "total": total}


@router.put("/calls/{call_id}")
def update_call(call_id: int, call_update: CallUpdate, db: Session = Depends(get_db)):
    """Actualizar información de una llamada"""
    call = db.query(models.Call).filter(models.Call.id == call_id).first()
    
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
    
    db.commit()
    db.refresh(call)
    
    return call


@router.delete("/calls/{call_id}")
def delete_call(call_id: int, db: Session = Depends(get_db)):
    """Eliminar una llamada de la base de datos"""
    call = db.query(models.Call).filter(models.Call.id == call_id).first()
    
    if not call:
        raise HTTPException(status_code=404, detail=f"Llamada con id {call_id} no encontrada")
    
    db.delete(call)
    db.commit()
    
    return {"message": f"Llamada {call_id} eliminada exitosamente"}


@router.get("/openapi.yaml", tags=["Documentacion"])
def get_openapi_yaml(request: Request):
    """Descargar OpenAPI en formato YAML"""
    openapi_dict = request.app.openapi()
    yaml_str = yaml.safe_dump(openapi_dict, sort_keys=False, allow_unicode=True)
    headers = {"Content-Disposition": 'attachment; filename="openapi.yaml"'}
    return Response(content=yaml_str, media_type="application/x-yaml", headers=headers)


"""Model management endpoints."""

from fastapi import APIRouter, Depends, HTTPException
from typing import Dict
import uuid

from models import (
    ModelsResponse,
    AddModelRequest,
    AddModelResponse,
    Model,
)
from auth import verify_api_key

router = APIRouter(prefix="/models", tags=["models"])

# In-memory storage (replace with database in production)
models_db: Dict[str, Model] = {}


@router.get("", response_model=ModelsResponse)
async def list_models(api_key: str = Depends(verify_api_key)):
    """Get all configured models."""
    return ModelsResponse(models=list(models_db.values()))


@router.post("", response_model=AddModelResponse)
async def add_model(request: AddModelRequest, api_key: str = Depends(verify_api_key)):
    """Add a new model."""
    model = request.model

    # Generate ID if not provided
    if not model.id:
        model.id = str(uuid.uuid4())

    # Check if model already exists
    if model.id in models_db:
        raise HTTPException(status_code=400, detail="Model already exists")

    # Store model
    models_db[model.id] = model

    return AddModelResponse(model=model)

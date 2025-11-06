"""Provider management endpoints."""

from fastapi import APIRouter, Depends, HTTPException
from typing import Dict
import uuid

from ..models import (
    ProvidersResponse,
    AddProviderRequest,
    AddProviderResponse,
    Provider,
)
from ..auth import verify_api_key

router = APIRouter(prefix="/providers", tags=["providers"])

# In-memory storage (replace with database in production)
providers_db: Dict[str, Provider] = {}


@router.get("", response_model=ProvidersResponse)
async def list_providers(api_key: str = Depends(verify_api_key)):
    """Get all configured providers."""
    return ProvidersResponse(providers=list(providers_db.values()))


@router.post("", response_model=AddProviderResponse)
async def add_provider(
    request: AddProviderRequest, api_key: str = Depends(verify_api_key)
):
    """Add a new provider."""
    provider = request.provider
    
    # Generate ID if not provided
    if not provider.id:
        provider.id = str(uuid.uuid4())
    
    # Check if provider already exists
    if provider.id in providers_db:
        raise HTTPException(status_code=400, detail="Provider already exists")
    
    # Store provider
    providers_db[provider.id] = provider
    
    return AddProviderResponse(provider=provider)

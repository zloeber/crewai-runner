"""Profile management router for CrewAI profiles."""

import os
import yaml
from pathlib import Path
from typing import List
from fastapi import APIRouter, HTTPException, status, Depends
from datetime import datetime

from auth import verify_api_key
from models import (
    ProfileConfig,
    ProfileListResponse,
    LoadProfileRequest,
    LoadProfileResponse,
    SaveProfileRequest,
    SaveProfileResponse,
    DeleteProfileRequest,
    DeleteProfileResponse,
    ExportProfileResponse,
    ImportProfileRequest,
    ImportProfileResponse,
    ErrorResponse,
    ProfileMetadata,
)

router = APIRouter(
    prefix="/profiles",
    tags=["profiles"],
    dependencies=[Depends(verify_api_key)],
)

# Configuration
PROFILES_DIR = Path("profiles")
PROFILES_DIR.mkdir(exist_ok=True)


def get_profile_path(name: str) -> Path:
    """Get the file path for a profile."""
    return PROFILES_DIR / f"{name}.yaml"


def load_profile_from_file(name: str) -> ProfileConfig:
    """Load a profile from YAML file."""
    profile_path = get_profile_path(name)
    
    if not profile_path.exists():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Profile '{name}' not found"
        )
    
    try:
        with open(profile_path, 'r', encoding='utf-8') as f:
            profile_data = yaml.safe_load(f)
        
        return ProfileConfig(**profile_data)
    except yaml.YAMLError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid YAML in profile '{name}': {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error loading profile '{name}': {str(e)}"
        )


def save_profile_to_file(profile: ProfileConfig, overwrite: bool = False) -> str:
    """Save a profile to YAML file."""
    name = profile.metadata.name
    profile_path = get_profile_path(name)
    
    if profile_path.exists() and not overwrite:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Profile '{name}' already exists. Use overwrite=true to replace it."
        )
    
    try:
        # Update the created timestamp if not set
        if not profile.metadata.created:
            profile.metadata.created = datetime.utcnow().isoformat() + "Z"
        
        # Convert to dict and save as YAML
        profile_data = profile.model_dump(exclude_none=True)
        
        with open(profile_path, 'w', encoding='utf-8') as f:
            yaml.dump(profile_data, f, default_flow_style=False, sort_keys=False, indent=2)
        
        return name
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error saving profile '{name}': {str(e)}"
        )


@router.get("/", response_model=ProfileListResponse)
async def list_profiles():
    """List all available profiles."""
    try:
        profiles = []
        
        for profile_file in PROFILES_DIR.glob("*.yaml"):
            try:
                profile = load_profile_from_file(profile_file.stem)
                profiles.append(profile.metadata)
            except Exception:
                # Skip invalid profiles but don't fail the entire request
                continue
        
        return ProfileListResponse(profiles=profiles)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error listing profiles: {str(e)}"
        )


@router.post("/load", response_model=LoadProfileResponse)
async def load_profile(request: LoadProfileRequest):
    """Load a specific profile by name."""
    profile = load_profile_from_file(request.name)
    return LoadProfileResponse(profile=profile)


@router.post("/save", response_model=SaveProfileResponse)
async def save_profile(request: SaveProfileRequest):
    """Save a profile configuration."""
    name = save_profile_to_file(request.profile, request.overwrite)
    
    action = "updated" if request.overwrite else "created"
    return SaveProfileResponse(
        name=name,
        message=f"Profile '{name}' {action} successfully"
    )


@router.delete("/{name}", response_model=DeleteProfileResponse)
async def delete_profile(name: str):
    """Delete a profile by name."""
    profile_path = get_profile_path(name)
    
    if not profile_path.exists():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Profile '{name}' not found"
        )
    
    try:
        profile_path.unlink()
        return DeleteProfileResponse(
            name=name,
            message=f"Profile '{name}' deleted successfully"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deleting profile '{name}': {str(e)}"
        )


@router.get("/{name}/export", response_model=ExportProfileResponse)
async def export_profile(name: str):
    """Export a profile as YAML content."""
    profile_path = get_profile_path(name)
    
    if not profile_path.exists():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Profile '{name}' not found"
        )
    
    try:
        with open(profile_path, 'r', encoding='utf-8') as f:
            yaml_content = f.read()
        
        return ExportProfileResponse(
            name=name,
            yamlContent=yaml_content
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error exporting profile '{name}': {str(e)}"
        )


@router.post("/import", response_model=ImportProfileResponse)
async def import_profile(request: ImportProfileRequest):
    """Import a profile from YAML content."""
    try:
        # Parse YAML content
        profile_data = yaml.safe_load(request.yamlContent)
        profile = ProfileConfig(**profile_data)
        
        # Save the profile
        name = save_profile_to_file(profile, request.overwrite)
        
        action = "updated" if request.overwrite else "created"
        return ImportProfileResponse(
            name=name,
            message=f"Profile '{name}' {action} successfully from YAML import"
        )
    except yaml.YAMLError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid YAML content: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error importing profile: {str(e)}"
        )


@router.get("/{name}", response_model=LoadProfileResponse)
async def get_profile(name: str):
    """Get a specific profile by name (alternative endpoint)."""
    profile = load_profile_from_file(name)
    return LoadProfileResponse(profile=profile)
"""Configuration management routes."""

from fastapi import APIRouter, HTTPException
from ..config_manager import ConfigManager
from ..models import (
    RunnerConfig,
    CreateCrewRequest,
    CreateCrewResponse,
    ListCrewsResponse,
    GetCrewResponse,
    DeleteCrewResponse,
)

router = APIRouter(prefix="/config", tags=["configuration"])

# Global config manager instance
config_manager = ConfigManager()


@router.get("/", response_model=RunnerConfig)
async def get_config():
    """Get current configuration."""
    return config_manager.load_config()


@router.get("/crews", response_model=ListCrewsResponse)
async def list_crews():
    """List all available crews."""
    crews = config_manager.list_crews()
    return ListCrewsResponse(crews=crews)


@router.get("/crews/{crew_name}", response_model=GetCrewResponse)
async def get_crew(crew_name: str):
    """Get specific crew configuration."""
    crew = config_manager.load_crew(crew_name)
    if not crew:
        raise HTTPException(status_code=404, detail=f"Crew '{crew_name}' not found")
    return GetCrewResponse(crew=crew)


@router.post("/crews", response_model=CreateCrewResponse)
async def create_crew(request: CreateCrewRequest):
    """Create or update a crew configuration."""
    try:
        config_manager.save_crew(request.crew)
        return CreateCrewResponse(
            message=f"Crew '{request.crew.name}' saved successfully",
            crew_name=request.crew.name,
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error saving crew: {str(e)}")


@router.put("/crews/{crew_name}", response_model=CreateCrewResponse)
async def update_crew(crew_name: str, request: CreateCrewRequest):
    """Update a specific crew configuration."""
    if not config_manager.crew_exists(crew_name):
        raise HTTPException(status_code=404, detail=f"Crew '{crew_name}' not found")

    # Ensure the crew name matches the URL parameter
    if request.crew.name != crew_name:
        raise HTTPException(
            status_code=400, detail="Crew name in request body must match URL parameter"
        )

    try:
        config_manager.save_crew(request.crew)
        return CreateCrewResponse(
            message=f"Crew '{crew_name}' updated successfully", crew_name=crew_name
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error updating crew: {str(e)}")


@router.delete("/crews/{crew_name}", response_model=DeleteCrewResponse)
async def delete_crew(crew_name: str):
    """Delete a crew configuration."""
    if not config_manager.delete_crew(crew_name):
        raise HTTPException(status_code=404, detail=f"Crew '{crew_name}' not found")

    return DeleteCrewResponse(
        message=f"Crew '{crew_name}' deleted successfully", crew_name=crew_name
    )


@router.post("/crews/{crew_name}/duplicate", response_model=CreateCrewResponse)
async def duplicate_crew(crew_name: str, new_name: str):
    """Duplicate an existing crew with a new name."""
    original_crew = config_manager.load_crew(crew_name)
    if not original_crew:
        raise HTTPException(status_code=404, detail=f"Crew '{crew_name}' not found")

    if config_manager.crew_exists(new_name):
        raise HTTPException(status_code=400, detail=f"Crew '{new_name}' already exists")

    # Create a copy with the new name
    duplicated_crew = original_crew.model_copy()
    duplicated_crew.name = new_name
    duplicated_crew.description = f"Copy of {original_crew.description}"

    try:
        config_manager.save_crew(duplicated_crew)
        return CreateCrewResponse(
            message=f"Crew '{crew_name}' duplicated as '{new_name}' successfully",
            crew_name=new_name,
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error duplicating crew: {str(e)}")


@router.get("/info")
async def get_config_info():
    """Get configuration directory information."""
    return {
        "config_directory": str(config_manager.get_config_dir()),
        "config_file": str(config_manager.config_file),
        "crews_directory": str(config_manager.crews_dir),
        "available_crews": config_manager.list_crews(),
    }


@router.post("/init")
async def initialize_config():
    """Initialize configuration with default settings and example crew."""
    try:
        # Load/create config
        _ = config_manager.load_config()

        # Create example crew if no crews exist
        crews = config_manager.list_crews()
        if not crews:
            example_crew = config_manager.create_example_crew()
            config_manager.save_crew(example_crew)
            crews = [example_crew.name]

        return {
            "message": "Configuration initialized successfully",
            "config_directory": str(config_manager.get_config_dir()),
            "crews_created": crews,
        }
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error initializing config: {str(e)}"
        )

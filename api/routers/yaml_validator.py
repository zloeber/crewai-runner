"""YAML validation endpoints."""

from fastapi import APIRouter, Depends
import yaml

from ..models import (
    ValidateYAMLRequest,
    ValidateYAMLResponse,
    Workflow,
)
from ..auth import verify_api_key

router = APIRouter(prefix="/yaml", tags=["yaml"])


@router.post("/validate", response_model=ValidateYAMLResponse)
async def validate_yaml(
    request: ValidateYAMLRequest, api_key: str = Depends(verify_api_key)
):
    """Validate a YAML workflow definition."""
    errors = []
    workflow = None
    
    try:
        # Parse YAML
        yaml_data = yaml.safe_load(request.yamlContent)
        
        # Try to validate against Workflow model
        workflow = Workflow(**yaml_data)
        
        return ValidateYAMLResponse(
            valid=True,
            workflow=workflow,
        )
    except yaml.YAMLError as e:
        errors.append(f"YAML parsing error: {str(e)}")
    except Exception as e:
        errors.append(f"Validation error: {str(e)}")
    
    return ValidateYAMLResponse(
        valid=False,
        errors=errors,
    )

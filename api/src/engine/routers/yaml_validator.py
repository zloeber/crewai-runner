"""YAML validation endpoints."""

from fastapi import APIRouter, Depends, Query
import yaml

from models import (
    ValidateYAMLRequest,
    ValidateYAMLResponse,
    Workflow,
)
from auth import verify_api_key
from services.orchestrator_factory import OrchestratorFactory

router = APIRouter(prefix="/yaml", tags=["yaml"])


@router.post("/validate", response_model=ValidateYAMLResponse)
async def validate_yaml(
    request: ValidateYAMLRequest,
    framework: str = Query(default="crewai", description="Framework to validate against"),
    api_key: str = Depends(verify_api_key)
):
    """Validate a YAML workflow definition."""
    errors = []
    workflow = None

    try:
        # Parse YAML
        yaml_data = yaml.safe_load(request.yamlContent)
        
        # Set framework if not in YAML
        if "framework" not in yaml_data:
            yaml_data["framework"] = framework

        # Try to validate against Workflow model
        workflow = Workflow(**yaml_data)
        
        # Use orchestrator for additional validation
        try:
            orchestrator = OrchestratorFactory.get_orchestrator(workflow.framework)
            config = {"workflow": workflow.model_dump()}
            is_valid, validation_errors = await orchestrator.validate(config)
            
            if not is_valid:
                errors.extend(validation_errors)
                return ValidateYAMLResponse(
                    valid=False,
                    errors=errors,
                    workflow=workflow,
                )
        except ValueError as e:
            errors.append(f"Framework error: {str(e)}")
            return ValidateYAMLResponse(
                valid=False,
                errors=errors,
                workflow=workflow,
            )

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

"""Workflow management endpoints."""

from fastapi import APIRouter, Depends, HTTPException
from typing import Dict

from engine.models import (
    StartWorkflowRequest,
    StartWorkflowResponse,
    StopWorkflowRequest,
    StopWorkflowResponse,
    WorkflowStatusResponse,
    AgentStatus,
)
from engine.auth import verify_api_key
from engine.services.orchestrator_factory import OrchestratorFactory

router = APIRouter(prefix="/workflows", tags=["workflows"])

# In-memory storage for workflow state
workflows_db: Dict[str, Dict] = {}


@router.post("/start", response_model=StartWorkflowResponse)
async def start_workflow(
    request: StartWorkflowRequest, api_key: str = Depends(verify_api_key)
):
    """Start a new workflow."""
    # Determine framework to use
    framework = request.framework or request.workflow.framework or "crewai"

    try:
        # Get orchestrator for the specified framework
        orchestrator = OrchestratorFactory.get_orchestrator(framework)

        # Prepare config for orchestrator
        config = {
            "workflow": request.workflow.model_dump(),
            "providerConfig": (
                request.providerConfig.model_dump() if request.providerConfig else None
            ),
        }

        # Execute workflow
        result = await orchestrator.execute(config)
        workflow_id = result.get("workflow_id")

        # Store workflow information
        workflows_db[workflow_id] = {
            "workflow": request.workflow,
            "providerConfig": request.providerConfig,
            "framework": framework,
            "status": "started",
            "agents": (
                [
                    AgentStatus(name=agent.name, status="idle")
                    for agent in request.workflow.agents
                ]
                if request.workflow.agents
                else []
            ),
            "currentTask": None,
            "progress": 0,
            "orchestrator": orchestrator,
        }

        return StartWorkflowResponse(
            workflowId=workflow_id,
            status="started",
            message=f"{framework.upper()} workflow started successfully",
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to start workflow: {str(e)}"
        )


@router.post("/stop", response_model=StopWorkflowResponse)
async def stop_workflow(
    request: StopWorkflowRequest, api_key: str = Depends(verify_api_key)
):
    """Stop a running workflow."""
    workflow_id = request.workflowId

    if workflow_id not in workflows_db:
        raise HTTPException(status_code=404, detail="Workflow not found")

    workflow_data = workflows_db[workflow_id]
    orchestrator = workflow_data.get("orchestrator")

    if orchestrator:
        try:
            await orchestrator.stop(workflow_id)
        except Exception as e:
            raise HTTPException(
                status_code=500, detail=f"Failed to stop workflow: {str(e)}"
            )

    # Update workflow status
    workflows_db[workflow_id]["status"] = "stopped"

    return StopWorkflowResponse(
        workflowId=workflow_id,
        status="stopped",
        message="Workflow stopped successfully",
    )


@router.get("/{workflowId}/status", response_model=WorkflowStatusResponse)
async def get_workflow_status(workflowId: str, api_key: str = Depends(verify_api_key)):
    """Get the status of a workflow."""
    if workflowId not in workflows_db:
        raise HTTPException(status_code=404, detail="Workflow not found")

    workflow_data = workflows_db[workflowId]

    return WorkflowStatusResponse(
        workflowId=workflowId,
        status=workflow_data["status"],
        agents=workflow_data["agents"],
        currentTask=workflow_data["currentTask"],
        progress=workflow_data["progress"],
    )


@router.get("/frameworks")
async def get_supported_frameworks(api_key: str = Depends(verify_api_key)):
    """Get list of supported frameworks."""
    frameworks = OrchestratorFactory.get_supported_frameworks()
    return {
        "frameworks": frameworks,
        "default": "crewai",
    }

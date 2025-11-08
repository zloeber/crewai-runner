"""Workflow management endpoints."""

from fastapi import APIRouter, Depends, HTTPException
from typing import Dict
import uuid

from models import (
    StartWorkflowRequest,
    StartWorkflowResponse,
    StopWorkflowRequest,
    StopWorkflowResponse,
    WorkflowStatusResponse,
    AgentStatus,
)
from auth import verify_api_key

router = APIRouter(prefix="/workflows", tags=["workflows"])

# In-memory storage for workflow state
workflows_db: Dict[str, Dict] = {}


@router.post("/start", response_model=StartWorkflowResponse)
async def start_workflow(
    request: StartWorkflowRequest, api_key: str = Depends(verify_api_key)
):
    """Start a new workflow."""
    workflow_id = str(uuid.uuid4())

    # Store workflow information
    workflows_db[workflow_id] = {
        "workflow": request.workflow,
        "providerConfig": request.providerConfig,
        "status": "started",
        "agents": [
            AgentStatus(name=agent.name, status="idle")
            for agent in request.workflow.agents
        ],
        "currentTask": None,
        "progress": 0,
    }

    # TODO: Integrate with CrewAI to actually start the workflow
    # For now, just return a success response

    return StartWorkflowResponse(
        workflowId=workflow_id,
        status="started",
        message="Workflow started successfully",
    )


@router.post("/stop", response_model=StopWorkflowResponse)
async def stop_workflow(
    request: StopWorkflowRequest, api_key: str = Depends(verify_api_key)
):
    """Stop a running workflow."""
    workflow_id = request.workflowId

    if workflow_id not in workflows_db:
        raise HTTPException(status_code=404, detail="Workflow not found")

    # Update workflow status
    workflows_db[workflow_id]["status"] = "stopped"

    # TODO: Integrate with CrewAI to actually stop the workflow

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

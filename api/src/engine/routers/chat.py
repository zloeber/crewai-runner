"""Chat endpoints for workflow interaction."""

from fastapi import APIRouter, Depends
from datetime import datetime

from models import SendMessageRequest, SendMessageResponse
from auth import verify_api_key

router = APIRouter(prefix="/chat", tags=["chat"])


@router.post("", response_model=SendMessageResponse)
async def send_message(
    request: SendMessageRequest, api_key: str = Depends(verify_api_key)
):
    """Send a message to a running workflow."""
    # TODO: Integrate with CrewAI to send messages to workflows
    # For now, return a mock response

    return SendMessageResponse(
        workflowId=request.workflowId,
        response=f"Received message: {request.message}",
        timestamp=datetime.utcnow().isoformat(),
    )

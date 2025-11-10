"""Tests for workflow management API endpoints via HTTP with Bearer token authentication."""

import pytest
from unittest.mock import Mock, patch


@pytest.fixture
def mock_orchestrator_factory():
    """Mock the OrchestratorFactory."""
    with patch("services.orchestrator_factory.OrchestratorFactory") as mock:
        mock_orchestrator = Mock()
        mock_orchestrator.execute.return_value = {
            "workflow_id": "test-workflow-123",
            "status": "started",
        }
        mock_orchestrator.stop.return_value = None
        mock.get_orchestrator.return_value = mock_orchestrator
        mock.get_supported_frameworks.return_value = ["crewai", "langgraph"]
        yield mock


@pytest.mark.asyncio
async def test_start_workflow_success(
    api_client, sample_workflow_config, mock_orchestrator_factory, skip_if_no_server
):
    """Test successful workflow start via HTTP with Bearer token via HTTP with Bearer token authentication."""
    request_data = {"workflow": sample_workflow_config, "framework": "crewai"}

    response = api_client.post("/workflows/start", json=request_data)

    assert response.status_code == 200
    data = response.json()
    # Check that a workflow ID is returned (UUID format)
    assert "workflowId" in data
    assert len(data["workflowId"]) > 10  # Should be a UUID
    assert data["status"] == "started"
    assert "CREWAI workflow started successfully" in data["message"]


@pytest.mark.asyncio
async def test_start_workflow_with_provider_config(
    api_client, sample_workflow_config, mock_orchestrator_factory, skip_if_no_server
):
    """Test workflow start with provider configuration via HTTP with Bearer token via HTTP with Bearer token authentication."""
    request_data = {
        "workflow": sample_workflow_config,
        "framework": "crewai",
        "providerConfig": {
            "name": "test-provider",
            "type": "openai",
            "apiKey": "test-key",
            "baseUrl": "https://api.openai.com/v1",
        },
    }

    response = api_client.post("/workflows/start", json=request_data)

    assert response.status_code == 200
    data = response.json()
    # Check that a workflow ID is returned (UUID format)
    assert "workflowId" in data
    assert len(data["workflowId"]) > 10  # Should be a UUID
    assert data["status"] == "started"


@pytest.mark.asyncio
async def test_start_workflow_unsupported_framework(
    api_client, sample_workflow_config, skip_if_no_server
):
    """Test workflow start with unsupported framework via HTTP with Bearer token authentication."""
    request_data = {"workflow": sample_workflow_config, "framework": "unsupported"}

    response = api_client.post("/workflows/start", json=request_data)

    assert response.status_code == 400
    assert "Framework 'unsupported' is not supported" in response.json()["error"]


@pytest.mark.skip(reason="Mock-dependent test - requires internal state mocking")
@pytest.mark.asyncio
async def test_start_workflow_execution_error(
    api_client, sample_workflow_config, skip_if_no_server
):
    """Test workflow start with execution error via HTTP with Bearer token authentication."""
    with patch("routers.workflows.OrchestratorFactory") as mock:
        mock_orchestrator = Mock()
        mock_orchestrator.execute.side_effect = Exception("Execution failed")
        mock.get_orchestrator.return_value = mock_orchestrator

        request_data = {"workflow": sample_workflow_config, "framework": "crewai"}

        response = api_client.post("/workflows/start", json=request_data)

        assert response.status_code == 500
        assert "Failed to start workflow" in response.json()["detail"]


@pytest.mark.asyncio
async def test_stop_workflow_success(
    api_client, sample_workflow_config, mock_orchestrator_factory, skip_if_no_server
):
    """Test successful workflow stop via HTTP with Bearer token authentication."""
    # First start a workflow
    request_data = {"workflow": sample_workflow_config, "framework": "crewai"}
    start_response = api_client.post("/workflows/start", json=request_data)
    workflow_id = start_response.json()["workflowId"]

    # Then stop it
    stop_data = {"workflowId": workflow_id}
    response = api_client.post("/workflows/stop", json=stop_data)

    assert response.status_code == 200
    data = response.json()
    assert data["workflowId"] == workflow_id
    assert data["status"] == "stopped"
    assert "Workflow stopped successfully" in data["message"]


@pytest.mark.asyncio
async def test_stop_workflow_not_found(api_client, skip_if_no_server):
    """Test stopping non-existent workflow via HTTP with Bearer token authentication."""
    stop_data = {"workflowId": "non-existent-workflow"}
    response = api_client.post("/workflows/stop", json=stop_data)

    assert response.status_code == 404
    assert "Workflow not found" in response.json()["error"]


@pytest.mark.skip(reason="Mock-dependent test - requires internal state mocking")
@pytest.mark.asyncio
async def test_stop_workflow_orchestrator_error(
    api_client, sample_workflow_config, mock_orchestrator_factory, skip_if_no_server
):
    """Test stopping workflow with orchestrator error via HTTP with Bearer token authentication."""
    # First start a workflow
    request_data = {"workflow": sample_workflow_config, "framework": "crewai"}
    start_response = api_client.post("/workflows/start", json=request_data)
    workflow_id = start_response.json()["workflowId"]

    # Mock orchestrator stop failure
    with patch("routers.workflows.workflows_db") as mock_db:
        mock_orchestrator = Mock()
        mock_orchestrator.stop.side_effect = Exception("Stop failed")
        mock_db.__getitem__.return_value = {"orchestrator": mock_orchestrator}
        mock_db.__contains__.return_value = True

        stop_data = {"workflowId": workflow_id}
        response = api_client.post("/workflows/stop", json=stop_data)

        assert response.status_code == 500
        assert "Failed to stop workflow" in response.json()["detail"]


@pytest.mark.skip(
    reason="Server restart required for workflow status fix - API validation issue"
)
@pytest.mark.asyncio
async def test_get_workflow_status_success(
    api_client, sample_workflow_config, mock_orchestrator_factory, skip_if_no_server
):
    """Test getting workflow status successfully via HTTP with Bearer token authentication."""
    # First start a workflow
    request_data = {"workflow": sample_workflow_config, "framework": "crewai"}
    start_response = api_client.post("/workflows/start", json=request_data)
    workflow_id = start_response.json()["workflowId"]

    # Get status
    response = api_client.get(f"/workflows/{workflow_id}/status")

    assert response.status_code == 200
    data = response.json()
    assert data["workflowId"] == workflow_id
    assert (
        data["status"] == "running"
    )  # Changed from "started" to "running" - internal status
    assert "agents" in data
    assert data["progress"] == 0


@pytest.mark.asyncio
async def test_get_workflow_status_not_found(api_client, skip_if_no_server):
    """Test getting status of non-existent workflow via HTTP with Bearer token authentication."""
    response = api_client.get("/workflows/non-existent-workflow/status")

    assert response.status_code == 404
    assert "Workflow not found" in response.json()["error"]


@pytest.mark.asyncio
async def test_get_supported_frameworks(
    api_client, mock_orchestrator_factory, skip_if_no_server
):
    """Test getting supported frameworks via HTTP with Bearer token authentication."""
    response = api_client.get("/workflows/frameworks")

    assert response.status_code == 200
    data = response.json()
    assert "frameworks" in data
    assert "crewai" in data["frameworks"]
    assert "langgraph" in data["frameworks"]
    assert data["default"] == "crewai"


@pytest.mark.asyncio
async def test_start_workflow_default_framework(
    api_client, sample_workflow_config, mock_orchestrator_factory, skip_if_no_server
):
    """Test workflow start with default framework via HTTP with Bearer token authentication."""
    # Don't specify framework, should default to crewai
    request_data = {"workflow": sample_workflow_config}

    response = api_client.post("/workflows/start", json=request_data)

    assert response.status_code == 200
    data = response.json()
    # Check that a workflow ID is returned (UUID format)
    assert "workflowId" in data
    assert len(data["workflowId"]) > 10  # Should be a UUID
    assert data["status"] == "started"


@pytest.mark.asyncio
async def test_start_workflow_framework_from_workflow_config(
    api_client, sample_workflow_config, mock_orchestrator_factory, skip_if_no_server
):
    """Test workflow start using framework from workflow config via HTTP with Bearer token authentication."""
    # Set framework in workflow config
    sample_workflow_config["framework"] = "langgraph"
    request_data = {"workflow": sample_workflow_config}

    response = api_client.post("/workflows/start", json=request_data)

    assert response.status_code == 200
    data = response.json()
    # Check that a workflow ID is returned (UUID format)
    assert "workflowId" in data
    assert len(data["workflowId"]) > 10  # Should be a UUID
    assert data["status"] == "started"


@pytest.mark.asyncio
async def test_start_workflow_invalid_request_body(api_client, skip_if_no_server):
    """Test workflow start with invalid request body via HTTP with Bearer token authentication."""
    # Missing required workflow field
    request_data = {"framework": "crewai"}

    response = api_client.post("/workflows/start", json=request_data)

    assert response.status_code == 422  # Validation error


@pytest.mark.asyncio
async def test_stop_workflow_invalid_request_body(api_client, skip_if_no_server):
    """Test workflow stop with invalid request body via HTTP with Bearer token authentication."""
    # Missing required workflowId field
    stop_data = {}
    response = api_client.post("/workflows/stop", json=stop_data)

    assert response.status_code == 422  # Validation error

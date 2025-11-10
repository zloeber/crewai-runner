"""Tests for chat API endpoints via HTTP with Bearer token authentication."""

import pytest
from datetime import datetime


@pytest.mark.asyncio
async def test_send_message_success(api_client, skip_if_no_server):
    """Test sending a message successfully via HTTP with Bearer token authentication."""
    request_data = {"workflowId": "test-workflow-123", "message": "Hello, workflow!"}

    response = api_client.post("/chat", json=request_data)

    assert response.status_code == 200
    data = response.json()
    assert data["workflowId"] == "test-workflow-123"
    assert "Received message: Hello, workflow!" in data["response"]
    assert "timestamp" in data

    # Verify timestamp is valid ISO format
    timestamp = datetime.fromisoformat(data["timestamp"])
    assert isinstance(timestamp, datetime)


@pytest.mark.asyncio
async def test_send_message_empty_message(api_client, skip_if_no_server):
    """Test sending an empty message via HTTP with Bearer token authentication."""
    request_data = {"workflowId": "test-workflow-123", "message": ""}

    response = api_client.post("/chat", json=request_data)

    assert response.status_code == 200
    data = response.json()
    assert data["workflowId"] == "test-workflow-123"
    assert "Received message: " in data["response"]


@pytest.mark.asyncio
async def test_send_message_long_message(api_client, skip_if_no_server):
    """Test sending a long message via HTTP with Bearer token authentication."""
    long_message = "This is a very long message " * 100
    request_data = {"workflowId": "test-workflow-123", "message": long_message}

    response = api_client.post("/chat", json=request_data)

    assert response.status_code == 200
    data = response.json()
    assert data["workflowId"] == "test-workflow-123"
    assert long_message in data["response"]


@pytest.mark.asyncio
async def test_send_message_special_characters(api_client, skip_if_no_server):
    """Test sending a message with special characters via HTTP with Bearer token authentication."""
    special_message = "Hello! @#$%^&*()_+ 你好 🚀 \n\t"
    request_data = {"workflowId": "test-workflow-123", "message": special_message}

    response = api_client.post("/chat", json=request_data)

    assert response.status_code == 200
    data = response.json()
    assert data["workflowId"] == "test-workflow-123"
    assert special_message in data["response"]


@pytest.mark.asyncio
async def test_send_message_missing_workflow_id(api_client, skip_if_no_server):
    """Test sending a message without workflow ID via HTTP with Bearer token authentication."""
    request_data = {"message": "Hello, workflow!"}

    response = api_client.post("/chat", json=request_data)

    assert response.status_code == 422  # Validation error


@pytest.mark.asyncio
async def test_send_message_missing_message(api_client, skip_if_no_server):
    """Test sending a request without message via HTTP with Bearer token authentication."""
    request_data = {"workflowId": "test-workflow-123"}

    response = api_client.post("/chat", json=request_data)

    assert response.status_code == 422  # Validation error


@pytest.mark.asyncio
async def test_send_message_invalid_workflow_id_type(api_client, skip_if_no_server):
    """Test sending a message with invalid workflow ID type via HTTP with Bearer token authentication."""
    request_data = {
        "workflowId": 123,  # Should be string
        "message": "Hello, workflow!",
    }

    response = api_client.post("/chat", json=request_data)

    assert response.status_code == 422  # Validation error


@pytest.mark.asyncio
async def test_send_message_invalid_message_type(api_client, skip_if_no_server):
    """Test sending a message with invalid message type via HTTP with Bearer token authentication."""
    request_data = {
        "workflowId": "test-workflow-123",
        "message": 12345,  # Should be string
    }

    response = api_client.post("/chat", json=request_data)

    assert response.status_code == 422  # Validation error


@pytest.mark.asyncio
async def test_send_message_empty_request_body(api_client, skip_if_no_server):
    """Test sending an empty request body via HTTP with Bearer token authentication."""
    response = api_client.post("/chat", json={})

    assert response.status_code == 422  # Validation error


@pytest.mark.asyncio
async def test_send_message_timestamp_format(api_client, skip_if_no_server):
    """Test that the timestamp is in correct ISO format via HTTP with Bearer token authentication."""
    request_data = {"workflowId": "test-workflow-123", "message": "Test timestamp"}

    response = api_client.post("/chat", json=request_data)

    assert response.status_code == 200
    data = response.json()

    # Parse timestamp and verify it's valid
    timestamp_str = data["timestamp"]
    timestamp = datetime.fromisoformat(timestamp_str)

    # Verify it's recent (within last minute)
    now = datetime.utcnow()
    time_diff = abs((now - timestamp).total_seconds())
    assert time_diff < 60  # Less than 1 minute difference


@pytest.mark.asyncio
async def test_send_message_multiple_requests(api_client, skip_if_no_server):
    """Test sending multiple messages in sequence via HTTP with Bearer token authentication."""
    messages = ["First message", "Second message", "Third message"]

    responses = []
    for i, message in enumerate(messages):
        request_data = {"workflowId": f"test-workflow-{i}", "message": message}

        response = api_client.post("/chat", json=request_data)
        assert response.status_code == 200
        responses.append(response.json())

    # Verify all responses are correct
    for i, (message, response_data) in enumerate(zip(messages, responses)):
        assert response_data["workflowId"] == f"test-workflow-{i}"
        assert message in response_data["response"]
        assert "timestamp" in response_data


@pytest.mark.asyncio
async def test_send_message_concurrent_requests(api_client, skip_if_no_server):
    """Test handling concurrent message requests via HTTP with Bearer token authentication."""
    import asyncio

    async def send_message(workflow_id: str, message: str):
        request_data = {"workflowId": workflow_id, "message": message}

        response = api_client.post("/chat", json=request_data)
        return response.json()

    # Send multiple messages concurrently
    tasks = [send_message(f"workflow-{i}", f"Message {i}") for i in range(5)]

    results = await asyncio.gather(*tasks)

    # Verify all responses are correct
    for i, result in enumerate(results):
        assert result["workflowId"] == f"workflow-{i}"
        assert f"Message {i}" in result["response"]

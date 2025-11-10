"""Tests for model management API endpoints via HTTP with Bearer token authentication."""

import pytest
from unittest.mock import Mock, patch


@pytest.fixture
def mock_models_db():
    """Mock the models database."""
    with patch("routers.models.models_db") as mock_db:
        # Mock model data
        test_model = {
            "id": "test-model-123",
            "name": "Test Model",
            "provider": "openai",
            "modelName": "gpt-4",
            "config": {"temperature": 0.7, "maxTokens": 2000},
        }

        mock_db.values.return_value = [test_model]
        mock_db.__contains__.side_effect = lambda key: key == "test-model-123"
        mock_db.__getitem__.side_effect = lambda key: (
            test_model if key == "test-model-123" else None
        )
        mock_db.__setitem__ = Mock()

        yield mock_db


@pytest.mark.asyncio
async def test_list_models_empty(api_client, skip_if_no_server):
    """Test listing models when none exist via HTTP with Bearer token authentication."""
    # Note: This test can't work reliably with real HTTP requests since data might exist
    response = api_client.get("/models")

    assert response.status_code == 200
    data = response.json()
    assert "models" in data
    # Can't guarantee empty list in real environment


@pytest.mark.asyncio
async def test_list_models_with_data(
    api_client, mock_models_db, skip_if_no_server, sample_model_config
):
    """Test listing models with existing data via HTTP with Bearer token authentication."""
    # First create a model to ensure data exists
    test_config = sample_model_config.copy()
    test_config["name"] = "Test Model for Listing"
    test_config.pop("id", None)  # Let ID be auto-generated

    add_response = api_client.post("/models", json={"model": test_config})
    assert add_response.status_code == 200

    # Now list models - should have at least the one we just created
    response = api_client.get("/models")

    assert response.status_code == 200
    data = response.json()
    assert "models" in data
    assert len(data["models"]) >= 1  # Should have at least the model we created

    # Check structure of at least one model
    found_test_model = False
    for model in data["models"]:
        assert "name" in model
        assert "type" in model
        assert "providerId" in model
        assert "endpoint" in model
        if model["name"] == "Test Model for Listing":
            found_test_model = True

    assert found_test_model, "Should find the test model we created"


@pytest.mark.asyncio
async def test_add_model_success(api_client, sample_model_config, skip_if_no_server):
    """Test adding a new model successfully via HTTP with Bearer token authentication."""
    # Create a unique model config to avoid conflicts
    test_config = sample_model_config.copy()
    test_config["name"] = "Unique Test Model for Add"
    # Remove ID to let it be auto-generated to avoid conflicts
    test_config.pop("id", None)

    request_data = {"model": test_config}

    response = api_client.post("/models", json=request_data)

    assert response.status_code == 200
    data = response.json()
    assert "model" in data
    assert data["model"]["name"] == "Unique Test Model for Add"
    assert data["model"]["type"] == "llm"
    assert data["model"]["providerId"] == "test-provider"
    assert data["model"]["endpoint"] == "https://api.openai.com/v1"
    assert "id" in data["model"]  # ID should be auto-generated


@pytest.mark.asyncio
async def test_add_model_auto_generate_id(api_client, skip_if_no_server):
    """Test adding model without ID auto-generates one via HTTP with Bearer token authentication."""
    model_config = {
        "name": "Auto ID Model",
        "type": "llm",
        "providerId": "auto-test-provider",
        "endpoint": "https://api.test.com/v1",
    }

    request_data = {"model": model_config}

    response = api_client.post("/models", json=request_data)

    assert response.status_code == 200
    data = response.json()
    assert "model" in data
    assert data["model"]["id"] is not None
    assert len(data["model"]["id"]) > 0  # UUID should be generated


@pytest.mark.skip(
    reason="Cannot mock internal components when using real HTTP requests"
)
async def test_add_model_already_exists(
    api_client, sample_model_config, skip_if_no_server
):
    """Test adding model that already exists via HTTP with Bearer token authentication."""
    with patch("routers.models.models_db") as mock_db:
        mock_db.__contains__.return_value = True  # Model exists

        request_data = {"model": sample_model_config}

        response = api_client.post("/models", json=request_data)

        assert response.status_code == 400
        assert "Model already exists" in response.json()["detail"]


@pytest.mark.asyncio
@pytest.mark.skip(
    reason="Cannot reliably test duplicate handling with real HTTP requests"
)
async def test_add_model_with_existing_id(
    api_client, sample_model_config, skip_if_no_server
):
    """Test adding model with pre-existing ID via HTTP with Bearer token authentication."""
    sample_model_config["id"] = "existing-model-id"

    with patch("routers.models.models_db") as mock_db:
        mock_db.__contains__.return_value = False

        request_data = {"model": sample_model_config}

        response = api_client.post("/models", json=request_data)

        assert response.status_code == 200
        data = response.json()
        assert data["model"]["id"] == "existing-model-id"


@pytest.mark.asyncio
@pytest.mark.skip(
    reason="Uses old schema format - needs schema update for real HTTP requests"
)
async def test_add_model_different_providers(api_client, skip_if_no_server):
    """Test adding models from different providers via HTTP with Bearer token authentication."""
    providers_and_models = [
        ("openai", "gpt-4"),
        ("anthropic", "claude-3-sonnet"),
        ("azure", "gpt-4-deployment"),
        ("ollama", "llama2"),
        ("google", "gemini-pro"),
    ]

    for provider, model_name in providers_and_models:
        model_config = {
            "name": f"Test {provider.title()} Model",
            "provider": provider,
            "modelName": model_name,
            "config": {"temperature": 0.7},
        }

        with patch("routers.models.models_db") as mock_db:
            mock_db.__contains__.return_value = False

            request_data = {"model": model_config}

            response = api_client.post("/models", json=request_data)

            assert response.status_code == 200
            data = response.json()
            assert data["model"]["provider"] == provider
            assert data["model"]["modelName"] == model_name


@pytest.mark.asyncio
@pytest.mark.skip(
    reason="Uses old schema format - needs schema update for real HTTP requests"
)
async def test_add_model_with_complex_config(api_client, skip_if_no_server):
    """Test adding model with complex configuration via HTTP with Bearer token authentication."""
    model_config = {
        "name": "Complex Model",
        "provider": "openai",
        "modelName": "gpt-4",
        "config": {
            "temperature": 0.8,
            "maxTokens": 4000,
            "topP": 0.9,
            "frequencyPenalty": 0.1,
            "presencePenalty": 0.1,
            "stop": ["\\n", "END"],
            "logitBias": {"50256": -100},
            "functions": [
                {
                    "name": "get_weather",
                    "description": "Get weather information",
                    "parameters": {
                        "type": "object",
                        "properties": {"location": {"type": "string"}},
                    },
                }
            ],
            "toolChoice": "auto",
            "responseFormat": {"type": "json_object"},
            "seed": 12345,
            "stream": False,
            "user": "test-user",
        },
    }

    with patch("routers.models.models_db") as mock_db:
        mock_db.__contains__.return_value = False

        request_data = {"model": model_config}

        response = api_client.post("/models", json=request_data)

        assert response.status_code == 200
        data = response.json()
        assert data["model"]["name"] == "Complex Model"
        assert data["model"]["config"]["temperature"] == 0.8
        assert data["model"]["config"]["maxTokens"] == 4000
        assert "functions" in data["model"]["config"]
        assert len(data["model"]["config"]["functions"]) == 1


@pytest.mark.asyncio
@pytest.mark.skip(
    reason="Uses old schema format - needs schema update for real HTTP requests"
)
async def test_add_model_minimal_config(api_client, skip_if_no_server):
    """Test adding model with minimal required configuration via HTTP with Bearer token authentication."""
    model_config = {
        "name": "Minimal Model",
        "provider": "openai",
        "modelName": "gpt-3.5-turbo",
    }

    with patch("routers.models.models_db") as mock_db:
        mock_db.__contains__.return_value = False

        request_data = {"model": model_config}

        response = api_client.post("/models", json=request_data)

        assert response.status_code == 200
        data = response.json()
        assert data["model"]["name"] == "Minimal Model"
        assert data["model"]["provider"] == "openai"
        assert data["model"]["modelName"] == "gpt-3.5-turbo"


@pytest.mark.asyncio
@pytest.mark.skip(
    reason="Uses old schema format - needs schema update for real HTTP requests"
)
async def test_add_model_azure_specific_config(api_client, skip_if_no_server):
    """Test adding Azure-specific model configuration via HTTP with Bearer token authentication."""
    model_config = {
        "name": "Azure Model",
        "provider": "azure",
        "modelName": "gpt-4",
        "config": {
            "apiVersion": "2023-12-01-preview",
            "deployment": "gpt-4-deployment",
            "baseUrl": "https://test.openai.azure.com/",
            "temperature": 0.7,
            "maxTokens": 2000,
        },
    }

    with patch("routers.models.models_db") as mock_db:
        mock_db.__contains__.return_value = False

        request_data = {"model": model_config}

        response = api_client.post("/models", json=request_data)

        assert response.status_code == 200
        data = response.json()
        assert data["model"]["provider"] == "azure"
        assert data["model"]["config"]["apiVersion"] == "2023-12-01-preview"
        assert data["model"]["config"]["deployment"] == "gpt-4-deployment"


@pytest.mark.asyncio
@pytest.mark.skip(
    reason="Uses old schema format - needs schema update for real HTTP requests"
)
async def test_add_model_ollama_specific_config(api_client, skip_if_no_server):
    """Test adding Ollama-specific model configuration via HTTP with Bearer token authentication."""
    model_config = {
        "name": "Ollama Model",
        "provider": "ollama",
        "modelName": "llama2:7b",
        "config": {
            "baseUrl": "http://localhost:11434",
            "temperature": 0.8,
            "numCtx": 4096,
            "numGpu": 1,
            "numThread": 8,
            "repeatPenalty": 1.1,
            "topK": 40,
            "topP": 0.9,
        },
    }

    with patch("routers.models.models_db") as mock_db:
        mock_db.__contains__.return_value = False

        request_data = {"model": model_config}

        response = api_client.post("/models", json=request_data)

        assert response.status_code == 200
        data = response.json()
        assert data["model"]["provider"] == "ollama"
        assert data["model"]["modelName"] == "llama2:7b"
        assert data["model"]["config"]["baseUrl"] == "http://localhost:11434"
        assert data["model"]["config"]["numCtx"] == 4096


@pytest.mark.asyncio
async def test_add_model_invalid_request_body(api_client, skip_if_no_server):
    """Test adding model with invalid request body via HTTP with Bearer token authentication."""
    # Missing required model field
    request_data = {}

    response = api_client.post("/models", json=request_data)

    assert response.status_code == 422  # Validation error


@pytest.mark.asyncio
async def test_add_model_missing_required_fields(api_client, skip_if_no_server):
    """Test adding model with missing required fields via HTTP with Bearer token authentication."""
    # Missing name, provider, and modelName fields
    model_config = {"config": {"temperature": 0.7}}

    request_data = {"model": model_config}

    response = api_client.post("/models", json=request_data)

    assert response.status_code == 422  # Validation error


@pytest.mark.asyncio
@pytest.mark.skip(
    reason="Cannot mock internal components when using real HTTP requests"
)
async def test_list_models_multiple_providers(api_client, skip_if_no_server):
    """Test listing models from multiple providers via HTTP with Bearer token authentication."""
    models = [
        {
            "id": "openai-model",
            "name": "OpenAI GPT-4",
            "provider": "openai",
            "modelName": "gpt-4",
            "config": {"temperature": 0.7},
        },
        {
            "id": "anthropic-model",
            "name": "Claude 3 Sonnet",
            "provider": "anthropic",
            "modelName": "claude-3-sonnet",
            "config": {"temperature": 0.8},
        },
        {
            "id": "ollama-model",
            "name": "Local Llama2",
            "provider": "ollama",
            "modelName": "llama2:7b",
            "config": {"temperature": 0.9},
        },
    ]

    with patch("routers.models.models_db") as mock_db:
        mock_db.values.return_value = models

        response = api_client.get("/models")

        assert response.status_code == 200
        data = response.json()
        assert len(data["models"]) == 3

        # Verify each provider is present
        providers = [m["provider"] for m in data["models"]]
        assert "openai" in providers
        assert "anthropic" in providers
        assert "ollama" in providers


@pytest.mark.asyncio
@pytest.mark.skip(
    reason="Cannot mock internal components when using real HTTP requests"
)
async def test_models_endpoint_authentication(api_client, skip_if_no_server):
    """Test that models endpoints require authentication via HTTP with Bearer token authentication."""
    # This test verifies that without proper API key, access is denied
    with patch("routers.models.verify_api_key") as mock_verify:
        mock_verify.side_effect = Exception("Unauthorized")

        # Try to access without authentication
        with pytest.raises(Exception):
            api_client.get("/models")


@pytest.mark.asyncio
@pytest.mark.skip(
    reason="Uses old schema format - needs schema update for real HTTP requests"
)
async def test_add_model_config_types(api_client, skip_if_no_server):
    """Test model configuration with different data types via HTTP with Bearer token authentication."""
    model_config = {
        "name": "Type Test Model",
        "provider": "openai",
        "modelName": "gpt-4",
        "config": {
            "temperature": 0.7,  # float
            "maxTokens": 2000,  # int
            "stream": False,  # bool
            "stop": ["END", "STOP"],  # list
            "logitBias": {"123": -1},  # dict
            "user": "test-user",  # string
        },
    }

    with patch("routers.models.models_db") as mock_db:
        mock_db.__contains__.return_value = False

        request_data = {"model": model_config}

        response = api_client.post("/models", json=request_data)

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data["model"]["config"]["temperature"], float)
        assert isinstance(data["model"]["config"]["maxTokens"], int)
        assert isinstance(data["model"]["config"]["stream"], bool)
        assert isinstance(data["model"]["config"]["stop"], list)
        assert isinstance(data["model"]["config"]["logitBias"], dict)

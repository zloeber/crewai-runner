"""Test configuration for pytest."""

import sys
import os
import pytest
import requests
from pathlib import Path
from unittest.mock import Mock, patch

# Add the src/engine directory to Python path (same as run_server.py)
engine_path = Path(__file__).parent.parent / "src" / "engine"
sys.path.insert(0, str(engine_path))

# Set environment variables for testing
os.environ.setdefault("CREWAI_API_KEY", "test-api-key")
os.environ.setdefault("ENGINE_API_KEY", "test-api-key")  # For the settings
os.environ.setdefault("OPENAI_API_KEY", "test-key")
os.environ.setdefault("ANTHROPIC_API_KEY", "test-key")

# Test API configuration
TEST_API_BASE_URL = "http://localhost:8000/api"
TEST_API_KEY = "test-api-key"


@pytest.fixture(autouse=True)
def mock_dependencies():
    """Mock external dependencies that might not be available during testing."""
    with patch(
        "engine.services.orchestrator_factory.OrchestratorFactory"
    ) as mock_factory:
        mock_orchestrator = Mock()
        mock_orchestrator.execute.return_value = {
            "workflow_id": "test-123",
            "status": "started",
        }
        mock_orchestrator.stop.return_value = None
        mock_orchestrator.validate.return_value = (True, None)
        mock_factory.get_orchestrator.return_value = mock_orchestrator
        mock_factory.get_supported_frameworks.return_value = ["crewai", "langgraph"]

        with patch("services.mcp_manager.mcp_manager") as mock_mcp:
            mock_mcp.list_servers.return_value = []
            mock_mcp.add_server.return_value = {"id": "test-server", "name": "test"}

            with patch("config_manager.ConfigManager") as mock_config:
                mock_config_instance = Mock()
                mock_config_instance.load_config.return_value = {"version": "1.0.0"}
                mock_config_instance.list_crews.return_value = []
                mock_config.return_value = mock_config_instance

                yield


@pytest.fixture
def mock_verify_api_key():
    """Mock the API key verification dependency."""
    with patch("auth.verify_api_key") as mock:
        mock.return_value = "test_api_key"
        yield mock


@pytest.fixture
def api_client(mock_verify_api_key, mock_dependencies):
    """Create an HTTP client for making authorized API requests."""

    class HTTPAPIClient:
        """HTTP client that mimics TestClient interface but uses real HTTP requests with Bearer auth."""

        def __init__(self, base_url: str, api_key: str):
            self.base_url = base_url
            self.headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            }
            self.session = requests.Session()
            self.session.headers.update(self.headers)

        def get(self, path: str, **kwargs):
            """Make GET request with Bearer token."""
            url = f"{self.base_url}{path}" if not path.startswith("http") else path
            return self.session.get(url, **kwargs)

        def post(self, path: str, **kwargs):
            """Make POST request with Bearer token."""
            url = f"{self.base_url}{path}" if not path.startswith("http") else path
            return self.session.post(url, **kwargs)

        def put(self, path: str, **kwargs):
            """Make PUT request with Bearer token."""
            url = f"{self.base_url}{path}" if not path.startswith("http") else path
            return self.session.put(url, **kwargs)

        def delete(self, path: str, **kwargs):
            """Make DELETE request with Bearer token."""
            url = f"{self.base_url}{path}" if not path.startswith("http") else path
            return self.session.delete(url, **kwargs)

    return HTTPAPIClient(TEST_API_BASE_URL, TEST_API_KEY)


@pytest.fixture(scope="session")
def api_server_check():
    """Check if the API server is running for HTTP tests."""
    try:
        response = requests.get(
            f"{TEST_API_BASE_URL.replace('/api', '')}/api/docs", timeout=5
        )
        if response.status_code == 200:
            return TEST_API_BASE_URL
        else:
            pytest.skip("API server is not responding correctly")
    except requests.exceptions.RequestException:
        pytest.skip(
            "API server is not running. Start with: cd api && ENGINE_API_KEY=test-api-key python run_server.py"
        )


@pytest.fixture
def skip_if_no_server(api_server_check):
    """Fixture that skips tests if API server is not available."""
    return api_server_check


@pytest.fixture
def sample_workflow_config():
    """Sample workflow configuration for testing."""
    return {
        "name": "Test Workflow",
        "framework": "crewai",
        "agents": [
            {
                "name": "test_agent",
                "role": "Test Role",
                "goal": "Test Goal",
                "backstory": "Test Backstory",
                "model": "gpt-4",
            }
        ],
        "tasks": [
            {
                "name": "test_task",
                "description": "Test Description",
                "expectedOutput": "Test Output",
                "agent": "test_agent",
            }
        ],
    }


@pytest.fixture
def sample_profile_config():
    """Sample profile configuration for testing."""
    return {
        "metadata": {
            "name": "test-profile",
            "description": "Test profile description",
            "version": "1.0.0",
            "created": "2024-01-01T00:00:00Z",
        },
        "llmConfig": {
            "provider": "openai",
            "model": "gpt-4",
            "apiKey": "test-key",
            "baseUrl": "https://api.openai.com/v1",
        },
        "agentDefaults": {"verbose": True, "memoryEnabled": True},
    }


@pytest.fixture
def sample_mcp_server_config():
    """Sample MCP server configuration for testing."""
    return {
        "name": "test-server",
        "description": "Test MCP server",
        "transport": {
            "type": "stdio",
            "command": "npx",
            "args": ["-y", "@modelcontextprotocol/server-filesystem", "/tmp"],
        },
        "env": {"TEST_VAR": "test_value"},
        "enabled": True,
    }


@pytest.fixture
def sample_provider_config():
    """Sample provider configuration for testing."""
    return {
        "id": "test-provider",
        "name": "Test Provider",
        "type": "openai",
        "config": {"apiKey": "test-key", "baseUrl": "https://api.openai.com/v1"},
    }


@pytest.fixture
def sample_model_config():
    """Sample model configuration for testing."""
    return {
        "id": "test-model",
        "name": "Test Model",
        "type": "llm",
        "providerId": "test-provider",
        "endpoint": "https://api.openai.com/v1",
    }

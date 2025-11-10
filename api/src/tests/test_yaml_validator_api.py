"""Tests for YAML validation API endpoints via HTTP with Bearer token authentication."""

import pytest
import yaml
from unittest.mock import Mock, patch


@pytest.fixture
def mock_orchestrator_factory():
    """Mock the OrchestratorFactory for validation tests."""
    with patch("routers.yaml_validator.OrchestratorFactory") as mock:
        mock_orchestrator = Mock()
        mock_orchestrator.validate.return_value = (True, None)  # Valid by default
        mock.get_orchestrator.return_value = mock_orchestrator
        yield mock


@pytest.fixture
def valid_yaml_content():
    """Valid YAML workflow content for testing."""
    return """
name: Test Workflow
framework: crewai
agents:
  - name: test_agent
    role: Test Role
    goal: Test Goal
    backstory: Test Backstory
    model: gpt-4
tasks:
  - name: test_task
    description: Test Description
    expectedOutput: Test Output
    agent: test_agent
"""


@pytest.fixture
def invalid_yaml_content():
    """Invalid YAML content for testing."""
    return """
name: Test Workflow
framework: crewai
agents:
  - name: test_agent
    role: Test Role
    # Missing required fields
tasks:
  - name: test_task
    # Missing required fields
"""


@pytest.mark.asyncio
async def test_validate_yaml_success(api_client, valid_yaml_content, mock_orchestrator_factory, skip_if_no_server):
    """Test successful YAML validation via HTTP with Bearer token authentication."""
    request_data = {"yamlContent": valid_yaml_content}
    
    response = api_client.post("/yaml/validate", json=request_data)
    
    assert response.status_code == 200
    data = response.json()
    assert data["valid"] is True
    assert "workflow" in data
    assert data["workflow"]["name"] == "Test Workflow"
    assert data["workflow"]["framework"] == "crewai"


@pytest.mark.asyncio
async def test_validate_yaml_with_framework_parameter(api_client, mock_orchestrator_factory, skip_if_no_server):
    """Test YAML validation with framework query parameter via HTTP with Bearer token authentication."""
    yaml_content = """
name: Test Workflow
agents:
  - name: test_agent
    role: Test Role
    goal: Test Goal
    backstory: Test Backstory
tasks:
  - name: test_task
    description: Test Description
    expectedOutput: Test Output
    agent: test_agent
"""
    
    request_data = {"yamlContent": yaml_content}
    
    response = api_client.post("/yaml/validate?framework=langgraph", json=request_data)
    
    assert response.status_code == 200
    data = response.json()
    assert data["valid"] is True
    assert data["workflow"]["framework"] == "langgraph"


@pytest.mark.asyncio
async def test_validate_yaml_framework_in_yaml_overrides_parameter(api_client, valid_yaml_content, mock_orchestrator_factory, skip_if_no_server):
    """Test that framework in YAML content takes precedence over query parameter via HTTP with Bearer token authentication."""
    request_data = {"yamlContent": valid_yaml_content}
    
    response = api_client.post("/yaml/validate?framework=langgraph", json=request_data)
    
    assert response.status_code == 200
    data = response.json()
    assert data["valid"] is True
    assert data["workflow"]["framework"] == "crewai"  # From YAML, not query param


@pytest.mark.asyncio
async def test_validate_yaml_invalid_yaml_syntax(api_client, skip_if_no_server):
    """Test validation with invalid YAML syntax via HTTP with Bearer token authentication."""
    invalid_yaml = """
name: Test Workflow
framework: crewai
agents:
  - name: test_agent
    role: Test Role
    # Invalid YAML syntax below
    invalid: yaml: content: [
"""
    
    request_data = {"yamlContent": invalid_yaml}
    
    response = api_client.post("/yaml/validate", json=request_data)
    
    assert response.status_code == 200
    data = response.json()
    assert data["valid"] is False
    assert "errors" in data
    assert any("YAML parsing error" in error for error in data["errors"])


@pytest.mark.asyncio
async def test_validate_yaml_orchestrator_validation_failure(api_client, valid_yaml_content, skip_if_no_server):
    """Test validation failure from orchestrator via HTTP with Bearer token authentication."""
    with patch("routers.yaml_validator.OrchestratorFactory") as mock:
        mock_orchestrator = Mock()
        mock_orchestrator.validate.return_value = (False, ["Missing required field: goal"])
        mock.get_orchestrator.return_value = mock_orchestrator
        
        request_data = {"yamlContent": valid_yaml_content}
        
        response = api_client.post("/yaml/validate", json=request_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["valid"] is False
        assert "errors" in data
        assert "Missing required field: goal" in data["errors"]


@pytest.mark.asyncio
async def test_validate_yaml_unsupported_framework(api_client, valid_yaml_content, skip_if_no_server):
    """Test validation with unsupported framework via HTTP with Bearer token authentication."""
    with patch("routers.yaml_validator.OrchestratorFactory") as mock:
        mock.get_orchestrator.side_effect = ValueError("Framework 'unsupported' not supported")
        
        yaml_content = valid_yaml_content.replace("framework: crewai", "framework: unsupported")
        request_data = {"yamlContent": yaml_content}
        
        response = api_client.post("/yaml/validate", json=request_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["valid"] is False
        assert "errors" in data
        assert any("Framework error" in error for error in data["errors"])


@pytest.mark.asyncio
async def test_validate_yaml_pydantic_validation_error(api_client, skip_if_no_server):
    """Test validation with Pydantic model validation error via HTTP with Bearer token authentication."""
    # YAML that parses but fails Pydantic validation
    invalid_workflow_yaml = """
name: Test Workflow
framework: crewai
agents:
  - name: test_agent
    # Missing required fields like role, goal, backstory
tasks:
  - name: test_task
    # Missing required fields like description, expectedOutput
"""
    
    request_data = {"yamlContent": invalid_workflow_yaml}
    
    response = api_client.post("/yaml/validate", json=request_data)
    
    assert response.status_code == 200
    data = response.json()
    assert data["valid"] is False
    assert "errors" in data


@pytest.mark.asyncio
async def test_validate_yaml_empty_content(api_client, skip_if_no_server):
    """Test validation with empty YAML content via HTTP with Bearer token authentication."""
    request_data = {"yamlContent": ""}
    
    response = api_client.post("/yaml/validate", json=request_data)
    
    assert response.status_code == 200
    data = response.json()
    assert data["valid"] is False
    assert "errors" in data


@pytest.mark.asyncio
async def test_validate_yaml_null_content(api_client, skip_if_no_server):
    """Test validation with null YAML content via HTTP with Bearer token authentication."""
    request_data = {"yamlContent": "null"}
    
    response = api_client.post("/yaml/validate", json=request_data)
    
    assert response.status_code == 200
    data = response.json()
    assert data["valid"] is False
    assert "errors" in data


@pytest.mark.asyncio
async def test_validate_yaml_complex_workflow(api_client, mock_orchestrator_factory, skip_if_no_server):
    """Test validation of complex workflow with multiple agents and tasks via HTTP with Bearer token authentication."""
    complex_yaml = """
name: Complex Marketing Campaign
framework: crewai
agents:
  - name: researcher
    role: Market Researcher
    goal: Research market trends and opportunities
    backstory: You are an experienced market researcher with deep industry knowledge
    model: gpt-4
    tools:
      - web_search
      - data_analysis
    memory: true
    verbose: true
  - name: writer
    role: Content Writer
    goal: Create compelling marketing content
    backstory: You are a creative writer specialized in marketing content
    model: gpt-3.5-turbo
    tools:
      - content_generator
    memory: true
  - name: reviewer
    role: Content Reviewer
    goal: Review and improve content quality
    backstory: You are a senior editor with years of experience
    model: gpt-4
    verbose: true
tasks:
  - name: market_research
    description: Conduct comprehensive market research
    expectedOutput: Detailed market analysis report
    agent: researcher
    tools:
      - web_search
      - competitor_analysis
  - name: content_creation
    description: Create marketing content based on research
    expectedOutput: Draft marketing materials
    agent: writer
    context:
      - market_research
  - name: content_review
    description: Review and refine the marketing content
    expectedOutput: Final polished marketing content
    agent: reviewer
    context:
      - content_creation
    outputFile: final_content.md
"""
    
    request_data = {"yamlContent": complex_yaml}
    
    response = api_client.post("/yaml/validate", json=request_data)
    
    assert response.status_code == 200
    data = response.json()
    assert data["valid"] is True
    assert data["workflow"]["name"] == "Complex Marketing Campaign"
    assert len(data["workflow"]["agents"]) == 3
    assert len(data["workflow"]["tasks"]) == 3


@pytest.mark.asyncio
async def test_validate_yaml_langgraph_workflow(api_client, mock_orchestrator_factory, skip_if_no_server):
    """Test validation of LangGraph workflow via HTTP with Bearer token authentication."""
    langgraph_yaml = """
name: LangGraph Workflow
framework: langgraph
nodes:
  - id: start
    type: start
    config: {}
  - id: agent1
    type: agent
    config:
      name: Assistant
      model: gpt-4
  - id: tool1
    type: tool
    config:
      name: calculator
      function: calculate
  - id: end
    type: end
    config: {}
edges:
  - source: start
    target: agent1
  - source: agent1
    target: tool1
    condition: needs_calculation
  - source: tool1
    target: agent1
  - source: agent1
    target: end
"""
    
    request_data = {"yamlContent": langgraph_yaml}
    
    response = api_client.post("/yaml/validate", json=request_data)
    
    assert response.status_code == 200
    data = response.json()
    assert data["valid"] is True
    assert data["workflow"]["framework"] == "langgraph"
    assert len(data["workflow"]["nodes"]) == 4
    assert len(data["workflow"]["edges"]) == 4


@pytest.mark.asyncio
async def test_validate_yaml_default_framework_crewai(api_client, mock_orchestrator_factory, skip_if_no_server):
    """Test that default framework is crewai when not specified via HTTP with Bearer token authentication."""
    yaml_without_framework = """
name: Test Workflow
agents:
  - name: test_agent
    role: Test Role
    goal: Test Goal
    backstory: Test Backstory
tasks:
  - name: test_task
    description: Test Description
    expectedOutput: Test Output
    agent: test_agent
"""
    
    request_data = {"yamlContent": yaml_without_framework}
    
    response = api_client.post("/yaml/validate", json=request_data)
    
    assert response.status_code == 200
    data = response.json()
    assert data["valid"] is True
    assert data["workflow"]["framework"] == "crewai"


@pytest.mark.asyncio
async def test_validate_yaml_missing_request_body(api_client, skip_if_no_server):
    """Test validation with missing request body via HTTP with Bearer token authentication."""
    response = api_client.post("/yaml/validate", json={})
    
    assert response.status_code == 422  # Validation error


@pytest.mark.asyncio
async def test_validate_yaml_invalid_request_body(api_client, skip_if_no_server):
    """Test validation with invalid request body via HTTP with Bearer token authentication."""
    # Missing required yamlContent field
    request_data = {"invalidField": "value"}
    
    response = api_client.post("/yaml/validate", json=request_data)
    
    assert response.status_code == 422  # Validation error


@pytest.mark.asyncio
async def test_validate_yaml_workflow_with_errors_includes_workflow_object(api_client, mock_orchestrator_factory, skip_if_no_server):
    """Test that validation response includes workflow object even when there are errors via HTTP with Bearer token authentication."""
    # Valid YAML that can be parsed but has validation errors
    yaml_content = """
name: Test Workflow
framework: crewai
agents:
  - name: test_agent
    role: Test Role
    goal: Test Goal
    backstory: Test Backstory
tasks:
  - name: test_task
    description: Test Description
    expectedOutput: Test Output
    agent: test_agent
"""
    
    with patch("routers.yaml_validator.OrchestratorFactory") as mock:
        mock_orchestrator = Mock()
        mock_orchestrator.validate.return_value = (False, ["Some validation error"])
        mock.get_orchestrator.return_value = mock_orchestrator
        
        request_data = {"yamlContent": yaml_content}
        
        response = api_client.post("/yaml/validate", json=request_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["valid"] is False
        assert "errors" in data
        assert "workflow" in data  # Should still include workflow object
        assert data["workflow"]["name"] == "Test Workflow"


@pytest.mark.asyncio
async def test_validate_yaml_exception_handling(api_client, skip_if_no_server):
    """Test validation handles unexpected exceptions gracefully via HTTP with Bearer token authentication."""
    with patch("routers.yaml_validator.yaml.safe_load") as mock_yaml:
        mock_yaml.side_effect = Exception("Unexpected error")
        
        request_data = {"yamlContent": "name: Test"}
        
        response = api_client.post("/yaml/validate", json=request_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["valid"] is False
        assert "errors" in data
        assert any("Validation error" in error for error in data["errors"])
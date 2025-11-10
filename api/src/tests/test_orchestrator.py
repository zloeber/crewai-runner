"""Tests for orchestrator factory and adapters."""

import pytest
from engine.services.orchestrator_factory import OrchestratorFactory
from engine.adapters import CrewAIAdapter, LangGraphAdapter


def test_factory_registration():
    """Test that frameworks are registered in the factory."""
    # Register adapters (normally done in main.py)
    OrchestratorFactory.register("crewai", CrewAIAdapter)
    OrchestratorFactory.register("langgraph", LangGraphAdapter)

    frameworks = OrchestratorFactory.get_supported_frameworks()
    assert "crewai" in frameworks
    assert "langgraph" in frameworks


def test_get_crewai_orchestrator():
    """Test getting CrewAI orchestrator."""
    OrchestratorFactory.register("crewai", CrewAIAdapter)

    orchestrator = OrchestratorFactory.get_orchestrator("crewai")
    assert isinstance(orchestrator, CrewAIAdapter)


def test_get_langgraph_orchestrator():
    """Test getting LangGraph orchestrator."""
    OrchestratorFactory.register("langgraph", LangGraphAdapter)

    orchestrator = OrchestratorFactory.get_orchestrator("langgraph")
    assert isinstance(orchestrator, LangGraphAdapter)


def test_case_insensitive_framework():
    """Test that framework names are case-insensitive."""
    OrchestratorFactory.register("crewai", CrewAIAdapter)

    orchestrator1 = OrchestratorFactory.get_orchestrator("crewai")
    orchestrator2 = OrchestratorFactory.get_orchestrator("CrewAI")
    orchestrator3 = OrchestratorFactory.get_orchestrator("CREWAI")

    assert all(
        isinstance(o, CrewAIAdapter)
        for o in [orchestrator1, orchestrator2, orchestrator3]
    )


def test_unsupported_framework():
    """Test that unsupported frameworks raise ValueError."""
    with pytest.raises(ValueError, match="not supported"):
        OrchestratorFactory.get_orchestrator("unsupported_framework")


@pytest.mark.asyncio
async def test_crewai_validation():
    """Test CrewAI workflow validation."""
    adapter = CrewAIAdapter()

    # Valid config
    valid_config = {
        "workflow": {
            "name": "Test Workflow",
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
    }

    is_valid, errors = await adapter.validate(valid_config)
    assert is_valid
    assert errors is None


@pytest.mark.asyncio
async def test_crewai_validation_missing_agents():
    """Test CrewAI validation with missing agents."""
    adapter = CrewAIAdapter()

    invalid_config = {"workflow": {"name": "Test Workflow", "tasks": []}}

    is_valid, errors = await adapter.validate(invalid_config)
    assert not is_valid
    assert "agents" in str(errors).lower()


@pytest.mark.asyncio
async def test_langgraph_validation():
    """Test LangGraph workflow validation."""
    adapter = LangGraphAdapter()

    # Valid config
    valid_config = {
        "workflow": {
            "name": "Test Graph",
            "nodes": [{"id": "node1", "type": "agent", "config": {}}],
            "edges": [{"source": "node1", "target": "END"}],
        }
    }

    is_valid, errors = await adapter.validate(valid_config)
    assert is_valid
    assert errors is None


@pytest.mark.asyncio
async def test_langgraph_validation_missing_nodes():
    """Test LangGraph validation with missing nodes."""
    adapter = LangGraphAdapter()

    invalid_config = {"workflow": {"name": "Test Graph", "edges": []}}

    is_valid, errors = await adapter.validate(invalid_config)
    assert not is_valid
    assert "nodes" in str(errors).lower()


@pytest.mark.asyncio
async def test_crewai_execute():
    """Test CrewAI workflow execution."""
    adapter = CrewAIAdapter()

    config = {
        "workflow": {
            "name": "Test Workflow",
            "agents": [
                {
                    "name": "test",
                    "role": "Test",
                    "goal": "Test",
                    "backstory": "Test",
                    "model": "gpt-4",
                }
            ],
            "tasks": [
                {
                    "name": "test",
                    "description": "Test",
                    "expectedOutput": "Test",
                    "agent": "test",
                }
            ],
        }
    }

    result = await adapter.execute(config)
    assert "workflow_id" in result
    assert result["status"] == "started"


@pytest.mark.asyncio
async def test_langgraph_execute():
    """Test LangGraph workflow execution."""
    adapter = LangGraphAdapter()

    config = {
        "workflow": {
            "name": "Test Graph",
            "nodes": [{"id": "node1", "type": "agent", "config": {}}],
            "edges": [{"source": "node1", "target": "END"}],
        }
    }

    result = await adapter.execute(config)
    assert "workflow_id" in result
    assert result["status"] == "started"

"""Tests for MCP (Model Context Protocol) server management API endpoints via HTTP with Bearer token authentication."""

import pytest
from unittest.mock import Mock, patch, AsyncMock


@pytest.fixture
def mock_mcp_manager():
    """Mock the MCP manager."""
    with patch("routers.mcp.mcp_manager") as mock:
        # Mock server configuration
        mock_server = {
            "id": "test-server-123",
            "name": "test-server",
            "description": "Test MCP server",
            "transport": {
                "type": "stdio",
                "command": "npx",
                "args": ["-y", "@modelcontextprotocol/server-filesystem", "/tmp"]
            },
            "enabled": True,
            "status": "connected"
        }
        
        # Mock tool
        mock_tool = {
            "name": "test_tool",
            "description": "Test tool description",
            "server_id": "test-server-123",
            "server_name": "test-server",
            "input_schema": {
                "type": "object",
                "properties": {
                    "param1": {"type": "string"}
                }
            },
            "output_schema": {
                "type": "object"
            }
        }
        
        # Mock connection status
        mock_status = {
            "server_id": "test-server-123",
            "status": "connected",
            "last_check": "2024-01-01T00:00:00Z",
            "error": None
        }
        
        # Configure mock methods
        mock.list_servers.return_value = [mock_server]
        mock.add_server.return_value = mock_server
        mock.update_server.return_value = mock_server
        mock.delete_server.return_value = True
        mock.test_connection.return_value = mock_status
        mock.get_server_status.return_value = mock_status
        mock.list_server_tools.return_value = [mock_tool]
        mock.list_all_tools.return_value = [mock_tool]
        mock.test_tool.return_value = {
            "success": True,
            "result": "Tool executed successfully",
            "error": None
        }
        mock.import_servers_from_config.return_value = [mock_server]
        mock.export_servers_to_config.return_value = '{"servers": []}'
        
        yield mock


@pytest.mark.asyncio
async def test_list_mcp_servers(api_client, mock_mcp_manager, skip_if_no_server):
    """Test listing all MCP servers via HTTP with Bearer token authentication."""
    response = api_client.get("/mcp/servers")
    
    assert response.status_code == 200
    data = response.json()
    assert "servers" in data
    # With HTTP testing, we get the actual server state (likely empty)
    assert isinstance(data["servers"], list)


@pytest.mark.asyncio
async def test_add_mcp_server_success(api_client, mock_mcp_manager, sample_mcp_server_config, skip_if_no_server):
    """Test adding a new MCP server successfully via HTTP with Bearer token authentication."""
    request_data = {"server": sample_mcp_server_config}
    
    response = api_client.post("/mcp/servers", json=request_data)
    
    assert response.status_code == 200
    data = response.json()
    assert "server" in data
    assert data["server"]["name"] == "test-server"


@pytest.mark.asyncio
async def test_add_mcp_server_error(api_client, mock_mcp_manager, sample_mcp_server_config, skip_if_no_server):
    """Test adding MCP server with error via HTTP with Bearer token authentication."""
    mock_mcp_manager.add_server.side_effect = Exception("Failed to add server")
    
    request_data = {"server": sample_mcp_server_config}
    
    response = api_client.post("/mcp/servers", json=request_data)
    
    assert response.status_code == 400
    assert "Failed to add server" in response.json()["error"]


@pytest.mark.asyncio
async def test_update_mcp_server_success(api_client, mock_mcp_manager, sample_mcp_server_config, skip_if_no_server):
    """Test updating an MCP server successfully via HTTP with Bearer token authentication."""
    request_data = {"server": sample_mcp_server_config}
    
    response = api_client.put("/mcp/servers/test-server-123", json=request_data)
    
    assert response.status_code == 200
    data = response.json()
    assert "server" in data
    assert data["server"]["name"] == "test-server"


@pytest.mark.asyncio
async def test_update_mcp_server_not_found(api_client, mock_mcp_manager, sample_mcp_server_config, skip_if_no_server):
    """Test updating non-existent MCP server via HTTP with Bearer token authentication."""
    mock_mcp_manager.update_server.return_value = None
    
    request_data = {"server": sample_mcp_server_config}
    
    response = api_client.put("/mcp/servers/non-existent", json=request_data)
    
    assert response.status_code == 404
    assert "Server non-existent not found" in response.json()["error"]


@pytest.mark.asyncio
async def test_update_mcp_server_error(api_client, mock_mcp_manager, sample_mcp_server_config, skip_if_no_server):
    """Test updating MCP server with error via HTTP with Bearer token authentication."""
    mock_mcp_manager.update_server.side_effect = Exception("Update failed")
    
    request_data = {"server": sample_mcp_server_config}
    
    response = api_client.put("/mcp/servers/test-server-123", json=request_data)
    
    assert response.status_code == 400
    assert "Failed to update server" in response.json()["error"]


@pytest.mark.asyncio
async def test_delete_mcp_server_success(api_client, mock_mcp_manager, skip_if_no_server):
    """Test deleting an MCP server successfully via HTTP with Bearer token authentication."""
    response = api_client.delete("/mcp/servers/test-server-123")
    
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == "test-server-123"
    assert "deleted successfully" in data["message"]


@pytest.mark.asyncio
async def test_delete_mcp_server_not_found(api_client, mock_mcp_manager, skip_if_no_server):
    """Test deleting non-existent MCP server via HTTP with Bearer token authentication."""
    mock_mcp_manager.delete_server.return_value = False
    
    response = api_client.delete("/mcp/servers/non-existent")
    
    assert response.status_code == 404
    assert "Server non-existent not found" in response.json()["error"]


@pytest.mark.asyncio
async def test_test_mcp_connection_success(api_client, mock_mcp_manager, skip_if_no_server):
    """Test testing MCP server connection successfully via HTTP with Bearer token authentication."""
    response = api_client.post("/mcp/servers/test-server-123/connect")
    
    assert response.status_code == 200
    data = response.json()
    assert data["server_id"] == "test-server-123"
    assert "connection_status" in data


@pytest.mark.asyncio
async def test_test_mcp_connection_error(api_client, mock_mcp_manager, skip_if_no_server):
    """Test testing MCP server connection with error via HTTP with Bearer token authentication."""
    mock_mcp_manager.test_connection.side_effect = Exception("Connection failed")
    
    response = api_client.post("/mcp/servers/test-server-123/connect")
    
    assert response.status_code == 500
    assert "Connection test failed" in response.json()["error"]


@pytest.mark.asyncio
async def test_get_mcp_server_status_success(api_client, mock_mcp_manager, skip_if_no_server):
    """Test getting MCP server status successfully via HTTP with Bearer token authentication."""
    response = api_client.get("/mcp/servers/test-server-123/status")
    
    assert response.status_code == 200
    data = response.json()
    assert data["server_id"] == "test-server-123"
    assert data["status"] == "connected"


@pytest.mark.asyncio
async def test_get_mcp_server_status_error(api_client, mock_mcp_manager, skip_if_no_server):
    """Test getting MCP server status with error via HTTP with Bearer token authentication."""
    mock_mcp_manager.get_server_status.side_effect = Exception("Status check failed")
    
    response = api_client.get("/mcp/servers/test-server-123/status")
    
    assert response.status_code == 500
    assert "Failed to get server status" in response.json()["error"]


@pytest.mark.asyncio
async def test_list_server_tools_success(api_client, mock_mcp_manager, skip_if_no_server):
    """Test listing tools from a specific MCP server via HTTP with Bearer token authentication."""
    response = api_client.get("/mcp/servers/test-server-123/tools")
    
    assert response.status_code == 200
    data = response.json()
    assert "tools" in data
    # With HTTP testing, we get the actual server state (likely empty)
    assert isinstance(data["tools"], list)


@pytest.mark.asyncio
async def test_list_server_tools_error(api_client, mock_mcp_manager, skip_if_no_server):
    """Test listing server tools with error via HTTP with Bearer token authentication."""
    mock_mcp_manager.list_server_tools.side_effect = Exception("Failed to list tools")
    
    response = api_client.get("/mcp/servers/test-server-123/tools")
    
    assert response.status_code == 500
    assert "Failed to list tools" in response.json()["error"]


@pytest.mark.asyncio
async def test_list_all_tools_success(api_client, mock_mcp_manager, skip_if_no_server):
    """Test listing all tools from all servers via HTTP with Bearer token authentication."""
    response = api_client.get("/mcp/tools")
    
    assert response.status_code == 200
    data = response.json()
    assert "tools" in data
    # With HTTP testing, we get the actual server state (likely empty)
    assert isinstance(data["tools"], list)


@pytest.mark.asyncio
async def test_list_all_tools_error(api_client, mock_mcp_manager, skip_if_no_server):
    """Test listing all tools with error via HTTP with Bearer token authentication."""
    mock_mcp_manager.list_all_tools.side_effect = Exception("Failed to list tools")
    
    response = api_client.get("/mcp/tools")
    
    assert response.status_code == 500
    assert "Failed to list tools" in response.json()["error"]


@pytest.mark.asyncio
async def test_test_mcp_tool_success(api_client, mock_mcp_manager, skip_if_no_server):
    """Test executing an MCP tool for testing via HTTP with Bearer token authentication."""
    request_data = {
        "server_id": "test-server-123",
        "tool_name": "test_tool",
        "parameters": {"param1": "value1"}
    }
    
    response = api_client.post("/mcp/tools/test", json=request_data)
    
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "result" in data


@pytest.mark.asyncio
async def test_test_mcp_tool_error(api_client, mock_mcp_manager, skip_if_no_server):
    """Test executing MCP tool with error via HTTP with Bearer token authentication."""
    mock_mcp_manager.test_tool.side_effect = Exception("Tool test failed")
    
    request_data = {
        "server_id": "test-server-123",
        "tool_name": "test_tool",
        "parameters": {"param1": "value1"}
    }
    
    response = api_client.post("/mcp/tools/test", json=request_data)
    
    assert response.status_code == 500
    assert "Tool test failed" in response.json()["error"]


@pytest.mark.asyncio
async def test_get_tool_schema_success(api_client, mock_mcp_manager, skip_if_no_server):
    """Test getting tool schema successfully via HTTP with Bearer token authentication."""
    response = api_client.get("/mcp/tools/test-server-123:test_tool/schema")
    
    assert response.status_code == 200
    data = response.json()
    assert data["tool_id"] == "test-server-123:test_tool"
    assert data["name"] == "test_tool"
    assert "input_schema" in data
    assert "output_schema" in data


@pytest.mark.asyncio
async def test_get_tool_schema_invalid_format(api_client, mock_mcp_manager, skip_if_no_server):
    """Test getting tool schema with invalid tool ID format via HTTP with Bearer token authentication."""
    response = api_client.get("/mcp/tools/invalid-format/schema")
    
    assert response.status_code == 400
    assert "Invalid tool_id format" in response.json()["error"]


@pytest.mark.asyncio
async def test_get_tool_schema_tool_not_found(api_client, mock_mcp_manager, skip_if_no_server):
    """Test getting schema for non-existent tool via HTTP with Bearer token authentication."""
    mock_mcp_manager.list_server_tools.return_value = []  # No tools
    
    response = api_client.get("/mcp/tools/test-server-123:non_existent/schema")
    
    assert response.status_code == 404
    assert "Tool not found" in response.json()["error"]


@pytest.mark.asyncio
async def test_import_mcp_config_success(api_client, mock_mcp_manager, skip_if_no_server):
    """Test importing MCP configuration successfully via HTTP with Bearer token authentication."""
    request_data = {
        "config_content": '{"servers": []}',
        "config_format": "custom"
    }
    
    response = api_client.post("/mcp/import/config", json=request_data)
    
    assert response.status_code == 200
    data = response.json()
    assert data["imported_count"] == 1
    assert "servers" in data
    assert "Successfully imported" in data["message"]


@pytest.mark.asyncio
async def test_import_mcp_config_invalid_format(api_client, mock_mcp_manager, skip_if_no_server):
    """Test importing MCP configuration with invalid format via HTTP with Bearer token authentication."""
    mock_mcp_manager.import_servers_from_config.side_effect = ValueError("Invalid format")
    
    request_data = {
        "config_content": "invalid config",
        "config_format": "custom"
    }
    
    response = api_client.post("/mcp/import/config", json=request_data)
    
    assert response.status_code == 400
    assert "Invalid format" in response.json()["error"]


@pytest.mark.asyncio
async def test_import_mcp_config_error(api_client, mock_mcp_manager, skip_if_no_server):
    """Test importing MCP configuration with error via HTTP with Bearer token authentication."""
    mock_mcp_manager.import_servers_from_config.side_effect = Exception("Import failed")
    
    request_data = {
        "config_content": '{"servers": []}',
        "config_format": "custom"
    }
    
    response = api_client.post("/mcp/import/config", json=request_data)
    
    assert response.status_code == 500
    assert "Import failed" in response.json()["error"]


@pytest.mark.asyncio
async def test_export_mcp_config_success(api_client, mock_mcp_manager, skip_if_no_server):
    """Test exporting MCP configuration successfully via HTTP with Bearer token authentication."""
    response = api_client.get("/mcp/export/config?format=custom")
    
    assert response.status_code == 200
    data = response.json()
    assert "config_content" in data
    assert data["format"] == "custom"


@pytest.mark.asyncio
async def test_export_mcp_config_error(api_client, mock_mcp_manager, skip_if_no_server):
    """Test exporting MCP configuration with error via HTTP with Bearer token authentication."""
    mock_mcp_manager.export_servers_to_config.side_effect = Exception("Export failed")
    
    response = api_client.get("/mcp/export/config")
    
    assert response.status_code == 500
    assert "Export failed" in response.json()["error"]


@pytest.mark.asyncio
async def test_export_tool_definition_crewai(api_client, mock_mcp_manager, skip_if_no_server):
    """Test exporting tool definition for CrewAI via HTTP with Bearer token authentication."""
    request_data = {"framework": "crewai"}
    
    response = api_client.post("/mcp/tools/test-server-123:test_tool/export", json=request_data)
    
    assert response.status_code == 200
    data = response.json()
    assert data["framework"] == "crewai"
    assert "tool_definition" in data
    assert "CrewAI" in data["instructions"]
    assert "from crewai_tools import Tool" in data["tool_definition"]


@pytest.mark.asyncio
async def test_export_tool_definition_langgraph(api_client, mock_mcp_manager, skip_if_no_server):
    """Test exporting tool definition for LangGraph via HTTP with Bearer token authentication."""
    request_data = {"framework": "langgraph"}
    
    response = api_client.post("/mcp/tools/test-server-123:test_tool/export", json=request_data)
    
    assert response.status_code == 200
    data = response.json()
    assert data["framework"] == "langgraph"
    assert "tool_definition" in data
    assert "LangGraph" in data["instructions"]
    assert "from langchain.tools import StructuredTool" in data["tool_definition"]


@pytest.mark.asyncio
async def test_export_tool_definition_yaml(api_client, mock_mcp_manager, skip_if_no_server):
    """Test exporting tool definition as YAML via HTTP with Bearer token authentication."""
    request_data = {"framework": "yaml"}
    
    response = api_client.post("/mcp/tools/test-server-123:test_tool/export", json=request_data)
    
    assert response.status_code == 200
    data = response.json()
    assert data["framework"] == "yaml"
    assert "tool_definition" in data
    assert "workflow YAML" in data["instructions"]
    assert "name: test_tool" in data["tool_definition"]


@pytest.mark.asyncio
async def test_export_tool_definition_invalid_tool_id(api_client, mock_mcp_manager, skip_if_no_server):
    """Test exporting tool definition with invalid tool ID via HTTP with Bearer token authentication."""
    request_data = {"framework": "crewai"}
    
    response = api_client.post("/mcp/tools/invalid-format/export", json=request_data)
    
    assert response.status_code == 400
    assert "Invalid tool_id format" in response.json()["error"]


@pytest.mark.asyncio
async def test_export_tool_definition_tool_not_found(api_client, mock_mcp_manager, skip_if_no_server):
    """Test exporting definition for non-existent tool via HTTP with Bearer token authentication."""
    mock_mcp_manager.list_server_tools.return_value = []  # No tools
    
    request_data = {"framework": "crewai"}
    
    response = api_client.post("/mcp/tools/test-server-123:non_existent/export", json=request_data)
    
    assert response.status_code == 404
    assert "Tool not found" in response.json()["error"]


@pytest.mark.asyncio
async def test_export_tool_definition_error(api_client, mock_mcp_manager, skip_if_no_server):
    """Test exporting tool definition with error via HTTP with Bearer token authentication."""
    mock_mcp_manager.list_server_tools.side_effect = Exception("Export failed")
    
    request_data = {"framework": "crewai"}
    
    response = api_client.post("/mcp/tools/test-server-123:test_tool/export", json=request_data)
    
    assert response.status_code == 500
    assert "Export failed" in response.json()["error"]


@pytest.mark.asyncio
async def test_add_mcp_server_invalid_request_body(api_client, skip_if_no_server):
    """Test adding MCP server with invalid request body via HTTP with Bearer token authentication."""
    # Missing required server field
    request_data = {}
    
    response = api_client.post("/mcp/servers", json=request_data)
    
    assert response.status_code == 422  # Validation error


@pytest.mark.asyncio
async def test_test_mcp_tool_invalid_request_body(api_client, skip_if_no_server):
    """Test testing MCP tool with invalid request body via HTTP with Bearer token authentication."""
    # Missing required fields
    request_data = {"server_id": "test-server"}
    
    response = api_client.post("/mcp/tools/test", json=request_data)
    
    assert response.status_code == 422  # Validation error
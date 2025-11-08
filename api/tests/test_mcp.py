"""Tests for MCP server management functionality."""

import pytest
from src.engine.models import (
    MCPServerConfig,
    MCPTransport,
    MCPServer,
)
from src.engine.services.mcp_manager import MCPServerManager


@pytest.fixture
def mcp_manager():
    """Create a fresh MCP manager for each test."""
    return MCPServerManager()


@pytest.fixture
def sample_server_config():
    """Sample MCP server configuration."""
    return MCPServerConfig(
        name="test-server",
        description="Test MCP server",
        transport=MCPTransport(
            type="stdio",
            command="npx",
            args=["-y", "@modelcontextprotocol/server-filesystem", "/tmp"],
        ),
        env={"TEST_VAR": "test_value"},
        tools=[],
        enabled=True,
    )


@pytest.mark.asyncio
async def test_add_server(mcp_manager, sample_server_config):
    """Test adding a new MCP server."""
    server = await mcp_manager.add_server(sample_server_config)

    assert server.id is not None
    assert server.name == "test-server"
    assert server.description == "Test MCP server"
    assert server.transport.type == "stdio"
    assert server.transport.command == "npx"
    assert server.enabled is True
    assert server.status == "disconnected"


@pytest.mark.asyncio
async def test_list_servers(mcp_manager, sample_server_config):
    """Test listing all servers."""
    # Add a server
    await mcp_manager.add_server(sample_server_config)

    # List servers
    servers = await mcp_manager.list_servers()

    assert len(servers) == 1
    assert servers[0].name == "test-server"


@pytest.mark.asyncio
async def test_get_server(mcp_manager, sample_server_config):
    """Test getting a specific server."""
    # Add a server
    added_server = await mcp_manager.add_server(sample_server_config)

    # Get the server
    server = await mcp_manager.get_server(added_server.id)

    assert server is not None
    assert server.id == added_server.id
    assert server.name == "test-server"


@pytest.mark.asyncio
async def test_update_server(mcp_manager, sample_server_config):
    """Test updating an existing server."""
    # Add a server
    server = await mcp_manager.add_server(sample_server_config)

    # Update the server
    updated_config = sample_server_config.model_copy()
    updated_config.name = "updated-server"
    updated_config.description = "Updated description"

    updated_server = await mcp_manager.update_server(server.id, updated_config)

    assert updated_server is not None
    assert updated_server.name == "updated-server"
    assert updated_server.description == "Updated description"


@pytest.mark.asyncio
async def test_delete_server(mcp_manager, sample_server_config):
    """Test deleting a server."""
    # Add a server
    server = await mcp_manager.add_server(sample_server_config)

    # Delete the server
    result = await mcp_manager.delete_server(server.id)

    assert result is True

    # Verify server is gone
    remaining_servers = await mcp_manager.list_servers()
    assert len(remaining_servers) == 0


@pytest.mark.asyncio
async def test_delete_nonexistent_server(mcp_manager):
    """Test deleting a server that doesn't exist."""
    result = await mcp_manager.delete_server("nonexistent-id")
    assert result is False


@pytest.mark.asyncio
async def test_get_server_status(mcp_manager, sample_server_config):
    """Test getting server connection status."""
    # Add a server
    server = await mcp_manager.add_server(sample_server_config)

    # Get status
    status = await mcp_manager.get_server_status(server.id)

    assert status.status == "disconnected"
    assert status.transport_type == "stdio"


@pytest.mark.asyncio
async def test_multiple_servers(mcp_manager):
    """Test managing multiple servers."""
    # Add multiple servers
    config1 = MCPServerConfig(
        name="server-1",
        transport=MCPTransport(type="stdio", command="cmd1"),
        env={},
        tools=[],
        enabled=True,
    )
    config2 = MCPServerConfig(
        name="server-2",
        transport=MCPTransport(type="stdio", command="cmd2"),
        env={},
        tools=[],
        enabled=True,
    )

    server1 = await mcp_manager.add_server(config1)
    server2 = await mcp_manager.add_server(config2)

    # List servers
    servers = await mcp_manager.list_servers()

    assert len(servers) == 2
    server_names = {s.name for s in servers}
    assert "server-1" in server_names
    assert "server-2" in server_names


@pytest.mark.asyncio
async def test_export_servers(mcp_manager, sample_server_config):
    """Test exporting server configuration."""
    # Add a server
    await mcp_manager.add_server(sample_server_config)

    # Export configuration
    config_json = await mcp_manager.export_servers_to_config("custom")

    assert config_json is not None
    assert "test-server" in config_json
    assert "mcpServers" in config_json


@pytest.mark.asyncio
async def test_import_servers_from_claude_config(mcp_manager):
    """Test importing servers from Claude Desktop config format."""
    claude_config = """{
        "mcpServers": {
            "filesystem": {
                "command": "npx",
                "args": ["-y", "@modelcontextprotocol/server-filesystem", "/tmp"],
                "env": {"TEST": "value"}
            },
            "github": {
                "command": "npx",
                "args": ["-y", "@modelcontextprotocol/server-github"],
                "env": {}
            }
        }
    }"""

    # Import servers
    servers = await mcp_manager.import_servers_from_config(
        claude_config, "claude_desktop"
    )

    assert len(servers) == 2
    server_names = {s.name for s in servers}
    assert "filesystem" in server_names
    assert "github" in server_names


@pytest.mark.asyncio
async def test_import_invalid_json(mcp_manager):
    """Test importing invalid JSON configuration."""
    invalid_config = "not valid json {{"

    with pytest.raises(ValueError, match="Invalid JSON"):
        await mcp_manager.import_servers_from_config(invalid_config, "claude_desktop")

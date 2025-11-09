"""MCP Server Manager for handling MCP server lifecycle and operations."""

import asyncio
import json
import time
import uuid
from typing import Dict, List, Optional, Any

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

from models import (
    MCPServer,
    MCPServerConfig,
    MCPTransport,
    MCPConnectionStatus,
    MCPTool,
    MCPToolTestResponse,
)


class MCPServerManager:
    """Manages MCP server connections and operations."""

    def __init__(self):
        self._servers: Dict[str, MCPServer] = {}
        self._sessions: Dict[str, ClientSession] = {}
        self._lock = asyncio.Lock()

    def _generate_id(self) -> str:
        """Generate a unique server ID."""
        return str(uuid.uuid4())

    async def add_server(self, config: MCPServerConfig) -> MCPServer:
        """Add a new MCP server."""
        async with self._lock:
            server_id = self._generate_id()
            server = MCPServer(
                id=server_id,
                name=config.name,
                description=config.description,
                transport=config.transport,
                env=config.env or {},
                tools=config.tools,
                enabled=config.enabled,
                status="disconnected",
            )
            self._servers[server_id] = server
            return server

    async def get_server(self, server_id: str) -> Optional[MCPServer]:
        """Get a server by ID."""
        return self._servers.get(server_id)

    async def list_servers(self) -> List[MCPServer]:
        """List all registered servers."""
        return list(self._servers.values())

    async def update_server(
        self, server_id: str, config: MCPServerConfig
    ) -> Optional[MCPServer]:
        """Update an existing server."""
        async with self._lock:
            if server_id not in self._servers:
                return None

            server = self._servers[server_id]
            server.name = config.name
            server.description = config.description
            server.transport = config.transport
            server.env = config.env or {}
            server.tools = config.tools
            server.enabled = config.enabled

            # Disconnect if connected
            if server_id in self._sessions:
                await self._disconnect_server(server_id)

            return server

    async def delete_server(self, server_id: str) -> bool:
        """Delete a server."""
        async with self._lock:
            if server_id not in self._servers:
                return False

            # Disconnect if connected
            if server_id in self._sessions:
                await self._disconnect_server(server_id)

            del self._servers[server_id]
            return True

    async def test_connection(self, server_id: str) -> MCPConnectionStatus:
        """Test connection to an MCP server."""
        server = self._servers.get(server_id)
        if not server:
            return MCPConnectionStatus(
                status="error",
                message="Server not found",
                transport_type="unknown",
                initialization_success=False,
            )

        start_time = time.time()
        try:
            # Try to connect
            session = await self._connect_server(server_id)
            latency_ms = (time.time() - start_time) * 1000

            if session:
                # Update server status
                server.status = "connected"
                server.error_message = None

                return MCPConnectionStatus(
                    status="connected",
                    message="Connection successful",
                    latency_ms=latency_ms,
                    transport_type=server.transport.type,
                    initialization_success=True,
                )
            else:
                server.status = "error"
                server.error_message = "Failed to establish connection"
                return MCPConnectionStatus(
                    status="error",
                    message="Failed to establish connection",
                    latency_ms=latency_ms,
                    transport_type=server.transport.type,
                    initialization_success=False,
                )

        except Exception as e:
            latency_ms = (time.time() - start_time) * 1000
            server.status = "error"
            server.error_message = str(e)
            return MCPConnectionStatus(
                status="error",
                message=f"Connection failed: {str(e)}",
                latency_ms=latency_ms,
                transport_type=server.transport.type,
                initialization_success=False,
            )

    async def get_server_status(self, server_id: str) -> MCPConnectionStatus:
        """Get current connection status of a server."""
        server = self._servers.get(server_id)
        if not server:
            return MCPConnectionStatus(
                status="error",
                message="Server not found",
                transport_type="unknown",
                initialization_success=False,
            )

        is_connected = server_id in self._sessions
        return MCPConnectionStatus(
            status=server.status,
            message=server.error_message or "Server status retrieved",
            transport_type=server.transport.type,
            initialization_success=is_connected,
        )

    async def list_server_tools(self, server_id: str) -> List[MCPTool]:
        """List all tools provided by a server."""
        server = self._servers.get(server_id)
        if not server:
            return []

        # Ensure server is connected
        session = await self._get_or_connect_server(server_id)
        if not session:
            return []

        try:
            # List tools from the MCP server
            tools_result = await session.list_tools()
            mcp_tools = []

            for tool in tools_result.tools:
                mcp_tool = MCPTool(
                    id=f"{server_id}:{tool.name}",
                    server_id=server_id,
                    server_name=server.name,
                    name=tool.name,
                    description=tool.description,
                    input_schema=tool.inputSchema,
                    output_schema=None,  # MCP doesn't expose output schema
                )
                mcp_tools.append(mcp_tool)

            # Update server's tool list
            server.tools = [t.name for t in mcp_tools]

            return mcp_tools

        except Exception as e:
            server.status = "error"
            server.error_message = f"Failed to list tools: {str(e)}"
            return []

    async def list_all_tools(self) -> List[MCPTool]:
        """List all tools from all connected servers."""
        all_tools = []
        for server_id in self._servers.keys():
            tools = await self.list_server_tools(server_id)
            all_tools.extend(tools)
        return all_tools

    async def test_tool(
        self, server_id: str, tool_name: str, parameters: Dict[str, Any]
    ) -> MCPToolTestResponse:
        """Test executing a tool."""
        start_time = time.time()

        server = self._servers.get(server_id)
        if not server:
            return MCPToolTestResponse(
                tool_name=tool_name,
                success=False,
                error="Server not found",
                execution_time_ms=0,
                request=parameters,
                response={},
            )

        # Ensure server is connected
        session = await self._get_or_connect_server(server_id)
        if not session:
            return MCPToolTestResponse(
                tool_name=tool_name,
                success=False,
                error="Failed to connect to server",
                execution_time_ms=(time.time() - start_time) * 1000,
                request=parameters,
                response={},
            )

        try:
            # Call the tool
            result = await session.call_tool(tool_name, parameters)
            execution_time_ms = (time.time() - start_time) * 1000

            return MCPToolTestResponse(
                tool_name=tool_name,
                success=True,
                result=result.content,
                execution_time_ms=execution_time_ms,
                request=parameters,
                response={"content": result.content},
            )

        except Exception as e:
            execution_time_ms = (time.time() - start_time) * 1000
            return MCPToolTestResponse(
                tool_name=tool_name,
                success=False,
                error=str(e),
                execution_time_ms=execution_time_ms,
                request=parameters,
                response={},
            )

    async def import_servers_from_config(
        self, config_content: str, config_format: str = "claude_desktop"
    ) -> List[MCPServer]:
        """Import MCP servers from configuration file."""
        imported_servers = []

        try:
            config = json.loads(config_content)

            if config_format == "claude_desktop":
                # Parse Claude Desktop config format
                mcp_servers = config.get("mcpServers", {})
                for name, server_config in mcp_servers.items():
                    transport_config = MCPTransport(
                        type="stdio",
                        command=server_config.get("command"),
                        args=server_config.get("args", []),
                    )

                    mcp_config = MCPServerConfig(
                        name=name,
                        description=f"Imported from Claude Desktop: {name}",
                        transport=transport_config,
                        env=server_config.get("env", {}),
                        tools=[],
                        enabled=True,
                    )

                    server = await self.add_server(mcp_config)
                    imported_servers.append(server)

            return imported_servers

        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON configuration: {str(e)}")
        except Exception as e:
            raise ValueError(f"Failed to import configuration: {str(e)}")

    async def export_servers_to_config(self, config_format: str = "custom") -> str:
        """Export MCP servers to configuration format."""
        servers_list = await self.list_servers()

        if config_format == "custom":
            # Export to our custom format
            config = {
                "mcpServers": {
                    server.name: {
                        "transport": {
                            "type": server.transport.type,
                            "command": server.transport.command,
                            "args": server.transport.args or [],
                            "host": server.transport.host,
                            "port": server.transport.port,
                            "url": server.transport.url,
                        },
                        "env": server.env,
                        "tools": server.tools,
                        "enabled": server.enabled,
                    }
                    for server in servers_list
                }
            }
            return json.dumps(config, indent=2)

        return "{}"

    async def _connect_server(self, server_id: str) -> Optional[ClientSession]:
        """Connect to an MCP server."""
        server = self._servers.get(server_id)
        if not server or not server.enabled:
            return None

        # Only support stdio transport for now
        if server.transport.type != "stdio":
            raise ValueError(f"Unsupported transport type: {server.transport.type}")

        if not server.transport.command:
            raise ValueError("Command is required for stdio transport")

        try:
            # Create server parameters
            server_params = StdioServerParameters(
                command=server.transport.command,
                args=server.transport.args or [],
                env=server.env,
            )

            # Create stdio client
            stdio = await stdio_client(server_params)
            read, write = stdio

            # Initialize session
            session = ClientSession(read, write)
            await session.initialize()

            # Store session
            self._sessions[server_id] = session
            server.status = "connected"
            server.error_message = None

            return session

        except Exception as e:
            server.status = "error"
            server.error_message = str(e)
            return None

    async def _disconnect_server(self, server_id: str):
        """Disconnect from an MCP server."""
        if server_id in self._sessions:
            session = self._sessions[server_id]
            try:
                # Close the session
                await session.__aexit__(None, None, None)
            except Exception as _:
                pass
            del self._sessions[server_id]

        server = self._servers.get(server_id)
        if server:
            server.status = "disconnected"

    async def _get_or_connect_server(self, server_id: str) -> Optional[ClientSession]:
        """Get existing session or connect to server."""
        if server_id in self._sessions:
            return self._sessions[server_id]
        return await self._connect_server(server_id)


# Global instance
mcp_manager = MCPServerManager()

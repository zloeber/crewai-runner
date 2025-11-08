"""MCP Server Management API endpoints."""

from fastapi import APIRouter, HTTPException, status
from typing import Optional

from models import (
    MCPServer,
    MCPServerListResponse,
    MCPServerConfig,
    AddMCPServerRequest,
    AddMCPServerResponse,
    UpdateMCPServerRequest,
    UpdateMCPServerResponse,
    DeleteMCPServerResponse,
    TestMCPConnectionResponse,
    MCPConnectionStatus,
    MCPToolListResponse,
    MCPToolTestRequest,
    MCPToolTestResponse,
    ImportMCPConfigRequest,
    ImportMCPConfigResponse,
    ExportMCPConfigResponse,
    ExportToolRequest,
    ExportToolResponse,
)
from services.mcp_manager import mcp_manager

router = APIRouter(prefix="/mcp", tags=["MCP"])


@router.get("/servers", response_model=MCPServerListResponse)
async def list_mcp_servers():
    """List all registered MCP servers."""
    servers = await mcp_manager.list_servers()
    return MCPServerListResponse(servers=servers)


@router.post("/servers", response_model=AddMCPServerResponse)
async def add_mcp_server(request: AddMCPServerRequest):
    """Register a new MCP server."""
    try:
        server = await mcp_manager.add_server(request.server)
        return AddMCPServerResponse(server=server)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to add server: {str(e)}",
        )


@router.put("/servers/{server_id}", response_model=UpdateMCPServerResponse)
async def update_mcp_server(server_id: str, request: UpdateMCPServerRequest):
    """Update an existing MCP server configuration."""
    try:
        server = await mcp_manager.update_server(server_id, request.server)
        if not server:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Server {server_id} not found",
            )
        return UpdateMCPServerResponse(server=server)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to update server: {str(e)}",
        )


@router.delete("/servers/{server_id}", response_model=DeleteMCPServerResponse)
async def delete_mcp_server(server_id: str):
    """Remove an MCP server."""
    success = await mcp_manager.delete_server(server_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Server {server_id} not found",
        )
    return DeleteMCPServerResponse(id=server_id, message="Server deleted successfully")


@router.post("/servers/{server_id}/connect", response_model=TestMCPConnectionResponse)
async def test_mcp_connection(server_id: str):
    """Test connection to an MCP server."""
    try:
        connection_status = await mcp_manager.test_connection(server_id)
        return TestMCPConnectionResponse(
            server_id=server_id, connection_status=connection_status
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Connection test failed: {str(e)}",
        )


@router.get("/servers/{server_id}/status", response_model=MCPConnectionStatus)
async def get_mcp_server_status(server_id: str):
    """Get current connection status of an MCP server."""
    try:
        status_info = await mcp_manager.get_server_status(server_id)
        return status_info
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get server status: {str(e)}",
        )


@router.get("/servers/{server_id}/tools", response_model=MCPToolListResponse)
async def list_server_tools(server_id: str):
    """List all tools provided by a specific MCP server."""
    try:
        tools = await mcp_manager.list_server_tools(server_id)
        return MCPToolListResponse(tools=tools)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list tools: {str(e)}",
        )


@router.get("/tools", response_model=MCPToolListResponse)
async def list_all_tools():
    """List all tools from all connected MCP servers."""
    try:
        tools = await mcp_manager.list_all_tools()
        return MCPToolListResponse(tools=tools)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list tools: {str(e)}",
        )


@router.post("/tools/test", response_model=MCPToolTestResponse)
async def test_mcp_tool(request: MCPToolTestRequest):
    """Execute a tool for testing purposes."""
    try:
        result = await mcp_manager.test_tool(
            request.server_id, request.tool_name, request.parameters
        )
        return result
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Tool test failed: {str(e)}",
        )


@router.get("/tools/{tool_id}/schema")
async def get_tool_schema(tool_id: str):
    """Get detailed schema for a specific tool."""
    # Parse tool_id format: "server_id:tool_name"
    parts = tool_id.split(":", 1)
    if len(parts) != 2:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid tool_id format. Expected 'server_id:tool_name'",
        )

    server_id, tool_name = parts

    try:
        tools = await mcp_manager.list_server_tools(server_id)
        tool = next((t for t in tools if t.name == tool_name), None)

        if not tool:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Tool not found"
            )

        return {
            "tool_id": tool_id,
            "name": tool.name,
            "description": tool.description,
            "input_schema": tool.input_schema,
            "output_schema": tool.output_schema,
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get tool schema: {str(e)}",
        )


@router.post("/import/config", response_model=ImportMCPConfigResponse)
async def import_mcp_config(request: ImportMCPConfigRequest):
    """Import MCP servers from configuration file (Claude Desktop, Cline, etc.)."""
    try:
        servers = await mcp_manager.import_servers_from_config(
            request.config_content, request.config_format
        )
        return ImportMCPConfigResponse(
            imported_count=len(servers),
            servers=servers,
            message=f"Successfully imported {len(servers)} server(s)",
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Import failed: {str(e)}",
        )


@router.get("/export/config", response_model=ExportMCPConfigResponse)
async def export_mcp_config(format: str = "custom"):
    """Export current MCP server configuration."""
    try:
        config_content = await mcp_manager.export_servers_to_config(format)
        return ExportMCPConfigResponse(config_content=config_content, format=format)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Export failed: {str(e)}",
        )


@router.post("/tools/{tool_id}/export", response_model=ExportToolResponse)
async def export_tool_definition(tool_id: str, request: ExportToolRequest):
    """Export tool definition in framework-specific format."""
    # Parse tool_id format: "server_id:tool_name"
    parts = tool_id.split(":", 1)
    if len(parts) != 2:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid tool_id format. Expected 'server_id:tool_name'",
        )

    server_id, tool_name = parts

    try:
        tools = await mcp_manager.list_server_tools(server_id)
        tool = next((t for t in tools if t.name == tool_name), None)

        if not tool:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Tool not found"
            )

        # Generate framework-specific export
        if request.framework == "crewai":
            tool_def = _export_crewai_tool(tool)
            instructions = "Add this tool to your CrewAI agent's tools list"
        elif request.framework == "langgraph":
            tool_def = _export_langgraph_tool(tool)
            instructions = "Import and use this tool in your LangGraph workflow"
        else:  # yaml
            tool_def = _export_yaml_tool(tool)
            instructions = "Include this tool definition in your workflow YAML"

        return ExportToolResponse(
            tool_definition=tool_def,
            framework=request.framework,
            instructions=instructions,
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Export failed: {str(e)}",
        )


def _export_crewai_tool(tool) -> str:
    """Export tool as CrewAI Tool definition."""
    return f"""from crewai_tools import Tool

{tool.name} = Tool(
    name="{tool.name}",
    description=\"\"\"
{tool.description or 'No description available'}
    \"\"\",
    func=lambda **kwargs: call_mcp_tool(
        server_id="{tool.server_id}",
        tool_name="{tool.name}",
        parameters=kwargs
    )
)

# Add to agent:
# agent = Agent(
#     role="Your Role",
#     tools=[{tool.name}],
#     ...
# )
"""


def _export_langgraph_tool(tool) -> str:
    """Export tool as LangGraph tool binding."""
    return f"""from langchain.tools import StructuredTool

{tool.name}_tool = StructuredTool.from_function(
    name="{tool.name}",
    description="{tool.description or 'No description available'}",
    func=lambda **kwargs: call_mcp_tool(
        server_id="{tool.server_id}",
        tool_name="{tool.name}",
        parameters=kwargs
    ),
    # Add input schema validation here
)

# Use in LangGraph:
# tools = [{tool.name}_tool]
"""


def _export_yaml_tool(tool) -> str:
    """Export tool as YAML definition."""
    return f"""# Tool: {tool.name}
name: {tool.name}
server: {tool.server_name}
description: {tool.description or 'No description available'}
input_schema:
  type: object
  properties: {{}}
  # Add properties based on: {tool.input_schema}
"""

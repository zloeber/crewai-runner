/**
 * MCP Server Management API Service
 */

import {
  MCPServer,
  MCPServerConfig,
  MCPTool,
  MCPToolTestResult,
  MCPConnectionStatus,
  AddServerRequest,
  AddServerResponse,
  UpdateServerRequest,
  UpdateServerResponse,
  DeleteServerResponse,
  TestConnectionResponse,
  ServerListResponse,
  ToolListResponse,
  ToolTestRequest,
  ImportConfigRequest,
  ImportConfigResponse,
  ExportConfigResponse,
  ExportToolRequest,
  ExportToolDefinition,
} from "@/types/mcp";

// Get API configuration from localStorage or environment
const getApiConfig = () => {
  const savedEndpoint = localStorage.getItem("crewai_api_endpoint");
  const savedToken = localStorage.getItem("crewai_api_token");

  return {
    endpoint:
      savedEndpoint ||
      import.meta.env.VITE_CREWAI_RUNNER_API_HOST ||
      "http://localhost:8000/api",
    token:
      savedToken ||
      import.meta.env.VITE_CREWAI_API_TOKEN ||
      "",
  };
};

// Helper function for API calls
async function apiCall<T>(
  endpoint: string,
  options: RequestInit = {}
): Promise<T> {
  const config = getApiConfig();
  const url = `${config.endpoint}${endpoint}`;

  const headers: HeadersInit = {
    "Content-Type": "application/json",
    ...(config.token && { Authorization: `Bearer ${config.token}` }),
    ...options.headers,
  };

  const response = await fetch(url, {
    ...options,
    headers,
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({
      error: "Request failed",
      message: response.statusText,
    }));
    throw new Error(error.message || error.error || "API request failed");
  }

  return response.json();
}

export const mcpApi = {
  // Server Management
  async listServers(): Promise<MCPServer[]> {
    const response = await apiCall<ServerListResponse>("/mcp/servers");
    return response.servers;
  },

  async addServer(config: MCPServerConfig): Promise<MCPServer> {
    const response = await apiCall<AddServerResponse>("/mcp/servers", {
      method: "POST",
      body: JSON.stringify({ server: config }),
    });
    return response.server;
  },

  async updateServer(
    serverId: string,
    config: MCPServerConfig
  ): Promise<MCPServer> {
    const response = await apiCall<UpdateServerResponse>(
      `/mcp/servers/${serverId}`,
      {
        method: "PUT",
        body: JSON.stringify({ server: config }),
      }
    );
    return response.server;
  },

  async deleteServer(serverId: string): Promise<DeleteServerResponse> {
    return apiCall<DeleteServerResponse>(`/mcp/servers/${serverId}`, {
      method: "DELETE",
    });
  },

  async testConnection(serverId: string): Promise<MCPConnectionStatus> {
    const response = await apiCall<TestConnectionResponse>(
      `/mcp/servers/${serverId}/connect`,
      {
        method: "POST",
      }
    );
    return response.connection_status;
  },

  async getServerStatus(serverId: string): Promise<MCPConnectionStatus> {
    return apiCall<MCPConnectionStatus>(`/mcp/servers/${serverId}/status`);
  },

  // Tool Operations
  async listServerTools(serverId: string): Promise<MCPTool[]> {
    const response = await apiCall<ToolListResponse>(
      `/mcp/servers/${serverId}/tools`
    );
    return response.tools;
  },

  async listAllTools(): Promise<MCPTool[]> {
    const response = await apiCall<ToolListResponse>("/mcp/tools");
    return response.tools;
  },

  async testTool(
    serverId: string,
    toolName: string,
    parameters: Record<string, any>
  ): Promise<MCPToolTestResult> {
    return apiCall<MCPToolTestResult>("/mcp/tools/test", {
      method: "POST",
      body: JSON.stringify({
        server_id: serverId,
        tool_name: toolName,
        parameters,
      } as ToolTestRequest),
    });
  },

  async getToolSchema(toolId: string): Promise<any> {
    return apiCall<any>(`/mcp/tools/${toolId}/schema`);
  },

  // Import/Export
  async importConfig(
    configContent: string,
    configFormat: "claude_desktop" | "cline" | "custom" = "claude_desktop"
  ): Promise<ImportConfigResponse> {
    return apiCall<ImportConfigResponse>("/mcp/import/config", {
      method: "POST",
      body: JSON.stringify({
        config_content: configContent,
        config_format: configFormat,
      } as ImportConfigRequest),
    });
  },

  async exportConfig(format: string = "custom"): Promise<ExportConfigResponse> {
    return apiCall<ExportConfigResponse>(`/mcp/export/config?format=${format}`);
  },

  async exportTool(
    toolId: string,
    framework: "crewai" | "langgraph" | "yaml"
  ): Promise<ExportToolDefinition> {
    return apiCall<ExportToolDefinition>(`/mcp/tools/${toolId}/export`, {
      method: "POST",
      body: JSON.stringify({ framework } as ExportToolRequest),
    });
  },
};

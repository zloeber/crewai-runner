/**
 * TypeScript types for MCP (Model Context Protocol) server management
 */

export type TransportType = "stdio" | "http" | "websocket";
export type ServerStatus = "connected" | "disconnected" | "error";
export type ExportFramework = "crewai" | "langgraph" | "yaml";
export type ConfigFormat = "claude_desktop" | "cline" | "custom";

export interface MCPTransport {
  type: TransportType;
  command?: string;
  args?: string[];
  host?: string;
  port?: number;
  url?: string;
}

export interface MCPServerConfig {
  name: string;
  description?: string;
  transport: MCPTransport;
  env?: Record<string, string>;
  tools: string[];
  enabled: boolean;
}

export interface MCPServer extends MCPServerConfig {
  id: string;
  status: ServerStatus;
  error_message?: string;
}

export interface MCPConnectionStatus {
  status: ServerStatus;
  message: string;
  latency_ms?: number;
  transport_type: string;
  initialization_success: boolean;
}

export interface MCPToolSchema {
  name: string;
  description?: string;
  input_schema: Record<string, any>;
  output_schema?: Record<string, any>;
}

export interface MCPTool {
  id: string;
  server_id: string;
  server_name: string;
  name: string;
  description?: string;
  input_schema: Record<string, any>;
  output_schema?: Record<string, any>;
}

export interface MCPToolTestResult {
  tool_name: string;
  success: boolean;
  result?: any;
  error?: string;
  execution_time_ms: number;
  request: Record<string, any>;
  response: Record<string, any>;
}

export interface ExportToolDefinition {
  tool_definition: string;
  framework: ExportFramework;
  instructions?: string;
}

// API Request/Response types
export interface AddServerRequest {
  server: MCPServerConfig;
}

export interface AddServerResponse {
  server: MCPServer;
}

export interface UpdateServerRequest {
  server: MCPServerConfig;
}

export interface UpdateServerResponse {
  server: MCPServer;
}

export interface DeleteServerResponse {
  id: string;
  message: string;
}

export interface TestConnectionResponse {
  server_id: string;
  connection_status: MCPConnectionStatus;
}

export interface ServerListResponse {
  servers: MCPServer[];
}

export interface ToolListResponse {
  tools: MCPTool[];
}

export interface ToolTestRequest {
  server_id: string;
  tool_name: string;
  parameters: Record<string, any>;
}

export interface ImportConfigRequest {
  config_content: string;
  config_format: ConfigFormat;
}

export interface ImportConfigResponse {
  imported_count: number;
  servers: MCPServer[];
  message: string;
}

export interface ExportConfigResponse {
  config_content: string;
  format: string;
}

export interface ExportToolRequest {
  framework: ExportFramework;
}

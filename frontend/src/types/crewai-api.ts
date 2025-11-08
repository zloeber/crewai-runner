// API request/response types for CrewAI integration

export interface ProviderConfig {
  id: string;
  name: string;
  type: "openai" | "anthropic" | "ollama" | "azure" | "custom";
  apiKey?: string;
  baseUrl?: string;
  models: ModelConfig[];
}

export interface ModelConfig {
  id: string;
  name: string;
  type: "llm" | "embedder";
  providerId: string;
  endpoint: string;
  default: boolean;
}

export interface WorkflowConfig {
  name: string;
  description?: string;
  agents: AgentConfig[];
  tasks: TaskConfig[];
}

export interface AgentConfig {
  name: string;
  role: string;
  goal: string;
  backstory: string;
  model: string;
  tools?: string[];
  allowDelegation?: boolean;
  verbose?: boolean;
}

export interface TaskConfig {
  name: string;
  description: string;
  expectedOutput: string;
  agent: string;
  tools?: string[];
  asyncExecution?: boolean;
  context?: string[];
  outputJson?: boolean;
}

export interface ChatMessage {
  id: string;
  role: "user" | "assistant" | "system";
  content: string;
  timestamp: string;
}

export interface StartWorkflowRequest {
  workflow: WorkflowConfig;
  providerConfig?: ProviderConfig;
}

export interface StartWorkflowResponse {
  workflowId: string;
  status: "started" | "running" | "completed" | "failed";
  message: string;
}

export interface StopWorkflowRequest {
  workflowId: string;
}

export interface StopWorkflowResponse {
  workflowId: string;
  status: "stopped" | "failed";
  message: string;
}

export interface ChatRequest {
  workflowId: string;
  message: string;
}

export interface ChatResponse {
  workflowId: string;
  response: string;
  timestamp: string;
}

export interface WorkflowStatusRequest {
  workflowId: string;
}

export interface WorkflowStatusResponse {
  workflowId: string;
  status: "idle" | "running" | "completed" | "failed" | "stopped";
  agents: {
    name: string;
    status: "idle" | "working" | "completed" | "failed";
    task?: string;
  }[];
  currentTask?: string;
  progress: number;
}

export interface ValidateYamlRequest {
  yamlContent: string;
}

export interface ValidateYamlResponse {
  valid: boolean;
  errors?: string[];
  workflow?: WorkflowConfig;
}

export interface ListProvidersResponse {
  providers: ProviderConfig[];
}

export interface ListModelsResponse {
  models: ModelConfig[];
}

export interface AddProviderRequest {
  provider: Omit<ProviderConfig, "id">;
}

export interface AddProviderResponse {
  provider: ProviderConfig;
}

export interface AddModelRequest {
  model: Omit<ModelConfig, "id">;
}

export interface AddModelResponse {
  model: ModelConfig;
}

// Profile Configuration Types
export interface ProfileMetadata {
  name: string;
  description?: string;
  version: string;
  created?: string;
  tags?: string[];
}

export interface MCPTransport {
  type: "stdio" | "http" | "websocket";
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
  tools?: string[];
  enabled?: boolean;
}

export interface ModelOverride {
  pattern?: string;
  agentName?: string;
  model: string;
  reason?: string;
}

export interface AgentDefaults {
  verbose?: boolean;
  allowDelegation?: boolean;
  model?: string;
  tools?: string[];
}

export interface TaskDefaults {
  asyncExecution?: boolean;
  outputJson?: boolean;
  timeoutMinutes?: number;
}

export interface WorkflowDefaults {
  verbose?: boolean;
  allowDelegation?: boolean;
  maxConcurrentTasks?: number;
  timeoutMinutes?: number;
  agentDefaults?: AgentDefaults;
  taskDefaults?: TaskDefaults;
}

export interface SecuritySettings {
  allowedDomains?: string[];
  restrictedTools?: string[];
  rateLimits?: Record<string, number>;
}

export interface ProfileConfig {
  apiVersion: "crewai/v1";
  kind: "Profile";
  metadata: ProfileMetadata;
  mcpServers?: MCPServerConfig[];
  providers?: ProviderConfig[];
  modelOverrides?: ModelOverride[];
  defaultToolSets?: Record<string, string[]>;
  workflowDefaults?: WorkflowDefaults;
  environment?: Record<string, string>;
  security?: SecuritySettings;
}

// Profile API Request/Response Types
export interface ProfileListResponse {
  profiles: ProfileMetadata[];
}

export interface LoadProfileRequest {
  name: string;
}

export interface LoadProfileResponse {
  profile: ProfileConfig;
}

export interface SaveProfileRequest {
  profile: ProfileConfig;
  overwrite?: boolean;
}

export interface SaveProfileResponse {
  name: string;
  message: string;
}

export interface DeleteProfileRequest {
  name: string;
}

export interface DeleteProfileResponse {
  name: string;
  message: string;
}

export interface ExportProfileResponse {
  name: string;
  yamlContent: string;
}

export interface ImportProfileRequest {
  yamlContent: string;
  overwrite?: boolean;
}

export interface ImportProfileResponse {
  name: string;
  message: string;
}
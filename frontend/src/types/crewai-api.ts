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
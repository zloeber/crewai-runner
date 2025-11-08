/**
 * TypeScript types for CrewAI Profile Configuration
 * Generated from profile.schema.json
 */

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

export interface Model {
  id?: string;
  name: string;
  type: "llm" | "embedder";
  providerId: string;
  endpoint: string;
  default?: boolean;
}

export interface Provider {
  id?: string;
  name: string;
  type: "openai" | "anthropic" | "ollama" | "azure" | "custom";
  apiKey?: string;
  baseUrl?: string;
  models?: Model[];
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
  providers?: Provider[];
  modelOverrides?: ModelOverride[];
  defaultToolSets?: Record<string, string[]>;
  workflowDefaults?: WorkflowDefaults;
  environment?: Record<string, string>;
  security?: SecuritySettings;
}

// API Request/Response types
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

// Profile state management types
export interface ProfileState {
  currentProfile: ProfileConfig | null;
  availableProfiles: ProfileMetadata[];
  isLoading: boolean;
  error: string | null;
}

// Profile validation types
export interface ProfileValidationError {
  path: string;
  message: string;
  code: string;
}

export interface ProfileValidationResult {
  isValid: boolean;
  errors: ProfileValidationError[];
  warnings: ProfileValidationError[];
}
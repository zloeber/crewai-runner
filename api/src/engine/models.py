"""Pydantic models for API request/response validation."""

from typing import Optional, List, Literal, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime


# Provider Models
class Model(BaseModel):
    id: Optional[str] = None
    name: str
    type: Literal["llm", "embedder"]
    providerId: str
    endpoint: str
    default: bool = False


class Provider(BaseModel):
    id: Optional[str] = None
    name: str
    type: Literal["openai", "anthropic", "ollama", "azure", "custom"]
    apiKey: Optional[str] = None
    baseUrl: Optional[str] = None
    models: List[Model] = []


class ProvidersResponse(BaseModel):
    providers: List[Provider]


class AddProviderRequest(BaseModel):
    provider: Provider


class AddProviderResponse(BaseModel):
    provider: Provider


# Model Models
class ModelsResponse(BaseModel):
    models: List[Model]


class AddModelRequest(BaseModel):
    model: Model


class AddModelResponse(BaseModel):
    model: Model


# Workflow Models
class Agent(BaseModel):
    name: str
    role: str
    goal: str
    backstory: str
    model: str
    tools: Optional[List[str]] = []
    allowDelegation: Optional[bool] = None
    verbose: Optional[bool] = None


class Task(BaseModel):
    name: str
    description: str
    expectedOutput: str
    agent: str
    tools: Optional[List[str]] = []
    asyncExecution: Optional[bool] = None
    context: Optional[List[str]] = []
    outputJson: Optional[bool] = None


class Workflow(BaseModel):
    name: str
    description: Optional[str] = None
    agents: List[Agent]
    tasks: List[Task]


class StartWorkflowRequest(BaseModel):
    workflow: Workflow
    providerConfig: Optional[Provider] = None


class StartWorkflowResponse(BaseModel):
    workflowId: str
    status: Literal["started", "running", "completed", "failed"]
    message: str


class StopWorkflowRequest(BaseModel):
    workflowId: str


class StopWorkflowResponse(BaseModel):
    workflowId: str
    status: Literal["stopped", "failed"]
    message: str


class AgentStatus(BaseModel):
    name: str
    status: Literal["idle", "working", "completed", "failed"]
    task: Optional[str] = None


class WorkflowStatusResponse(BaseModel):
    workflowId: str
    status: Literal["idle", "running", "completed", "failed", "stopped"]
    agents: List[AgentStatus]
    currentTask: Optional[str] = None
    progress: float = Field(ge=0, le=100)


# Chat Models
class SendMessageRequest(BaseModel):
    workflowId: str
    message: str


class SendMessageResponse(BaseModel):
    workflowId: str
    response: str
    timestamp: str


# YAML Models
class ValidateYAMLRequest(BaseModel):
    yamlContent: str


class ValidateYAMLResponse(BaseModel):
    valid: bool
    errors: Optional[List[str]] = None
    workflow: Optional[Workflow] = None


# Error Models
class ErrorResponse(BaseModel):
    error: str
    message: str


# Profile Configuration Models
class MCPTransport(BaseModel):
    type: Literal["stdio", "http", "websocket"] = "stdio"
    command: Optional[str] = None
    args: Optional[List[str]] = []
    host: Optional[str] = None
    port: Optional[int] = None
    url: Optional[str] = None


class MCPServerConfig(BaseModel):
    name: str
    description: Optional[str] = None
    transport: MCPTransport
    env: Optional[Dict[str, str]] = {}
    tools: List[str] = []
    enabled: bool = True


class ModelOverride(BaseModel):
    pattern: Optional[str] = None  # Pattern to match agent names/roles
    agentName: Optional[str] = None  # Specific agent name
    model: str
    reason: Optional[str] = None


class ToolSet(BaseModel):
    name: str
    tools: List[str]
    description: Optional[str] = None


class AgentDefaults(BaseModel):
    verbose: bool = True
    allowDelegation: bool = False
    model: Optional[str] = None
    tools: Optional[List[str]] = []


class TaskDefaults(BaseModel):
    asyncExecution: bool = False
    outputJson: bool = False
    timeoutMinutes: Optional[int] = None


class WorkflowDefaults(BaseModel):
    verbose: bool = True
    allowDelegation: bool = False
    maxConcurrentTasks: int = 3
    timeoutMinutes: int = 30
    agentDefaults: Optional[AgentDefaults] = None
    taskDefaults: Optional[TaskDefaults] = None


class SecuritySettings(BaseModel):
    allowedDomains: List[str] = []
    restrictedTools: List[str] = []
    rateLimits: Optional[Dict[str, int]] = {}


class ProfileMetadata(BaseModel):
    name: str
    description: Optional[str] = None
    version: str = "1.0.0"
    created: Optional[str] = None
    tags: List[str] = []


class ProfileConfig(BaseModel):
    apiVersion: str = "crewai/v1"
    kind: str = "Profile"
    metadata: ProfileMetadata
    mcpServers: List[MCPServerConfig] = []
    providers: List[Provider] = []
    modelOverrides: List[ModelOverride] = []
    defaultToolSets: Optional[Dict[str, List[str]]] = {}
    workflowDefaults: Optional[WorkflowDefaults] = None
    environment: Optional[Dict[str, str]] = {}
    security: Optional[SecuritySettings] = None


# Profile API Models
class ProfileListResponse(BaseModel):
    profiles: List[ProfileMetadata]


class LoadProfileRequest(BaseModel):
    name: str


class LoadProfileResponse(BaseModel):
    profile: ProfileConfig


class SaveProfileRequest(BaseModel):
    profile: ProfileConfig
    overwrite: bool = False


class SaveProfileResponse(BaseModel):
    name: str
    message: str


class DeleteProfileRequest(BaseModel):
    name: str


class DeleteProfileResponse(BaseModel):
    name: str
    message: str


class ExportProfileResponse(BaseModel):
    name: str
    yamlContent: str


class ImportProfileRequest(BaseModel):
    yamlContent: str
    overwrite: bool = False


class ImportProfileResponse(BaseModel):
    name: str
    message: str

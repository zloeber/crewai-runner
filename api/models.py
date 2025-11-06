"""Pydantic models for API request/response validation."""

from typing import Optional, List, Literal
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

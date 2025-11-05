import {
  StartWorkflowRequest,
  StartWorkflowResponse,
  StopWorkflowRequest,
  StopWorkflowResponse,
  ChatRequest,
  ChatResponse,
  WorkflowStatusRequest,
  WorkflowStatusResponse,
  ValidateYamlRequest,
  ValidateYamlResponse,
  ListProvidersResponse,
  ListModelsResponse,
  AddProviderRequest,
  AddProviderResponse,
  AddModelRequest,
  AddModelResponse,
  ProviderConfig,
  ModelConfig,
  WorkflowConfig
} from "@/types/crewai-api";

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000/api";

class CrewAIApi {
  private async request<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
    const url = `${API_BASE_URL}${endpoint}`;
    const response = await fetch(url, {
      headers: {
        "Content-Type": "application/json",
        ...options.headers,
      },
      ...options,
    });

    if (!response.ok) {
      throw new Error(`API request failed: ${response.status} ${response.statusText}`);
    }

    return response.json();
  }

  // Workflow endpoints
  async startWorkflow(data: StartWorkflowRequest): Promise<StartWorkflowResponse> {
    return this.request("/workflows/start", {
      method: "POST",
      body: JSON.stringify(data),
    });
  }

  async stopWorkflow(data: StopWorkflowRequest): Promise<StopWorkflowResponse> {
    return this.request("/workflows/stop", {
      method: "POST",
      body: JSON.stringify(data),
    });
  }

  async getWorkflowStatus(data: WorkflowStatusRequest): Promise<WorkflowStatusResponse> {
    return this.request(`/workflows/${data.workflowId}/status`);
  }

  // Chat endpoints
  async sendMessage(data: ChatRequest): Promise<ChatResponse> {
    return this.request("/chat", {
      method: "POST",
      body: JSON.stringify(data),
    });
  }

  // Configuration endpoints
  async listProviders(): Promise<ListProvidersResponse> {
    return this.request("/providers");
  }

  async addProvider(data: AddProviderRequest): Promise<AddProviderResponse> {
    return this.request("/providers", {
      method: "POST",
      body: JSON.stringify(data),
    });
  }

  async listModels(): Promise<ListModelsResponse> {
    return this.request("/models");
  }

  async addModel(data: AddModelRequest): Promise<AddModelResponse> {
    return this.request("/models", {
      method: "POST",
      body: JSON.stringify(data),
    });
  }

  // YAML endpoints
  async validateYaml(data: ValidateYamlRequest): Promise<ValidateYamlResponse> {
    return this.request("/yaml/validate", {
      method: "POST",
      body: JSON.stringify(data),
    });
  }

  // Utility method to load a workflow from YAML
  async loadWorkflowFromYaml(yamlContent: string): Promise<WorkflowConfig | null> {
    const response = await this.validateYaml({ yamlContent });
    return response.valid ? response.workflow || null : null;
  }
}

export const crewAIApi = new CrewAIApi();
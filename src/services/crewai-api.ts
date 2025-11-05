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
    
    // Add default headers
    const headers = {
      "Content-Type": "application/json",
      ...options.headers,
    };

    try {
      const response = await fetch(url, {
        headers,
        ...options,
      });

      if (!response.ok) {
        let errorMessage = `API request failed: ${response.status} ${response.statusText}`;
        
        try {
          const errorData = await response.json();
          if (errorData.message) {
            errorMessage = errorData.message;
          }
        } catch (e) {
          // If we can't parse the error response, use the default message
        }
        
        throw new Error(errorMessage);
      }

      return response.json();
    } catch (error) {
      // If it's a network error or CORS issue, provide a more helpful message
      if (error instanceof TypeError && error.message === 'Failed to fetch') {
        throw new Error('Unable to connect to the API server. Please ensure the backend is running.');
      }
      
      // Re-throw other errors
      throw error;
    }
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
    try {
      return await this.request("/providers");
    } catch (error) {
      console.warn("Failed to load providers, using empty list:", error);
      return { providers: [] };
    }
  }

  async addProvider(data: AddProviderRequest): Promise<AddProviderResponse> {
    return this.request("/providers", {
      method: "POST",
      body: JSON.stringify(data),
    });
  }

  async listModels(): Promise<ListModelsResponse> {
    try {
      return await this.request("/models");
    } catch (error) {
      console.warn("Failed to load models, using empty list:", error);
      return { models: [] };
    }
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
    try {
      const response = await this.validateYaml({ yamlContent });
      return response.valid ? response.workflow || null : null;
    } catch (error) {
      console.error("Failed to validate YAML:", error);
      return null;
    }
  }
}

export const crewAIApi = new CrewAIApi();
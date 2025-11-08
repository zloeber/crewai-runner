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
  WorkflowConfig,
  // Profile types
  ProfileListResponse,
  LoadProfileRequest,
  LoadProfileResponse,
  SaveProfileRequest,
  SaveProfileResponse,
  DeleteProfileRequest,
  DeleteProfileResponse,
  ExportProfileResponse,
  ImportProfileRequest,
  ImportProfileResponse,
  ProfileConfig
} from "../types/crewai-api";

class CrewAIApi {
  private authToken: string | null = null;

  // Get the current API base URL (supports dynamic configuration)
  getApiBaseUrl(): string {
    // First check localStorage for user configuration
    const stored = localStorage.getItem('crewai_api_endpoint');
    if (stored) {
      return stored;
    }
    
    // Fall back to environment variable
    return import.meta.env.VITE_CREWAI_RUNNER_API_HOST || "http://localhost:8000";
  }

  // Set the API base URL
  setApiBaseUrl(url: string) {
    localStorage.setItem('crewai_api_endpoint', url);
  }

  // Set the authorization token
  setAuthToken(token: string | null) {
    this.authToken = token;
    // Store in localStorage for persistence
    if (token) {
      localStorage.setItem('crewai_auth_token', token);
    } else {
      localStorage.removeItem('crewai_auth_token');
    }
  }

  // Get the current auth token
  getAuthToken(): string | null {
    // First check in-memory token
    if (this.authToken) {
      return this.authToken;
    }
    
    // Fall back to localStorage
    const stored = localStorage.getItem('crewai_auth_token');
    if (stored) {
      this.authToken = stored;
      return stored;
    }
    
    // Check environment variable as fallback
    const envToken = import.meta.env.VITE_CREWAI_API_TOKEN;
    if (envToken) {
      return envToken;
    }
    
    return null;
  }

  private async request<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
    // For API endpoints, prepend /api if not already present
    // For health check, use the endpoint as-is
    const apiEndpoint = endpoint.startsWith('/health') ? endpoint : `/api${endpoint}`;
    const url = `${this.getApiBaseUrl()}${apiEndpoint}`;
    
    // Add default headers
    const headers: Record<string, string> = {
      "Content-Type": "application/json",
      ...(options.headers as Record<string, string>),
    };

    // Add authorization header if token is available
    const token = this.getAuthToken();
    if (token) {
      headers.Authorization = `Bearer ${token}`;
    }

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

  // Health check endpoint
  async healthCheck(): Promise<{ status: string }> {
    return this.request("/health");
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

  // Authentication utility methods
  isAuthenticated(): boolean {
    return this.getAuthToken() !== null;
  }

  clearAuth(): void {
    this.setAuthToken(null);
  }

  // Test authentication by making a simple request
  async testAuth(): Promise<boolean> {
    try {
      await this.listProviders();
      return true;
    } catch (error) {
      // If we get a 401/403, auth failed
      if (error instanceof Error && (error.message.includes('401') || error.message.includes('403'))) {
        return false;
      }
      // For other errors, we assume auth is OK but there's another issue
      return true;
    }
  }

  // Profile management endpoints
  async listProfiles(): Promise<ProfileListResponse> {
    try {
      return await this.request("/profiles");
    } catch (error) {
      console.warn("Failed to load profiles, using empty list:", error);
      return { profiles: [] };
    }
  }

  async loadProfile(data: LoadProfileRequest): Promise<LoadProfileResponse> {
    return this.request("/profiles/load", {
      method: "POST",
      body: JSON.stringify(data),
    });
  }

  async getProfile(name: string): Promise<LoadProfileResponse> {
    return this.request(`/profiles/${encodeURIComponent(name)}`);
  }

  async saveProfile(data: SaveProfileRequest): Promise<SaveProfileResponse> {
    return this.request("/profiles/save", {
      method: "POST",
      body: JSON.stringify(data),
    });
  }

  async deleteProfile(name: string): Promise<DeleteProfileResponse> {
    return this.request(`/profiles/${encodeURIComponent(name)}`, {
      method: "DELETE",
    });
  }

  async exportProfile(name: string): Promise<ExportProfileResponse> {
    return this.request(`/profiles/${encodeURIComponent(name)}/export`);
  }

  async importProfile(data: ImportProfileRequest): Promise<ImportProfileResponse> {
    return this.request("/profiles/import", {
      method: "POST",
      body: JSON.stringify(data),
    });
  }
}

export const crewAIApi = new CrewAIApi();
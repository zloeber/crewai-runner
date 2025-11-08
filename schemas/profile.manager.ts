/**
 * Profile management utilities
 * Common functions for working with CrewAI profiles
 */

import { 
  ProfileConfig, 
  ProfileMetadata,
  LoadProfileRequest,
  LoadProfileResponse,
  SaveProfileRequest,
  SaveProfileResponse,
  DeleteProfileRequest,
  DeleteProfileResponse,
  ExportProfileResponse,
  ImportProfileRequest,
  ImportProfileResponse,
  ProfileListResponse
} from './profile.types';
import { ProfileValidator } from './profile.validator';

export class ProfileManager {
  private baseUrl: string;
  private authToken: string | null = null;

  constructor(baseUrl: string, authToken?: string) {
    this.baseUrl = baseUrl.replace(/\/$/, ''); // Remove trailing slash
    this.authToken = authToken || null;
  }

  /**
   * Set authentication token
   */
  setAuthToken(token: string | null) {
    this.authToken = token;
  }

  /**
   * Get HTTP headers for API requests
   */
  private getHeaders(): HeadersInit {
    const headers: HeadersInit = {
      'Content-Type': 'application/json',
    };

    if (this.authToken) {
      headers['Authorization'] = `Bearer ${this.authToken}`;
    }

    return headers;
  }

  /**
   * Handle API responses
   */
  private async handleResponse<T>(response: Response): Promise<T> {
    if (!response.ok) {
      const errorData = await response.json().catch(() => ({
        error: 'Unknown error',
        message: `HTTP ${response.status}: ${response.statusText}`
      }));
      throw new Error(errorData.message || errorData.error || 'API request failed');
    }

    return response.json();
  }

  /**
   * List all available profiles
   */
  async listProfiles(): Promise<ProfileMetadata[]> {
    const response = await fetch(`${this.baseUrl}/api/profiles`, {
      method: 'GET',
      headers: this.getHeaders(),
    });

    const data = await this.handleResponse<ProfileListResponse>(response);
    return data.profiles;
  }

  /**
   * Load a specific profile by name
   */
  async loadProfile(name: string): Promise<ProfileConfig> {
    const request: LoadProfileRequest = { name };

    const response = await fetch(`${this.baseUrl}/api/profiles/load`, {
      method: 'POST',
      headers: this.getHeaders(),
      body: JSON.stringify(request),
    });

    const data = await this.handleResponse<LoadProfileResponse>(response);
    return data.profile;
  }

  /**
   * Get a specific profile by name (alternative to loadProfile)
   */
  async getProfile(name: string): Promise<ProfileConfig> {
    const response = await fetch(`${this.baseUrl}/api/profiles/${encodeURIComponent(name)}`, {
      method: 'GET',
      headers: this.getHeaders(),
    });

    const data = await this.handleResponse<LoadProfileResponse>(response);
    return data.profile;
  }

  /**
   * Save a profile configuration
   */
  async saveProfile(profile: ProfileConfig, overwrite: boolean = false): Promise<SaveProfileResponse> {
    // Validate profile before saving
    const validation = ProfileValidator.validateProfile(profile);
    if (!validation.isValid) {
      const errorMessages = validation.errors.map(e => `${e.path}: ${e.message}`).join('; ');
      throw new Error(`Profile validation failed: ${errorMessages}`);
    }

    const request: SaveProfileRequest = {
      profile,
      overwrite
    };

    const response = await fetch(`${this.baseUrl}/api/profiles/save`, {
      method: 'POST',
      headers: this.getHeaders(),
      body: JSON.stringify(request),
    });

    return this.handleResponse<SaveProfileResponse>(response);
  }

  /**
   * Delete a profile by name
   */
  async deleteProfile(name: string): Promise<DeleteProfileResponse> {
    const response = await fetch(`${this.baseUrl}/api/profiles/${encodeURIComponent(name)}`, {
      method: 'DELETE',
      headers: this.getHeaders(),
    });

    return this.handleResponse<DeleteProfileResponse>(response);
  }

  /**
   * Export a profile as YAML
   */
  async exportProfile(name: string): Promise<ExportProfileResponse> {
    const response = await fetch(`${this.baseUrl}/api/profiles/${encodeURIComponent(name)}/export`, {
      method: 'GET',
      headers: this.getHeaders(),
    });

    return this.handleResponse<ExportProfileResponse>(response);
  }

  /**
   * Import a profile from YAML content
   */
  async importProfile(yamlContent: string, overwrite: boolean = false): Promise<ImportProfileResponse> {
    const request: ImportProfileRequest = {
      yamlContent,
      overwrite
    };

    const response = await fetch(`${this.baseUrl}/api/profiles/import`, {
      method: 'POST',
      headers: this.getHeaders(),
      body: JSON.stringify(request),
    });

    return this.handleResponse<ImportProfileResponse>(response);
  }

  /**
   * Create a new empty profile with defaults
   */
  createEmptyProfile(name: string, description?: string): ProfileConfig {
    if (!ProfileValidator.validateProfileName(name)) {
      throw new Error('Invalid profile name. Use lowercase alphanumeric characters and hyphens only.');
    }

    return {
      apiVersion: 'crewai/v1',
      kind: 'Profile',
      metadata: {
        name,
        description: description || `Profile configuration for ${name}`,
        version: '1.0.0',
        created: new Date().toISOString(),
        tags: []
      },
      mcpServers: [],
      providers: [],
      modelOverrides: [],
      defaultToolSets: {},
      workflowDefaults: {
        verbose: true,
        allowDelegation: false,
        maxConcurrentTasks: 3,
        timeoutMinutes: 30,
        agentDefaults: {
          verbose: true,
          allowDelegation: false,
          tools: []
        },
        taskDefaults: {
          asyncExecution: false,
          outputJson: false
        }
      },
      environment: {},
      security: {
        allowedDomains: [],
        restrictedTools: [],
        rateLimits: {}
      }
    };
  }

  /**
   * Clone an existing profile with a new name
   */
  async cloneProfile(sourceName: string, targetName: string, description?: string): Promise<ProfileConfig> {
    if (!ProfileValidator.validateProfileName(targetName)) {
      throw new Error('Invalid target profile name. Use lowercase alphanumeric characters and hyphens only.');
    }

    const sourceProfile = await this.loadProfile(sourceName);
    
    const clonedProfile: ProfileConfig = {
      ...sourceProfile,
      metadata: {
        ...sourceProfile.metadata,
        name: targetName,
        description: description || `Cloned from ${sourceName}`,
        version: '1.0.0',
        created: new Date().toISOString()
      }
    };

    return clonedProfile;
  }

  /**
   * Validate a profile configuration
   */
  validateProfile(profile: Partial<ProfileConfig>) {
    return ProfileValidator.validateProfile(profile);
  }

  /**
   * Get profile summary information
   */
  getProfileSummary(profile: ProfileConfig) {
    return {
      name: profile.metadata.name,
      description: profile.metadata.description,
      version: profile.metadata.version,
      mcpServerCount: profile.mcpServers?.length || 0,
      providerCount: profile.providers?.length || 0,
      modelOverrideCount: profile.modelOverrides?.length || 0,
      hasWorkflowDefaults: !!profile.workflowDefaults,
      hasSecurity: !!profile.security,
      environmentVarCount: Object.keys(profile.environment || {}).length,
      tags: profile.metadata.tags || []
    };
  }

  /**
   * Compare two profiles and return differences
   */
  compareProfiles(profile1: ProfileConfig, profile2: ProfileConfig) {
    const summary1 = this.getProfileSummary(profile1);
    const summary2 = this.getProfileSummary(profile2);

    const differences = [];

    if (summary1.mcpServerCount !== summary2.mcpServerCount) {
      differences.push(`MCP servers: ${summary1.mcpServerCount} vs ${summary2.mcpServerCount}`);
    }

    if (summary1.providerCount !== summary2.providerCount) {
      differences.push(`Providers: ${summary1.providerCount} vs ${summary2.providerCount}`);
    }

    if (summary1.modelOverrideCount !== summary2.modelOverrideCount) {
      differences.push(`Model overrides: ${summary1.modelOverrideCount} vs ${summary2.modelOverrideCount}`);
    }

    if (summary1.environmentVarCount !== summary2.environmentVarCount) {
      differences.push(`Environment variables: ${summary1.environmentVarCount} vs ${summary2.environmentVarCount}`);
    }

    return differences;
  }
}
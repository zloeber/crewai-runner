/**
 * Profile validation utilities
 * Provides client-side validation for CrewAI profile configurations
 */

import { 
  ProfileConfig, 
  ProfileValidationError, 
  ProfileValidationResult,
  ProfileMetadata 
} from './profile.types';

const PROFILE_NAME_PATTERN = /^[a-z0-9-]+$/;
const VERSION_PATTERN = /^\d+\.\d+\.\d+$/;

export class ProfileValidator {
  /**
   * Validate a complete profile configuration
   */
  static validateProfile(profile: Partial<ProfileConfig>): ProfileValidationResult {
    const errors: ProfileValidationError[] = [];
    const warnings: ProfileValidationError[] = [];

    // Validate required fields
    if (!profile.apiVersion) {
      errors.push({
        path: 'apiVersion',
        message: 'API version is required',
        code: 'REQUIRED_FIELD'
      });
    } else if (profile.apiVersion !== 'crewai/v1') {
      errors.push({
        path: 'apiVersion',
        message: 'API version must be "crewai/v1"',
        code: 'INVALID_VALUE'
      });
    }

    if (!profile.kind) {
      errors.push({
        path: 'kind',
        message: 'Kind is required',
        code: 'REQUIRED_FIELD'
      });
    } else if (profile.kind !== 'Profile') {
      errors.push({
        path: 'kind',
        message: 'Kind must be "Profile"',
        code: 'INVALID_VALUE'
      });
    }

    if (!profile.metadata) {
      errors.push({
        path: 'metadata',
        message: 'Metadata is required',
        code: 'REQUIRED_FIELD'
      });
    } else {
      const metadataValidation = this.validateMetadata(profile.metadata);
      errors.push(...metadataValidation.errors);
      warnings.push(...metadataValidation.warnings);
    }

    // Validate optional sections
    if (profile.mcpServers) {
      const mcpValidation = this.validateMCPServers(profile.mcpServers);
      errors.push(...mcpValidation.errors);
      warnings.push(...mcpValidation.warnings);
    }

    if (profile.providers) {
      const providersValidation = this.validateProviders(profile.providers);
      errors.push(...providersValidation.errors);
      warnings.push(...providersValidation.warnings);
    }

    if (profile.modelOverrides) {
      const overridesValidation = this.validateModelOverrides(profile.modelOverrides);
      errors.push(...overridesValidation.errors);
      warnings.push(...overridesValidation.warnings);
    }

    if (profile.workflowDefaults) {
      const workflowValidation = this.validateWorkflowDefaults(profile.workflowDefaults);
      errors.push(...workflowValidation.errors);
      warnings.push(...workflowValidation.warnings);
    }

    return {
      isValid: errors.length === 0,
      errors,
      warnings
    };
  }

  /**
   * Validate profile metadata
   */
  static validateMetadata(metadata: Partial<ProfileMetadata>): ProfileValidationResult {
    const errors: ProfileValidationError[] = [];
    const warnings: ProfileValidationError[] = [];

    if (!metadata.name) {
      errors.push({
        path: 'metadata.name',
        message: 'Profile name is required',
        code: 'REQUIRED_FIELD'
      });
    } else if (!PROFILE_NAME_PATTERN.test(metadata.name)) {
      errors.push({
        path: 'metadata.name',
        message: 'Profile name must be lowercase alphanumeric with hyphens only',
        code: 'INVALID_FORMAT'
      });
    }

    if (!metadata.version) {
      errors.push({
        path: 'metadata.version',
        message: 'Profile version is required',
        code: 'REQUIRED_FIELD'
      });
    } else if (!VERSION_PATTERN.test(metadata.version)) {
      errors.push({
        path: 'metadata.version',
        message: 'Version must follow semantic versioning (e.g., 1.0.0)',
        code: 'INVALID_FORMAT'
      });
    }

    if (metadata.created) {
      try {
        new Date(metadata.created);
      } catch {
        errors.push({
          path: 'metadata.created',
          message: 'Created timestamp must be a valid ISO date',
          code: 'INVALID_FORMAT'
        });
      }
    }

    if (!metadata.description) {
      warnings.push({
        path: 'metadata.description',
        message: 'Profile description is recommended for better documentation',
        code: 'MISSING_RECOMMENDED'
      });
    }

    return { isValid: errors.length === 0, errors, warnings };
  }

  /**
   * Validate MCP servers configuration
   */
  static validateMCPServers(servers: any[]): ProfileValidationResult {
    const errors: ProfileValidationError[] = [];
    const warnings: ProfileValidationError[] = [];

    const serverNames = new Set<string>();

    servers.forEach((server, index) => {
      const basePath = `mcpServers[${index}]`;

      if (!server.name) {
        errors.push({
          path: `${basePath}.name`,
          message: 'MCP server name is required',
          code: 'REQUIRED_FIELD'
        });
      } else if (serverNames.has(server.name)) {
        errors.push({
          path: `${basePath}.name`,
          message: `Duplicate MCP server name: ${server.name}`,
          code: 'DUPLICATE_VALUE'
        });
      } else {
        serverNames.add(server.name);
      }

      if (!server.transport) {
        errors.push({
          path: `${basePath}.transport`,
          message: 'MCP server transport configuration is required',
          code: 'REQUIRED_FIELD'
        });
      } else {
        if (!server.transport.type) {
          errors.push({
            path: `${basePath}.transport.type`,
            message: 'Transport type is required',
            code: 'REQUIRED_FIELD'
          });
        } else if (!['stdio', 'http', 'websocket'].includes(server.transport.type)) {
          errors.push({
            path: `${basePath}.transport.type`,
            message: 'Transport type must be stdio, http, or websocket',
            code: 'INVALID_VALUE'
          });
        }

        if (server.transport.type === 'stdio' && !server.transport.command) {
          errors.push({
            path: `${basePath}.transport.command`,
            message: 'Command is required for stdio transport',
            code: 'REQUIRED_FIELD'
          });
        }

        if ((server.transport.type === 'http' || server.transport.type === 'websocket') &&
            !server.transport.url && (!server.transport.host || !server.transport.port)) {
          errors.push({
            path: `${basePath}.transport`,
            message: 'Either URL or host+port is required for http/websocket transport',
            code: 'MISSING_REQUIRED_COMBINATION'
          });
        }
      }

      if (!server.description) {
        warnings.push({
          path: `${basePath}.description`,
          message: 'MCP server description is recommended',
          code: 'MISSING_RECOMMENDED'
        });
      }
    });

    return { isValid: errors.length === 0, errors, warnings };
  }

  /**
   * Validate providers configuration
   */
  static validateProviders(providers: any[]): ProfileValidationResult {
    const errors: ProfileValidationError[] = [];
    const warnings: ProfileValidationError[] = [];

    const providerNames = new Set<string>();

    providers.forEach((provider, index) => {
      const basePath = `providers[${index}]`;

      if (!provider.name) {
        errors.push({
          path: `${basePath}.name`,
          message: 'Provider name is required',
          code: 'REQUIRED_FIELD'
        });
      } else if (providerNames.has(provider.name)) {
        errors.push({
          path: `${basePath}.name`,
          message: `Duplicate provider name: ${provider.name}`,
          code: 'DUPLICATE_VALUE'
        });
      } else {
        providerNames.add(provider.name);
      }

      if (!provider.type) {
        errors.push({
          path: `${basePath}.type`,
          message: 'Provider type is required',
          code: 'REQUIRED_FIELD'
        });
      } else if (!['openai', 'anthropic', 'ollama', 'azure', 'custom'].includes(provider.type)) {
        errors.push({
          path: `${basePath}.type`,
          message: 'Provider type must be one of: openai, anthropic, ollama, azure, custom',
          code: 'INVALID_VALUE'
        });
      }

      if (provider.models) {
        provider.models.forEach((model: any, modelIndex: number) => {
          const modelPath = `${basePath}.models[${modelIndex}]`;

          if (!model.name) {
            errors.push({
              path: `${modelPath}.name`,
              message: 'Model name is required',
              code: 'REQUIRED_FIELD'
            });
          }

          if (!model.type) {
            errors.push({
              path: `${modelPath}.type`,
              message: 'Model type is required',
              code: 'REQUIRED_FIELD'
            });
          } else if (!['llm', 'embedder'].includes(model.type)) {
            errors.push({
              path: `${modelPath}.type`,
              message: 'Model type must be llm or embedder',
              code: 'INVALID_VALUE'
            });
          }

          if (!model.endpoint) {
            errors.push({
              path: `${modelPath}.endpoint`,
              message: 'Model endpoint is required',
              code: 'REQUIRED_FIELD'
            });
          }
        });
      }
    });

    return { isValid: errors.length === 0, errors, warnings };
  }

  /**
   * Validate model overrides configuration
   */
  static validateModelOverrides(overrides: any[]): ProfileValidationResult {
    const errors: ProfileValidationError[] = [];
    const warnings: ProfileValidationError[] = [];

    overrides.forEach((override, index) => {
      const basePath = `modelOverrides[${index}]`;

      if (!override.model) {
        errors.push({
          path: `${basePath}.model`,
          message: 'Model is required for override',
          code: 'REQUIRED_FIELD'
        });
      }

      if (!override.pattern && !override.agentName) {
        errors.push({
          path: basePath,
          message: 'Either pattern or agentName must be specified',
          code: 'MISSING_REQUIRED_COMBINATION'
        });
      }

      if (override.pattern) {
        try {
          new RegExp(override.pattern);
        } catch {
          errors.push({
            path: `${basePath}.pattern`,
            message: 'Pattern must be a valid regular expression',
            code: 'INVALID_FORMAT'
          });
        }
      }

      if (!override.reason) {
        warnings.push({
          path: `${basePath}.reason`,
          message: 'Reason for model override is recommended for documentation',
          code: 'MISSING_RECOMMENDED'
        });
      }
    });

    return { isValid: errors.length === 0, errors, warnings };
  }

  /**
   * Validate workflow defaults configuration
   */
  static validateWorkflowDefaults(defaults: any): ProfileValidationResult {
    const errors: ProfileValidationError[] = [];
    const warnings: ProfileValidationError[] = [];

    if (defaults.maxConcurrentTasks !== undefined && 
        (typeof defaults.maxConcurrentTasks !== 'number' || defaults.maxConcurrentTasks < 1)) {
      errors.push({
        path: 'workflowDefaults.maxConcurrentTasks',
        message: 'Max concurrent tasks must be a positive number',
        code: 'INVALID_VALUE'
      });
    }

    if (defaults.timeoutMinutes !== undefined && 
        (typeof defaults.timeoutMinutes !== 'number' || defaults.timeoutMinutes < 1)) {
      errors.push({
        path: 'workflowDefaults.timeoutMinutes',
        message: 'Timeout minutes must be a positive number',
        code: 'INVALID_VALUE'
      });
    }

    if (defaults.taskDefaults?.timeoutMinutes !== undefined && 
        (typeof defaults.taskDefaults.timeoutMinutes !== 'number' || defaults.taskDefaults.timeoutMinutes < 1)) {
      errors.push({
        path: 'workflowDefaults.taskDefaults.timeoutMinutes',
        message: 'Task timeout minutes must be a positive number',
        code: 'INVALID_VALUE'
      });
    }

    return { isValid: errors.length === 0, errors, warnings };
  }

  /**
   * Quick validation for profile name
   */
  static validateProfileName(name: string): boolean {
    return PROFILE_NAME_PATTERN.test(name);
  }

  /**
   * Quick validation for semantic version
   */
  static validateVersion(version: string): boolean {
    return VERSION_PATTERN.test(version);
  }
}
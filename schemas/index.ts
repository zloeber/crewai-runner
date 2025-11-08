/**
 * CrewAI Profile Schema Library
 * 
 * This library provides comprehensive support for CrewAI profile management including:
 * - TypeScript types and interfaces
 * - JSON Schema validation
 * - Profile validation utilities
 * - Profile management API client
 * 
 * Usage:
 * ```typescript
 * import { ProfileManager, ProfileValidator, ProfileConfig } from './schemas';
 * 
 * // Create a profile manager
 * const manager = new ProfileManager('http://localhost:8000', 'your-api-token');
 * 
 * // List available profiles
 * const profiles = await manager.listProfiles();
 * 
 * // Load a specific profile
 * const profile = await manager.loadProfile('default');
 * 
 * // Validate a profile
 * const validation = ProfileValidator.validateProfile(profile);
 * ```
 */

// Export all types
export * from './profile.types';

// Export validation utilities
export { ProfileValidator } from './profile.validator';

// Export profile manager
export { ProfileManager } from './profile.manager';

// Export JSON schema (for runtime validation if needed)
export { default as profileSchema } from './profile.schema.json';

// Import for internal use
import { ProfileValidator } from './profile.validator';

// Version information
export const SCHEMA_VERSION = '1.0.0';
export const SUPPORTED_API_VERSIONS = ['crewai/v1'];

// Utility functions
export const utils = {
  /**
   * Check if a profile configuration is valid
   */
  isValidProfile: (profile: any): boolean => {
    try {
      const validation = ProfileValidator.validateProfile(profile);
      return validation.isValid;
    } catch {
      return false;
    }
  },

  /**
   * Get the profile name from a profile configuration
   */
  getProfileName: (profile: any): string | null => {
    return profile?.metadata?.name || null;
  },

  /**
   * Check if a string is a valid profile name
   */
  isValidProfileName: (name: string): boolean => {
    return ProfileValidator.validateProfileName(name);
  },

  /**
   * Check if a string is a valid semantic version
   */
  isValidVersion: (version: string): boolean => {
    return ProfileValidator.validateVersion(version);
  },

  /**
   * Generate a unique profile name based on a base name
   */
  generateUniqueProfileName: (baseName: string, existingNames: string[]): string => {
    let counter = 1;
    let candidateName = baseName;

    while (existingNames.includes(candidateName)) {
      candidateName = `${baseName}-${counter}`;
      counter++;
    }

    return candidateName;
  },

  /**
   * Format a profile for display
   */
  formatProfileForDisplay: (profile: any) => {
    if (!profile?.metadata) return 'Unknown Profile';
    
    const { name, description, version } = profile.metadata;
    return description ? `${name} (${version}) - ${description}` : `${name} (${version})`;
  }
};

// Constants
export const PROFILE_CONSTANTS = {
  DEFAULT_API_VERSION: 'crewai/v1',
  DEFAULT_KIND: 'Profile',
  DEFAULT_VERSION: '1.0.0',
  SUPPORTED_TRANSPORT_TYPES: ['stdio', 'http', 'websocket'],
  SUPPORTED_PROVIDER_TYPES: ['openai', 'anthropic', 'ollama', 'azure', 'custom'],
  SUPPORTED_MODEL_TYPES: ['llm', 'embedder'],
  PROFILE_NAME_PATTERN: /^[a-z0-9-]+$/,
  VERSION_PATTERN: /^\d+\.\d+\.\d+$/
} as const;
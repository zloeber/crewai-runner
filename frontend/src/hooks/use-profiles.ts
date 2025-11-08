import { useState, useEffect, useCallback } from 'react';
import { crewAIApi } from '../services/crewai-api';
import type { 
  ProfileConfig, 
  ProfileMetadata,
  LoadProfileResponse,
  SaveProfileResponse,
  DeleteProfileResponse,
  ExportProfileResponse,
  ImportProfileResponse
} from '../types/crewai-api';

interface UseProfilesReturn {
  // State
  profiles: ProfileMetadata[];
  currentProfile: ProfileConfig | null;
  loading: boolean;
  error: string | null;
  
  // Actions
  loadProfiles: () => Promise<void>;
  loadProfile: (name: string) => Promise<void>;
  saveProfile: (profile: ProfileConfig, overwrite?: boolean) => Promise<SaveProfileResponse>;
  deleteProfile: (name: string) => Promise<DeleteProfileResponse>;
  exportProfile: (name: string) => Promise<ExportProfileResponse>;
  importProfile: (yamlContent: string, overwrite?: boolean) => Promise<ImportProfileResponse>;
  clearCurrentProfile: () => void;
  clearError: () => void;
}

export const useProfiles = (): UseProfilesReturn => {
  const [profiles, setProfiles] = useState<ProfileMetadata[]>([]);
  const [currentProfile, setCurrentProfile] = useState<ProfileConfig | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Load all available profiles
  const loadProfiles = useCallback(async () => {
    setLoading(true);
    setError(null);
    
    try {
      const response = await crewAIApi.listProfiles();
      setProfiles(response.profiles);
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to load profiles';
      setError(errorMessage);
      console.error('Failed to load profiles:', err);
    } finally {
      setLoading(false);
    }
  }, []);

  // Load a specific profile
  const loadProfile = useCallback(async (name: string) => {
    setLoading(true);
    setError(null);
    
    try {
      const response = await crewAIApi.loadProfile({ name });
      setCurrentProfile(response.profile);
      
      // Also refresh the profiles list to ensure we have latest metadata
      await loadProfiles();
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : `Failed to load profile: ${name}`;
      setError(errorMessage);
      console.error('Failed to load profile:', err);
    } finally {
      setLoading(false);
    }
  }, [loadProfiles]);

  // Save a profile
  const saveProfile = useCallback(async (profile: ProfileConfig, overwrite: boolean = false): Promise<SaveProfileResponse> => {
    setLoading(true);
    setError(null);
    
    try {
      const response = await crewAIApi.saveProfile({ profile, overwrite });
      
      // Refresh profiles list after saving
      await loadProfiles();
      
      // If we saved the current profile, update it
      if (currentProfile?.metadata.name === profile.metadata.name) {
        setCurrentProfile(profile);
      }
      
      return response;
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to save profile';
      setError(errorMessage);
      console.error('Failed to save profile:', err);
      throw err;
    } finally {
      setLoading(false);
    }
  }, [currentProfile, loadProfiles]);

  // Delete a profile
  const deleteProfile = useCallback(async (name: string): Promise<DeleteProfileResponse> => {
    setLoading(true);
    setError(null);
    
    try {
      const response = await crewAIApi.deleteProfile(name);
      
      // Refresh profiles list after deletion
      await loadProfiles();
      
      // If we deleted the current profile, clear it
      if (currentProfile?.metadata.name === name) {
        setCurrentProfile(null);
      }
      
      return response;
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : `Failed to delete profile: ${name}`;
      setError(errorMessage);
      console.error('Failed to delete profile:', err);
      throw err;
    } finally {
      setLoading(false);
    }
  }, [currentProfile, loadProfiles]);

  // Export a profile
  const exportProfile = useCallback(async (name: string): Promise<ExportProfileResponse> => {
    setLoading(true);
    setError(null);
    
    try {
      const response = await crewAIApi.exportProfile(name);
      return response;
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : `Failed to export profile: ${name}`;
      setError(errorMessage);
      console.error('Failed to export profile:', err);
      throw err;
    } finally {
      setLoading(false);
    }
  }, []);

  // Import a profile
  const importProfile = useCallback(async (yamlContent: string, overwrite: boolean = false): Promise<ImportProfileResponse> => {
    setLoading(true);
    setError(null);
    
    try {
      const response = await crewAIApi.importProfile({ yamlContent, overwrite });
      
      // Refresh profiles list after import
      await loadProfiles();
      
      return response;
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : 'Failed to import profile';
      setError(errorMessage);
      console.error('Failed to import profile:', err);
      throw err;
    } finally {
      setLoading(false);
    }
  }, [loadProfiles]);

  // Clear current profile
  const clearCurrentProfile = useCallback(() => {
    setCurrentProfile(null);
  }, []);

  // Clear error
  const clearError = useCallback(() => {
    setError(null);
  }, []);

  // Load profiles on mount
  useEffect(() => {
    loadProfiles();
  }, [loadProfiles]);

  return {
    // State
    profiles,
    currentProfile,
    loading,
    error,
    
    // Actions
    loadProfiles,
    loadProfile,
    saveProfile,
    deleteProfile,
    exportProfile,
    importProfile,
    clearCurrentProfile,
    clearError,
  };
};
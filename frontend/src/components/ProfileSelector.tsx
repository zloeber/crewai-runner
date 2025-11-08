import React from 'react';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from './ui/select';
import { Button } from './ui/button';
import { Badge } from './ui/badge';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Loader2, RefreshCw, FileText, Settings } from 'lucide-react';
import { useProfiles } from '../hooks/use-profiles';
import type { ProfileConfig } from '../types/crewai-api';

interface ProfileSelectorProps {
  onProfileSelected?: (profile: ProfileConfig) => void;
  onManageProfiles?: () => void;
  className?: string;
}

export const ProfileSelector: React.FC<ProfileSelectorProps> = ({
  onProfileSelected,
  onManageProfiles,
  className = ''
}) => {
  const {
    profiles,
    currentProfile,
    loading,
    error,
    loadProfiles,
    loadProfile,
    clearError
  } = useProfiles();

  const handleProfileChange = async (profileName: string) => {
    try {
      await loadProfile(profileName);
      if (currentProfile && onProfileSelected) {
        onProfileSelected(currentProfile);
      }
    } catch (err) {
      // Error is handled by the hook
      console.error('Failed to load profile:', err);
    }
  };

  const handleRefresh = () => {
    clearError();
    loadProfiles();
  };

  return (
    <Card className={`w-full ${className}`}>
      <CardHeader className="pb-3">
        <CardTitle className="text-sm font-medium">Profile Configuration</CardTitle>
      </CardHeader>
      <CardContent className="space-y-3">
        {error && (
          <div className="text-sm text-red-600 bg-red-50 p-2 rounded border">
            {error}
          </div>
        )}

        <div className="flex gap-2">
          <div className="flex-1">
            <Select
              value={currentProfile?.metadata.name || ''}
              onValueChange={handleProfileChange}
              disabled={loading}
            >
              <SelectTrigger>
                <SelectValue placeholder={loading ? "Loading profiles..." : "Select a profile"} />
              </SelectTrigger>
              <SelectContent>
                {profiles.map((profile) => (
                  <SelectItem key={profile.name} value={profile.name}>
                    <div className="flex items-center justify-between w-full">
                      <span>{profile.name}</span>
                      <Badge variant="outline" className="ml-2 text-xs">
                        {profile.version}
                      </Badge>
                    </div>
                  </SelectItem>
                ))}
                {profiles.length === 0 && !loading && (
                  <SelectItem value="" disabled>
                    No profiles available
                  </SelectItem>
                )}
              </SelectContent>
            </Select>
          </div>
          
          <Button
            variant="outline"
            size="sm"
            onClick={handleRefresh}
            disabled={loading}
          >
            {loading ? (
              <Loader2 className="h-4 w-4 animate-spin" />
            ) : (
              <RefreshCw className="h-4 w-4" />
            )}
          </Button>

          {onManageProfiles && (
            <Button
              variant="outline"
              size="sm"
              onClick={onManageProfiles}
            >
              <Settings className="h-4 w-4" />
            </Button>
          )}
        </div>

        {currentProfile && (
          <div className="space-y-2 p-3 bg-muted/50 rounded-lg">
            <div className="flex items-center justify-between">
              <h4 className="font-medium text-sm">{currentProfile.metadata.name}</h4>
              <div className="flex gap-1">
                <Badge variant="outline" className="text-xs">
                  {currentProfile.metadata.version}
                </Badge>
                {currentProfile.metadata.tags?.map((tag: string, index: number) => (
                  <Badge key={index} variant="secondary" className="text-xs">
                    {tag}
                  </Badge>
                ))}
              </div>
            </div>
            
            {currentProfile.metadata.description && (
              <p className="text-xs text-muted-foreground">
                {currentProfile.metadata.description}
              </p>
            )}

            <div className="flex justify-between text-xs text-muted-foreground">
              <span>
                {currentProfile.mcpServers?.length || 0} MCP servers, {' '}
                {currentProfile.providers?.length || 0} providers
              </span>
              {currentProfile.metadata.created && (
                <span>
                  Created: {new Date(currentProfile.metadata.created).toLocaleDateString()}
                </span>
              )}
            </div>
          </div>
        )}

        {!currentProfile && !loading && profiles.length > 0 && (
          <div className="text-center py-4 text-muted-foreground">
            <FileText className="mx-auto h-8 w-8 mb-2 opacity-50" />
            <p className="text-sm">Select a profile to view configuration</p>
          </div>
        )}
      </CardContent>
    </Card>
  );
};
import React, { useState } from 'react';
import { Badge } from './ui/badge';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from './ui/card';
import { Button } from './ui/button';
import { Collapsible, CollapsibleContent, CollapsibleTrigger } from './ui/collapsible';
import { Separator } from './ui/separator';
import { 
  ChevronDown, 
  ChevronRight, 
  Server, 
  Cog, 
  Users, 
  Shield, 
  Download,
  Copy,
  Info,
  CheckCircle
} from 'lucide-react';
import type { 
  ProfileConfig, 
  ProfileMetadata,
  MCPServerConfig,
  ProviderConfig,
  ModelOverride,
  WorkflowDefaults 
} from '../types/crewai-api';

interface ProfileDisplayProps {
  profile: ProfileConfig | null;
  onExport?: (profileName: string) => void;
  onEdit?: (profile: ProfileConfig) => void;
  className?: string;
}

export const ProfileDisplay: React.FC<ProfileDisplayProps> = ({ 
  profile, 
  onExport, 
  onEdit, 
  className = '' 
}) => {
  const [expandedSections, setExpandedSections] = useState<Set<string>>(new Set());

  const toggleSection = (section: string) => {
    const newExpanded = new Set(expandedSections);
    if (newExpanded.has(section)) {
      newExpanded.delete(section);
    } else {
      newExpanded.add(section);
    }
    setExpandedSections(newExpanded);
  };

  const copyToClipboard = async (text: string) => {
    try {
      await navigator.clipboard.writeText(text);
      // You might want to show a toast notification here
    } catch (err) {
      console.error('Failed to copy to clipboard:', err);
    }
  };

  if (!profile) {
    return (
      <Card className={`w-full ${className}`}>
        <CardContent className="flex items-center justify-center py-8">
          <div className="text-center text-muted-foreground">
            <Info className="mx-auto h-12 w-12 mb-4 opacity-50" />
            <p>No profile loaded</p>
            <p className="text-sm">Load a profile to view its configuration</p>
          </div>
        </CardContent>
      </Card>
    );
  }

  const getSummaryStats = () => {
    return {
      mcpServers: profile.mcpServers?.length || 0,
      providers: profile.providers?.length || 0,
      models: profile.providers?.reduce((acc: number, p: ProviderConfig) => acc + (p.models?.length || 0), 0) || 0,
      overrides: profile.modelOverrides?.length || 0,
      tools: Object.values(profile.defaultToolSets || {}).flat().length,
      environments: Object.keys(profile.environment || {}).length
    };
  };

  const stats = getSummaryStats();

  return (
    <Card className={`w-full ${className}`}>
      <CardHeader>
        <div className="flex items-start justify-between">
          <div className="space-y-2">
            <CardTitle className="flex items-center gap-2">
              <CheckCircle className="h-5 w-5 text-green-500" />
              {profile.metadata.name}
            </CardTitle>
            <CardDescription>
              {profile.metadata.description || 'No description provided'}
            </CardDescription>
            <div className="flex items-center gap-2">
              <Badge variant="outline">{profile.metadata.version}</Badge>
              {profile.metadata.tags?.map((tag: string, index: number) => (
                <Badge key={index} variant="secondary">{tag}</Badge>
              ))}
            </div>
          </div>
          <div className="flex gap-2">
            {onExport && (
              <Button
                variant="outline"
                size="sm"
                onClick={() => onExport(profile.metadata.name)}
              >
                <Download className="h-4 w-4 mr-2" />
                Export
              </Button>
            )}
            {onEdit && (
              <Button
                variant="outline"
                size="sm"
                onClick={() => onEdit(profile)}
              >
                <Cog className="h-4 w-4 mr-2" />
                Edit
              </Button>
            )}
          </div>
        </div>
      </CardHeader>

      <CardContent className="space-y-4">
        {/* Quick Stats */}
        <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4">
          <div className="text-center">
            <div className="text-2xl font-bold text-blue-600">{stats.mcpServers}</div>
            <div className="text-xs text-muted-foreground">MCP Servers</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold text-green-600">{stats.providers}</div>
            <div className="text-xs text-muted-foreground">Providers</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold text-purple-600">{stats.models}</div>
            <div className="text-xs text-muted-foreground">Models</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold text-orange-600">{stats.overrides}</div>
            <div className="text-xs text-muted-foreground">Overrides</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold text-cyan-600">{stats.tools}</div>
            <div className="text-xs text-muted-foreground">Default Tools</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold text-indigo-600">{stats.environments}</div>
            <div className="text-xs text-muted-foreground">Env Vars</div>
          </div>
        </div>

        <Separator />

        {/* MCP Servers Section */}
        {profile.mcpServers && profile.mcpServers.length > 0 && (
          <Collapsible>
            <CollapsibleTrigger
              className="flex w-full items-center justify-between py-2 hover:bg-muted/50 rounded px-2"
              onClick={() => toggleSection('mcpServers')}
            >
              <div className="flex items-center gap-2">
                <Server className="h-4 w-4" />
                <span className="font-medium">MCP Servers ({stats.mcpServers})</span>
              </div>
              {expandedSections.has('mcpServers') ? (
                <ChevronDown className="h-4 w-4" />
              ) : (
                <ChevronRight className="h-4 w-4" />
              )}
            </CollapsibleTrigger>
            <CollapsibleContent className="space-y-2 mt-2">
              {profile.mcpServers.map((server: MCPServerConfig, index: number) => (
                <Card key={index} className="border-l-4 border-l-blue-500">
                  <CardContent className="p-4">
                    <div className="flex items-start justify-between">
                      <div className="space-y-1">
                        <div className="flex items-center gap-2">
                          <h4 className="font-medium">{server.name}</h4>
                          <Badge variant={server.enabled !== false ? "default" : "secondary"}>
                            {server.enabled !== false ? "Enabled" : "Disabled"}
                          </Badge>
                        </div>
                        {server.description && (
                          <p className="text-sm text-muted-foreground">{server.description}</p>
                        )}
                        <div className="text-xs space-y-1">
                          <div>Transport: <code className="bg-muted px-1 rounded">{server.transport.type}</code></div>
                          {server.transport.command && (
                            <div>Command: <code className="bg-muted px-1 rounded">{server.transport.command}</code></div>
                          )}
                          {server.tools && server.tools.length > 0 && (
                            <div>Tools: {server.tools.length} available</div>
                          )}
                        </div>
                      </div>
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => copyToClipboard(JSON.stringify(server, null, 2))}
                      >
                        <Copy className="h-3 w-3" />
                      </Button>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </CollapsibleContent>
          </Collapsible>
        )}

        {/* Providers Section */}
        {profile.providers && profile.providers.length > 0 && (
          <Collapsible>
            <CollapsibleTrigger
              className="flex w-full items-center justify-between py-2 hover:bg-muted/50 rounded px-2"
              onClick={() => toggleSection('providers')}
            >
              <div className="flex items-center gap-2">
                <Users className="h-4 w-4" />
                <span className="font-medium">Providers ({stats.providers})</span>
              </div>
              {expandedSections.has('providers') ? (
                <ChevronDown className="h-4 w-4" />
              ) : (
                <ChevronRight className="h-4 w-4" />
              )}
            </CollapsibleTrigger>
            <CollapsibleContent className="space-y-2 mt-2">
              {profile.providers.map((provider: ProviderConfig, index: number) => (
                <Card key={index} className="border-l-4 border-l-green-500">
                  <CardContent className="p-4">
                    <div className="flex items-start justify-between">
                      <div className="space-y-1">
                        <div className="flex items-center gap-2">
                          <h4 className="font-medium">{provider.name}</h4>
                          <Badge variant="outline">{provider.type}</Badge>
                        </div>
                        <div className="text-xs space-y-1">
                          {provider.baseUrl && (
                            <div>Base URL: <code className="bg-muted px-1 rounded">{provider.baseUrl}</code></div>
                          )}
                          <div>Models: {provider.models?.length || 0} configured</div>
                          <div>API Key: {provider.apiKey ? '••••••••' : 'Not configured'}</div>
                        </div>
                      </div>
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => copyToClipboard(JSON.stringify(provider, null, 2))}
                      >
                        <Copy className="h-3 w-3" />
                      </Button>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </CollapsibleContent>
          </Collapsible>
        )}

        {/* Model Overrides Section */}
        {profile.modelOverrides && profile.modelOverrides.length > 0 && (
          <Collapsible>
            <CollapsibleTrigger
              className="flex w-full items-center justify-between py-2 hover:bg-muted/50 rounded px-2"
              onClick={() => toggleSection('overrides')}
            >
              <div className="flex items-center gap-2">
                <Cog className="h-4 w-4" />
                <span className="font-medium">Model Overrides ({stats.overrides})</span>
              </div>
              {expandedSections.has('overrides') ? (
                <ChevronDown className="h-4 w-4" />
              ) : (
                <ChevronRight className="h-4 w-4" />
              )}
            </CollapsibleTrigger>
            <CollapsibleContent className="space-y-2 mt-2">
              {profile.modelOverrides.map((override: ModelOverride, index: number) => (
                <Card key={index} className="border-l-4 border-l-orange-500">
                  <CardContent className="p-4">
                    <div className="space-y-2">
                      <div className="flex items-center gap-2">
                        <h4 className="font-medium">
                          {override.agentName || `Pattern: ${override.pattern}`}
                        </h4>
                        <Badge variant="outline">{override.model}</Badge>
                      </div>
                      {override.reason && (
                        <p className="text-sm text-muted-foreground">{override.reason}</p>
                      )}
                    </div>
                  </CardContent>
                </Card>
              ))}
            </CollapsibleContent>
          </Collapsible>
        )}

        {/* Workflow Defaults Section */}
        {profile.workflowDefaults && (
          <Collapsible>
            <CollapsibleTrigger
              className="flex w-full items-center justify-between py-2 hover:bg-muted/50 rounded px-2"
              onClick={() => toggleSection('workflow')}
            >
              <div className="flex items-center gap-2">
                <Cog className="h-4 w-4" />
                <span className="font-medium">Workflow Defaults</span>
              </div>
              {expandedSections.has('workflow') ? (
                <ChevronDown className="h-4 w-4" />
              ) : (
                <ChevronRight className="h-4 w-4" />
              )}
            </CollapsibleTrigger>
            <CollapsibleContent className="mt-2">
              <Card className="border-l-4 border-l-purple-500">
                <CardContent className="p-4 space-y-2">
                  <div className="grid grid-cols-2 gap-4 text-sm">
                    <div>Verbose: <Badge variant={profile.workflowDefaults.verbose ? "default" : "secondary"}>
                      {profile.workflowDefaults.verbose ? "Yes" : "No"}
                    </Badge></div>
                    <div>Allow Delegation: <Badge variant={profile.workflowDefaults.allowDelegation ? "default" : "secondary"}>
                      {profile.workflowDefaults.allowDelegation ? "Yes" : "No"}
                    </Badge></div>
                    <div>Max Concurrent Tasks: <code className="bg-muted px-1 rounded">
                      {profile.workflowDefaults.maxConcurrentTasks || 3}
                    </code></div>
                    <div>Timeout: <code className="bg-muted px-1 rounded">
                      {profile.workflowDefaults.timeoutMinutes || 30} min
                    </code></div>
                  </div>
                </CardContent>
              </Card>
            </CollapsibleContent>
          </Collapsible>
        )}

        {/* Security Section */}
        {profile.security && (
          <Collapsible>
            <CollapsibleTrigger
              className="flex w-full items-center justify-between py-2 hover:bg-muted/50 rounded px-2"
              onClick={() => toggleSection('security')}
            >
              <div className="flex items-center gap-2">
                <Shield className="h-4 w-4" />
                <span className="font-medium">Security Settings</span>
              </div>
              {expandedSections.has('security') ? (
                <ChevronDown className="h-4 w-4" />
              ) : (
                <ChevronRight className="h-4 w-4" />
              )}
            </CollapsibleTrigger>
            <CollapsibleContent className="mt-2">
              <Card className="border-l-4 border-l-red-500">
                <CardContent className="p-4 space-y-2">
                  <div className="text-sm space-y-2">
                    <div>
                      Allowed Domains: <code className="bg-muted px-1 rounded">
                        {profile.security.allowedDomains?.length || 0}
                      </code>
                    </div>
                    <div>
                      Restricted Tools: <code className="bg-muted px-1 rounded">
                        {profile.security.restrictedTools?.length || 0}
                      </code>
                    </div>
                    <div>
                      Rate Limits: <code className="bg-muted px-1 rounded">
                        {Object.keys(profile.security.rateLimits || {}).length}
                      </code>
                    </div>
                  </div>
                </CardContent>
              </Card>
            </CollapsibleContent>
          </Collapsible>
        )}

        {/* Created Date */}
        {profile.metadata.created && (
          <div className="text-xs text-muted-foreground text-center pt-4 border-t">
            Created: {new Date(profile.metadata.created).toLocaleString()}
          </div>
        )}
      </CardContent>
    </Card>
  );
};
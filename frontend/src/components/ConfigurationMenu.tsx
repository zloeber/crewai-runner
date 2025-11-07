import { useState, useEffect } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Badge } from "@/components/ui/badge";
import { Separator } from "@/components/ui/separator";
import { 
  Settings, 
  Server, 
  Key, 
  Check, 
  X, 
  RefreshCw, 
  Eye, 
  EyeOff,
  Save,
  RotateCcw 
} from "lucide-react";
import { crewAIApi } from "@/services/crewai-api";
import { useToast } from "@/hooks/use-toast";

interface ConnectionStatus {
  isConnected: boolean;
  lastChecked: Date | null;
  latency: number | null;
  error: string | null;
}

interface ConfigurationMenuProps {
  className?: string;
}

export function ConfigurationMenu({ className }: ConfigurationMenuProps) {
  const { toast } = useToast();
  
  // Connection status state
  const [connectionStatus, setConnectionStatus] = useState<ConnectionStatus>({
    isConnected: false,
    lastChecked: null,
    latency: null,
    error: null,
  });
  const [isTestingConnection, setIsTestingConnection] = useState(false);

  // Configuration state
  const [apiEndpoint, setApiEndpoint] = useState("");
  const [authToken, setAuthToken] = useState("");
  const [showToken, setShowToken] = useState(false);
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [isSaving, setIsSaving] = useState(false);

  // Track if configuration has changed
  const [hasChanges, setHasChanges] = useState(false);
  const [originalApiEndpoint, setOriginalApiEndpoint] = useState("");
  const [originalAuthToken, setOriginalAuthToken] = useState("");

  useEffect(() => {
    // Load current configuration on mount
    loadCurrentConfiguration();
    // Initial connection test
    testConnection();
  }, []);

  useEffect(() => {
    // Check if configuration has changed
    const endpointChanged = apiEndpoint !== originalApiEndpoint;
    const tokenChanged = authToken !== originalAuthToken;
    setHasChanges(endpointChanged || tokenChanged);
  }, [apiEndpoint, authToken, originalApiEndpoint, originalAuthToken]);

  const loadCurrentConfiguration = () => {
    // Load API endpoint (fallback to environment variable)
    const currentEndpoint = localStorage.getItem('crewai_api_endpoint') || 
                           import.meta.env.VITE_CREWAI_RUNNER_API_HOST || 
                           "http://localhost:8000";
    
    // Load auth token
    const currentToken = crewAIApi.getAuthToken() || "";
    
    setApiEndpoint(currentEndpoint);
    setAuthToken(currentToken);
    setOriginalApiEndpoint(currentEndpoint);
    setOriginalAuthToken(currentToken);
    setIsAuthenticated(crewAIApi.isAuthenticated());
  };

  const testConnection = async (customEndpoint?: string) => {
    setIsTestingConnection(true);
    const startTime = Date.now();
    const endpoint = customEndpoint || apiEndpoint;
    
    try {
      const response = await fetch(`${endpoint}/health`, {
        method: "GET",
        headers: {
          "Content-Type": "application/json",
          ...(authToken && { Authorization: `Bearer ${authToken}` }),
        },
      });

      const latency = Date.now() - startTime;

      if (response.ok) {
        setConnectionStatus({
          isConnected: true,
          lastChecked: new Date(),
          latency,
          error: null,
        });
      } else {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }
    } catch (error) {
      const errorMessage = error instanceof Error ? error.message : "Unknown error";
      
      setConnectionStatus({
        isConnected: false,
        lastChecked: new Date(),
        latency: null,
        error: errorMessage,
      });
    } finally {
      setIsTestingConnection(false);
    }
  };

  const handleSaveConfiguration = async () => {
    setIsSaving(true);
    
    try {
      // Save API endpoint to localStorage
      localStorage.setItem('crewai_api_endpoint', apiEndpoint);
      
      // Update auth token in API service
      crewAIApi.setAuthToken(authToken || null);
      
      // Update the original values to mark as saved
      setOriginalApiEndpoint(apiEndpoint);
      setOriginalAuthToken(authToken);
      setIsAuthenticated(crewAIApi.isAuthenticated());
      
      // Test the new configuration
      await testConnection();
      
      // Test authentication if token is provided
      if (authToken) {
        const authValid = await crewAIApi.testAuth();
        if (!authValid) {
          toast({
            title: "Authentication Warning",
            description: "Configuration saved, but the API token appears to be invalid",
            variant: "destructive",
          });
        }
      }
      
      toast({
        title: "Configuration Saved",
        description: "API endpoint and authentication settings have been updated",
      });
      
    } catch (error) {
      toast({
        title: "Save Failed",
        description: error instanceof Error ? error.message : "Failed to save configuration",
        variant: "destructive",
      });
    } finally {
      setIsSaving(false);
    }
  };

  const handleResetConfiguration = () => {
    setApiEndpoint(originalApiEndpoint);
    setAuthToken(originalAuthToken);
    toast({
      title: "Configuration Reset",
      description: "Changes have been discarded",
    });
  };

  const handleClearToken = () => {
    setAuthToken("");
    crewAIApi.clearAuth();
    setIsAuthenticated(false);
    toast({
      title: "Token Cleared",
      description: "Authentication token has been removed",
    });
  };

  const formatLastChecked = (date: Date | null) => {
    if (!date) return "Never";
    return date.toLocaleTimeString();
  };

  const getConnectionStatus = () => {
    if (connectionStatus.isConnected) {
      return connectionStatus.latency !== null && connectionStatus.latency > 500 
        ? "slow" 
        : "connected";
    }
    return "disconnected";
  };

  const getStatusColor = () => {
    const status = getConnectionStatus();
    switch (status) {
      case "connected":
        return "bg-green-500";
      case "slow":
        return "bg-yellow-500";
      case "disconnected":
        return "bg-red-500";
      default:
        return "bg-gray-500";
    }
  };

  const getStatusText = () => {
    const status = getConnectionStatus();
    switch (status) {
      case "connected":
        return "Connected";
      case "slow":
        return "Slow Connection";
      case "disconnected":
        return "Disconnected";
      default:
        return "Unknown";
    }
  };

  const getAuthStatusColor = () => {
    if (isAuthenticated) {
      return "bg-green-100 text-green-800 border-green-200";
    }
    return "bg-red-100 text-red-800 border-red-200";
  };

  return (
    <Card className={className}>
      <CardHeader>
        <div className="flex justify-between items-center">
          <div>
            <CardTitle className="flex items-center gap-2">
              <Settings className="h-5 w-5" />
              Configuration
            </CardTitle>
            <CardDescription>
              Manage API endpoint, authentication, and connection status
            </CardDescription>
          </div>
          <div className="flex gap-2">
            <Button
              variant="outline"
              size="sm"
              onClick={() => testConnection()}
              disabled={isTestingConnection}
            >
              <RefreshCw className={`h-4 w-4 ${isTestingConnection ? "animate-spin" : ""}`} />
              Test
            </Button>
          </div>
        </div>
      </CardHeader>
      <CardContent className="space-y-6">
        {/* Connection Status Section */}
        <div>
          <div className="flex items-center gap-2 mb-3">
            <Server className="h-4 w-4" />
            <h3 className="text-sm font-medium">Connection Status</h3>
          </div>
          <div className="space-y-3">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <div className={`w-3 h-3 rounded-full ${getStatusColor()}`}></div>
                <span className="font-medium">{getStatusText()}</span>
              </div>
              <Badge variant="outline">
                {connectionStatus.latency !== null ? `${connectionStatus.latency}ms` : "N/A"}
              </Badge>
            </div>
            
            <div className="text-sm text-muted-foreground">
              <div>Last checked: {formatLastChecked(connectionStatus.lastChecked)}</div>
              {connectionStatus.error && (
                <div className="text-red-500 mt-1">Error: {connectionStatus.error}</div>
              )}
            </div>
          </div>
        </div>

        <Separator />

        {/* API Endpoint Configuration */}
        <div>
          <div className="flex items-center gap-2 mb-3">
            <Server className="h-4 w-4" />
            <h3 className="text-sm font-medium">API Endpoint</h3>
          </div>
          <div className="space-y-2">
            <Label htmlFor="api-endpoint">Server URL</Label>
            <Input
              id="api-endpoint"
              type="url"
              placeholder="http://localhost:8000/api"
              value={apiEndpoint}
              onChange={(e) => setApiEndpoint(e.target.value)}
              disabled={isSaving}
            />
            <div className="text-xs text-muted-foreground">
              Current endpoint: {apiEndpoint || "Not configured"}
            </div>
          </div>
        </div>

        <Separator />

        {/* Authentication Configuration */}
        <div>
          <div className="flex items-center gap-2 mb-3">
            <Key className="h-4 w-4" />
            <h3 className="text-sm font-medium">Authentication</h3>
            <Badge variant="outline" className={getAuthStatusColor()}>
              <div className="flex items-center gap-1">
                {isAuthenticated ? (
                  <Check className="h-3 w-3" />
                ) : (
                  <X className="h-3 w-3" />
                )}
                {isAuthenticated ? "Authenticated" : "Not Authenticated"}
              </div>
            </Badge>
          </div>
          <div className="space-y-3">
            <div className="space-y-2">
              <Label htmlFor="auth-token">Bearer Token</Label>
              <div className="flex gap-2">
                <div className="relative flex-1">
                  <Input
                    id="auth-token"
                    type={showToken ? "text" : "password"}
                    placeholder="Enter your API token..."
                    value={authToken}
                    onChange={(e) => setAuthToken(e.target.value)}
                    disabled={isSaving}
                  />
                  <Button
                    type="button"
                    variant="ghost"
                    size="sm"
                    className="absolute right-0 top-0 h-full px-3 py-2 hover:bg-transparent"
                    onClick={() => setShowToken(!showToken)}
                    disabled={isSaving}
                  >
                    {showToken ? (
                      <EyeOff className="h-4 w-4" />
                    ) : (
                      <Eye className="h-4 w-4" />
                    )}
                  </Button>
                </div>
              </div>
            </div>
            
            {authToken && (
              <Button
                variant="outline"
                size="sm"
                onClick={handleClearToken}
                className="text-red-600 hover:text-red-700 hover:bg-red-50"
                disabled={isSaving}
              >
                Clear Token
              </Button>
            )}
          </div>
        </div>

        <Separator />

        {/* Action Buttons */}
        <div className="flex justify-between items-center">
          <div className="text-xs text-muted-foreground">
            {hasChanges ? "• Unsaved changes" : "• Configuration is up to date"}
          </div>
          <div className="flex gap-2">
            {hasChanges && (
              <Button
                variant="outline"
                size="sm"
                onClick={handleResetConfiguration}
                disabled={isSaving}
              >
                <RotateCcw className="h-4 w-4 mr-1" />
                Reset
              </Button>
            )}
            <Button
              onClick={handleSaveConfiguration}
              disabled={isSaving || !hasChanges}
            >
              <Save className="h-4 w-4 mr-1" />
              {isSaving ? "Saving..." : "Save Configuration"}
            </Button>
          </div>
        </div>

        {/* Help Text */}
        <div className="text-xs text-muted-foreground space-y-1 pt-2 border-t">
          <p>• Configuration is stored in your browser's local storage</p>
          <p>• Authentication token is used for all API requests</p>
          <p>• Test connection after changing settings to verify connectivity</p>
        </div>
      </CardContent>
    </Card>
  );
}
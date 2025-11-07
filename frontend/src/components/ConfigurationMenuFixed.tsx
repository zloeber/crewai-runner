"use client";

import { useState, useEffect } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Badge } from "@/components/ui/badge";
import { 
  Settings, 
  Server, 
  Key, 
  Check, 
  X, 
  RefreshCw, 
  Eye, 
  EyeOff,
  Save
} from "lucide-react";
import { useToast } from "@/hooks/use-toast";

interface ConnectionStatus {
  isConnected: boolean;
  lastChecked: Date | null;
  latency: number | null;
  error: string | null;
}

export function ConfigurationMenuFixed() {
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

  useEffect(() => {
    // Load current configuration on mount
    loadCurrentConfiguration();
    // Initial connection test
    testConnection();
  }, []);

  const loadCurrentConfiguration = () => {
    // Load API endpoint (fallback to environment variable)
    const currentEndpoint = localStorage.getItem('crewai_api_endpoint') || 
                           import.meta.env.VITE_CREWAI_RUNNER_API_HOST || 
                           "http://localhost:8000/api";
    
    // Load auth token
    const currentToken = localStorage.getItem('crewai_auth_token') || "";
    
    setApiEndpoint(currentEndpoint);
    setAuthToken(currentToken);
    setIsAuthenticated(!!currentToken);
  };

  const testConnection = async (customEndpoint?: string) => {
    setIsTestingConnection(true);
    const startTime = Date.now();
    const endpoint = customEndpoint || apiEndpoint;
    
    try {
      const response = await fetch(`${endpoint}/health`, {
        method: "GET",
        headers: {
          "Content-Type": "application/json"
          //...(authToken && { Authorization: `Bearer ${authToken}` }),
        },
      });

      const latency = Date.now() - startTime;

      if (response.ok) {
        const result = await response.json();
        if (result.status === "healthy") {
          setConnectionStatus({
            isConnected: true,
            lastChecked: new Date(),
            latency,
            error: null,
          });
        } else {
          throw new Error(`Health check failed: ${result.status || 'Unknown status'}`);
        }
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

  const handleSaveConfiguration = () => {
    try {
      // Save API endpoint to localStorage
      localStorage.setItem('crewai_api_endpoint', apiEndpoint);
      
      // Save auth token to localStorage
      if (authToken) {
        localStorage.setItem('crewai_auth_token', authToken);
        setIsAuthenticated(true);
      } else {
        localStorage.removeItem('crewai_auth_token');
        setIsAuthenticated(false);
      }
      
      // Test the new configuration
      testConnection();
      
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
    }
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

  return (
    <Card>
      <CardHeader>
        <div className="flex justify-between items-center">
          <div>
            <CardTitle className="flex items-center gap-2">
              <Settings className="h-5 w-5" />
              Configuration
            </CardTitle>
            <CardDescription>
              Manage API endpoint and authentication
            </CardDescription>
          </div>
          <Button
            variant="outline"
            size="sm"
            onClick={() => testConnection()}
            disabled={isTestingConnection}
          >
            <RefreshCw className={`h-4 w-4 ${isTestingConnection ? "animate-spin" : ""}`} />
          </Button>
        </div>
      </CardHeader>
      <CardContent className="space-y-4">
        {/* Connection Status */}
        <div className="space-y-2">
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

        {/* API Endpoint Configuration */}
        <div className="space-y-2">
          <Label htmlFor="api-endpoint">API Endpoint</Label>
          <Input
            id="api-endpoint"
            type="url"
            placeholder="http://localhost:8000/api"
            value={apiEndpoint}
            onChange={(e) => setApiEndpoint(e.target.value)}
          />
        </div>

        {/* Authentication Configuration */}
        <div className="space-y-2">
          <div className="flex items-center justify-between">
            <Label htmlFor="auth-token">Auth Token</Label>
            <Badge variant="outline" className={isAuthenticated ? "bg-green-100 text-green-800" : "bg-red-100 text-red-800"}>
              {isAuthenticated ? (
                <><Check className="h-3 w-3 mr-1" />Authenticated</>
              ) : (
                <><X className="h-3 w-3 mr-1" />Not Authenticated</>
              )}
            </Badge>
          </div>
          <div className="flex gap-2">
            <div className="relative flex-1">
              <Input
                id="auth-token"
                type={showToken ? "text" : "password"}
                placeholder="Enter your API token..."
                value={authToken}
                onChange={(e) => setAuthToken(e.target.value)}
              />
              <Button
                type="button"
                variant="ghost"
                size="sm"
                className="absolute right-0 top-0 h-full px-3 py-2 hover:bg-transparent"
                onClick={() => setShowToken(!showToken)}
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

        {/* Save Button */}
        <Button onClick={handleSaveConfiguration} className="w-full">
          <Save className="h-4 w-4 mr-2" />
          Save Configuration
        </Button>

        {/* Help Text */}
        <div className="text-xs text-muted-foreground space-y-1 pt-2 border-t">
          <p>• Configuration is stored in your browser's local storage</p>
          <p>• Test connection after changing settings</p>
        </div>
      </CardContent>
    </Card>
  );
}

export default ConfigurationMenuFixed;
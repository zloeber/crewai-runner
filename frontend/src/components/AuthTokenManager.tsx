import { useState, useEffect } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Badge } from "@/components/ui/badge";
import { Key, Check, X, Eye, EyeOff } from "lucide-react";
import { crewAIApi } from "@/services/crewai-api";
import { useToast } from "@/hooks/use-toast";

interface AuthTokenManagerProps {
  onAuthChange?: (isAuthenticated: boolean) => void;
}

export function AuthTokenManager({ onAuthChange }: AuthTokenManagerProps) {
  const { toast } = useToast();
  const [token, setToken] = useState("");
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [showToken, setShowToken] = useState(false);

  useEffect(() => {
    // Check if we have an existing token on mount
    const existingToken = crewAIApi.getAuthToken();
    if (existingToken) {
      setToken(existingToken);
      setIsAuthenticated(true);
      onAuthChange?.(true);
    }
  }, [onAuthChange]);

  const handleSetToken = async () => {
    if (!token.trim()) {
      toast({
        title: "Invalid Token",
        description: "Please enter a valid API token",
        variant: "destructive",
      });
      return;
    }

    setIsLoading(true);
    
    try {
      // Set the token
      crewAIApi.setAuthToken(token.trim());
      
      // Test the authentication
      const authValid = await crewAIApi.testAuth();
      
      if (authValid) {
        setIsAuthenticated(true);
        onAuthChange?.(true);
        toast({
          title: "Authentication Successful",
          description: "API token has been set and validated",
        });
      } else {
        // Clear the invalid token
        crewAIApi.clearAuth();
        setIsAuthenticated(false);
        onAuthChange?.(false);
        toast({
          title: "Authentication Failed",
          description: "The provided token is invalid",
          variant: "destructive",
        });
      }
    } catch (error) {
      crewAIApi.clearAuth();
      setIsAuthenticated(false);
      onAuthChange?.(false);
      toast({
        title: "Authentication Error",
        description: error instanceof Error ? error.message : "Failed to validate token",
        variant: "destructive",
      });
    } finally {
      setIsLoading(false);
    }
  };

  const handleClearToken = () => {
    crewAIApi.clearAuth();
    setToken("");
    setIsAuthenticated(false);
    onAuthChange?.(false);
    toast({
      title: "Token Cleared",
      description: "API token has been removed",
    });
  };

  const getStatusIcon = () => {
    if (isAuthenticated) {
      return <Check className="h-4 w-4 text-green-600" />;
    }
    return <X className="h-4 w-4 text-red-600" />;
  };

  const getStatusText = () => {
    if (isAuthenticated) {
      return "Authenticated";
    }
    return "Not Authenticated";
  };

  const getStatusColor = () => {
    if (isAuthenticated) {
      return "bg-green-100 text-green-800 border-green-200";
    }
    return "bg-red-100 text-red-800 border-red-200";
  };

  return (
    <Card>
      <CardHeader>
        <div className="flex justify-between items-center">
          <div>
            <CardTitle className="flex items-center gap-2">
              <Key className="h-5 w-5" />
              API Authentication
            </CardTitle>
            <CardDescription>
              Configure your CrewAI Runner API authentication token
            </CardDescription>
          </div>
          <Badge variant="outline" className={getStatusColor()}>
            <div className="flex items-center gap-1">
              {getStatusIcon()}
              {getStatusText()}
            </div>
          </Badge>
        </div>
      </CardHeader>
      <CardContent>
        <div className="space-y-4">
          <div className="space-y-2">
            <Label htmlFor="api-token">API Token</Label>
            <div className="flex gap-2">
              <div className="relative flex-1">
                <Input
                  id="api-token"
                  type={showToken ? "text" : "password"}
                  placeholder="Enter your API token..."
                  value={token}
                  onChange={(e) => setToken(e.target.value)}
                  onKeyDown={(e) => {
                    if (e.key === "Enter") {
                      handleSetToken();
                    }
                  }}
                  disabled={isLoading}
                />
                <Button
                  type="button"
                  variant="ghost"
                  size="sm"
                  className="absolute right-0 top-0 h-full px-3 py-2 hover:bg-transparent"
                  onClick={() => setShowToken(!showToken)}
                  disabled={isLoading}
                >
                  {showToken ? (
                    <EyeOff className="h-4 w-4" />
                  ) : (
                    <Eye className="h-4 w-4" />
                  )}
                </Button>
              </div>
              <Button
                onClick={handleSetToken}
                disabled={isLoading || !token.trim()}
              >
                {isLoading ? "Testing..." : "Set Token"}
              </Button>
            </div>
          </div>

          {isAuthenticated && (
            <div className="flex justify-between items-center p-3 bg-green-50 border border-green-200 rounded-md">
              <span className="text-sm text-green-800">
                Token is valid and ready to use
              </span>
              <Button
                variant="outline"
                size="sm"
                onClick={handleClearToken}
                className="text-red-600 hover:text-red-700 hover:bg-red-50"
              >
                Clear Token
              </Button>
            </div>
          )}

          <div className="text-xs text-muted-foreground space-y-1">
            <p>• The token will be stored in your browser's local storage</p>
            <p>• You can also set VITE_CREWAI_API_TOKEN in your environment</p>
            <p>• Leave blank if your API doesn't require authentication</p>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}
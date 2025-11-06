"use client";

import { useState, useEffect } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { RefreshCw } from "lucide-react";
import { useToast } from "@/hooks/use-toast";

interface ConnectionStatus {
  isConnected: boolean;
  lastChecked: Date | null;
  latency: number | null;
  error: string | null;
}

export function ConnectionMonitor() {
  const { toast } = useToast();
  const [status, setStatus] = useState<ConnectionStatus>({
    isConnected: false,
    lastChecked: null,
    latency: null,
    error: null,
  });
  const [isLoading, setIsLoading] = useState(false);

  const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000/api";

  const checkConnection = async () => {
    setIsLoading(true);
    const startTime = Date.now();
    
    try {
      const response = await fetch(`${API_BASE_URL}/health`, {
        method: "GET",
        headers: {
          "Content-Type": "application/json",
        },
      });

      const latency = Date.now() - startTime;

      if (response.ok) {
        setStatus({
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
      
      setStatus({
        isConnected: false,
        lastChecked: new Date(),
        latency: null,
        error: errorMessage,
      });
      
      // Only show toast for connection failures
      if (!status.isConnected) {
        toast({
          title: "Connection Error",
          description: `Failed to connect to backend: ${errorMessage}`,
          variant: "destructive",
        });
      }
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    // Initial check
    checkConnection();
    
    // Set up periodic checks every 30 seconds
    const interval = setInterval(checkConnection, 30000);
    
    return () => clearInterval(interval);
  }, []);

  const formatLastChecked = (date: Date | null) => {
    if (!date) return "Never";
    return date.toLocaleTimeString();
  };

  const getConnectionStatus = () => {
    if (status.isConnected) {
      return status.latency !== null && status.latency > 500 
        ? "slow" 
        : "connected";
    }
    return "disconnected";
  };

  const getStatusColor = () => {
    const connectionStatus = getConnectionStatus();
    switch (connectionStatus) {
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
    const connectionStatus = getConnectionStatus();
    switch (connectionStatus) {
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
            <CardTitle>Connection Status</CardTitle>
            <CardDescription>Backend API connection monitor</CardDescription>
          </div>
          <Button
            variant="outline"
            size="sm"
            onClick={checkConnection}
            disabled={isLoading}
          >
            <RefreshCw className={`h-4 w-4 ${isLoading ? "animate-spin" : ""}`} />
          </Button>
        </div>
      </CardHeader>
      <CardContent>
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <div className={`w-3 h-3 rounded-full ${getStatusColor()}`}></div>
              <span className="font-medium">{getStatusText()}</span>
            </div>
            <Badge variant="outline">
              {status.latency !== null ? `${status.latency}ms` : "N/A"}
            </Badge>
          </div>
          
          <div className="text-sm text-muted-foreground">
            <div>Last checked: {formatLastChecked(status.lastChecked)}</div>
            {status.error && (
              <div className="text-red-500 mt-1">Error: {status.error}</div>
            )}
          </div>
          
          <div className="pt-2 border-t">
            <div className="text-xs text-muted-foreground">
              <div>API Endpoint: {API_BASE_URL}</div>
              <div className="mt-1">
                {status.isConnected 
                  ? "Connection established" 
                  : "Attempting to connect..."}
              </div>
            </div>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}
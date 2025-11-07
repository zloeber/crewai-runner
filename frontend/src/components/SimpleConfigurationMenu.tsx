import { useState, useEffect, useCallback } from "react";

interface ConfigurationMenuProps {
  className?: string;
}

export function SimpleConfigurationMenu({ className }: ConfigurationMenuProps) {
  const [apiEndpoint, setApiEndpoint] = useState("");
  const [authToken, setAuthToken] = useState("");
  const [connectionStatus, setConnectionStatus] = useState("unknown");

  const testConnection = useCallback(async () => {
    try {
      setConnectionStatus("testing");
      const response = await fetch(`${apiEndpoint}/health`, {
        method: "GET",
        headers: {
          "Content-Type": "application/json",
          ...(authToken && { Authorization: `Bearer ${authToken}` }),
        },
      });

      if (response.ok) {
        try {
          const result = await response.json();
          if (result.status === "healthy") {
            setConnectionStatus("connected");
          } else {
            setConnectionStatus("error");
          }
        } catch (jsonError) {
          console.error("JSON parsing error:", jsonError);
          setConnectionStatus("error");
        }
      } else {
        console.error(`HTTP ${response.status}: ${response.statusText}`);
        setConnectionStatus("error");
      }
    } catch (networkError) {
      console.error("Network error:", networkError);
      setConnectionStatus("disconnected");
    }
  }, [apiEndpoint, authToken]);

  useEffect(() => {
    // Load current configuration
    const endpoint = localStorage.getItem('crewai_api_endpoint') || 
                     (import.meta.env.VITE_CREWAI_RUNNER_API_HOST || "http://localhost:8000");
    const token = localStorage.getItem('crewai_auth_token') || 
                  (import.meta.env.VITE_CREWAI_API_TOKEN || "");
    
    setApiEndpoint(endpoint);
    setAuthToken(token);
    
    // Test connection automatically after loading config
    setTimeout(() => {
      testConnection();
    }, 100);
  }, [testConnection]);

  const saveConfiguration = () => {
    localStorage.setItem('crewai_api_endpoint', apiEndpoint);
    localStorage.setItem('crewai_auth_token', authToken);
    alert('Configuration saved!');
  };

  return (
    <div className={`p-4 border rounded-lg space-y-4 bg-white shadow-sm ${className || ''}`}>
      <h3 className="text-lg font-semibold">Configuration Menu</h3>
      
      {/* Connection Status */}
      <div className="space-y-2">
        <label className="text-sm font-medium">Connection Status:</label>
        <div className="flex items-center gap-2">
          <div className={`w-3 h-3 rounded-full ${
            connectionStatus === 'connected' ? 'bg-green-500' : 
            connectionStatus === 'disconnected' ? 'bg-red-500' : 
            connectionStatus === 'testing' ? 'bg-yellow-500' :
            connectionStatus === 'error' ? 'bg-red-500' : 'bg-gray-500'
          }`}></div>
          <span className="text-sm capitalize">{connectionStatus}</span>
          <button 
            onClick={testConnection}
            disabled={connectionStatus === 'testing'}
            className="px-2 py-1 text-xs bg-blue-100 hover:bg-blue-200 disabled:opacity-50 disabled:cursor-not-allowed rounded"
          >
            {connectionStatus === 'testing' ? 'Testing...' : 'Test'}
          </button>
        </div>
      </div>

      {/* API Endpoint */}
      <div className="space-y-2">
        <label className="text-sm font-medium">API Endpoint:</label>
        <input
          type="url"
          value={apiEndpoint}
          onChange={(e) => setApiEndpoint(e.target.value)}
          placeholder="http://localhost:8000"
          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
        />
      </div>

      {/* Auth Token */}
      <div className="space-y-2">
        <label className="text-sm font-medium">Auth Token:</label>
        <input
          type="password"
          value={authToken}
          onChange={(e) => setAuthToken(e.target.value)}
          placeholder="Bearer token (optional)"
          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
        />
      </div>

      {/* Actions */}
      <div className="flex gap-2">
        <button
          onClick={saveConfiguration}
          className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500"
        >
          Save Configuration
        </button>
        <button
          onClick={testConnection}
          className="px-4 py-2 bg-gray-600 text-white rounded-md hover:bg-gray-700 focus:outline-none focus:ring-2 focus:ring-gray-500"
        >
          Test Connection
        </button>
      </div>

      <div className="text-xs text-gray-500 mt-2">
        Configuration is saved to localStorage and persists across sessions.
      </div>
    </div>
  );
}
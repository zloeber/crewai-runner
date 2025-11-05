"use client";

import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Separator } from "@/components/ui/separator";
import { Badge } from "@/components/ui/badge";
import { Plus, Trash2 } from "lucide-react";

interface ProviderConfigProps {}

export function ProviderConfig({}: ProviderConfigProps) {
  const [provider, setProvider] = useState("openai");
  const [apiKey, setApiKey] = useState("");
  const [customEndpoints, setCustomEndpoints] = useState([
    { id: 1, name: "Custom LLM Endpoint", url: "https://api.custom-llm.com/v1", type: "llm" },
    { id: 2, name: "Custom Embedder", url: "https://api.custom-embed.com/v1", type: "embedder" }
  ]);
  const [newEndpoint, setNewEndpoint] = useState({ name: "", url: "", type: "llm" });

  const addEndpoint = () => {
    if (newEndpoint.name && newEndpoint.url) {
      setCustomEndpoints([
        ...customEndpoints,
        { 
          id: Date.now(), 
          name: newEndpoint.name, 
          url: newEndpoint.url, 
          type: newEndpoint.type 
        }
      ]);
      setNewEndpoint({ name: "", url: "", type: "llm" });
    }
  };

  const removeEndpoint = (id: number) => {
    setCustomEndpoints(customEndpoints.filter(endpoint => endpoint.id !== id));
  };

  return (
    <div className="space-y-6">
      <div className="space-y-2">
        <Label htmlFor="provider">Default Provider</Label>
        <Select value={provider} onValueChange={setProvider}>
          <SelectTrigger id="provider">
            <SelectValue placeholder="Select a provider" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="openai">OpenAI</SelectItem>
            <SelectItem value="anthropic">Anthropic</SelectItem>
            <SelectItem value="ollama">Ollama</SelectItem>
            <SelectItem value="azure">Azure OpenAI</SelectItem>
            <SelectItem value="custom">Custom Provider</SelectItem>
          </SelectContent>
        </Select>
      </div>

      {provider === "custom" && (
        <div className="space-y-2">
          <Label htmlFor="custom-provider">Custom Provider URL</Label>
          <Input 
            id="custom-provider" 
            placeholder="https://api.your-provider.com/v1" 
          />
        </div>
      )}

      <div className="space-y-2">
        <Label htmlFor="api-key">API Key</Label>
        <Input 
          id="api-key" 
          type="password" 
          placeholder="Enter your API key" 
          value={apiKey}
          onChange={(e) => setApiKey(e.target.value)}
        />
      </div>

      <Separator />

      <div>
        <div className="flex justify-between items-center mb-3">
          <h3 className="font-medium">Custom Endpoints</h3>
          <Badge variant="secondary">{customEndpoints.length} configured</Badge>
        </div>
        
        <div className="space-y-3 mb-4">
          {customEndpoints.map((endpoint) => (
            <div key={endpoint.id} className="flex items-center justify-between p-3 bg-gray-50 rounded-md">
              <div>
                <div className="font-medium">{endpoint.name}</div>
                <div className="text-sm text-gray-500 truncate max-w-[200px]">{endpoint.url}</div>
              </div>
              <div className="flex items-center gap-2">
                <Badge variant="outline" className="text-xs">
                  {endpoint.type}
                </Badge>
                <Button 
                  variant="ghost" 
                  size="icon"
                  onClick={() => removeEndpoint(endpoint.id)}
                >
                  <Trash2 className="h-4 w-4" />
                </Button>
              </div>
            </div>
          ))}
        </div>

        <Card>
          <CardHeader>
            <CardTitle className="text-sm">Add New Endpoint</CardTitle>
          </CardHeader>
          <CardContent className="space-y-3">
            <div className="space-y-2">
              <Label htmlFor="endpoint-name">Name</Label>
              <Input 
                id="endpoint-name"
                placeholder="My Custom LLM"
                value={newEndpoint.name}
                onChange={(e) => setNewEndpoint({...newEndpoint, name: e.target.value})}
              />
            </div>
            
            <div className="space-y-2">
              <Label htmlFor="endpoint-url">URL</Label>
              <Input 
                id="endpoint-url"
                placeholder="https://api.example.com/v1"
                value={newEndpoint.url}
                onChange={(e) => setNewEndpoint({...newEndpoint, url: e.target.value})}
              />
            </div>
            
            <div className="space-y-2">
              <Label htmlFor="endpoint-type">Type</Label>
              <Select 
                value={newEndpoint.type} 
                onValueChange={(value) => setNewEndpoint({...newEndpoint, type: value})}
              >
                <SelectTrigger id="endpoint-type">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="llm">LLM Model</SelectItem>
                  <SelectItem value="embedder">Embedder</SelectItem>
                </SelectContent>
              </Select>
            </div>
            
            <Button className="w-full" onClick={addEndpoint}>
              <Plus className="mr-2 h-4 w-4" />
              Add Endpoint
            </Button>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
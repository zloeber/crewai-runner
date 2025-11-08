"use client";

import { useState, useEffect } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Separator } from "@/components/ui/separator";
import { Badge } from "@/components/ui/badge";
import { Plus, Trash2 } from "lucide-react";
import { crewAIApi } from "@/services/crewai-api";
import { ProviderConfig as ProviderConfigType, ModelConfig } from "@/types/crewai-api";
import { useToast } from "@/hooks/use-toast";

interface ProviderConfigProps {}

export function ProviderConfig({}: ProviderConfigProps) {
  const { toast } = useToast();
  const [provider, setProvider] = useState("openai");
  const [apiKey, setApiKey] = useState("");
  const [customProviders, setCustomProviders] = useState<ProviderConfigType[]>([]);
  const [models, setModels] = useState<ModelConfig[]>([]);
  const [newProvider, setNewProvider] = useState({
    name: "",
    type: "custom" as const,
    baseUrl: "",
  });
  const [newModel, setNewModel] = useState({
    name: "",
    type: "llm" as const,
    providerId: "",
    endpoint: "",
  });

  useEffect(() => {
    loadProviders();
    loadModels();
  }, []);

  const loadProviders = async () => {
    try {
      const response = await crewAIApi.listProviders();
      setCustomProviders(response.providers);
    } catch (error) {
      console.error("Failed to load providers:", error);
      // Initialize with empty array if API fails
      setCustomProviders([]);
    }
  };

  const loadModels = async () => {
    try {
      const response = await crewAIApi.listModels();
      setModels(response.models);
    } catch (error) {
      console.error("Failed to load models:", error);
      // Initialize with empty array if API fails
      setModels([]);
    }
  };

  const addProvider = async () => {
    if (!newProvider.name) {
      toast({
        title: "Validation Error",
        description: "Please enter a provider name",
        variant: "destructive",
      });
      return;
    }

    // Only require baseUrl for custom providers
    if (newProvider.type === "custom" && !newProvider.baseUrl) {
      toast({
        title: "Validation Error",
        description: "Please enter a base URL for custom providers",
        variant: "destructive",
      });
      return;
    }

    try {
      const response = await crewAIApi.addProvider({
        provider: {
          name: newProvider.name,
          type: newProvider.type,
          baseUrl: newProvider.baseUrl || undefined,
          models: [],
        },
      });

      setCustomProviders([...customProviders, response.provider]);
      setNewProvider({ name: "", type: "custom", baseUrl: "" });
      
      toast({
        title: "Success",
        description: "Provider added successfully",
      });
    } catch (error: any) {
      console.error("Failed to add provider:", error);
      toast({
        title: "Error",
        description: error.message || "Failed to add provider",
        variant: "destructive",
      });
    }
  };

  const addModel = async () => {
    if (!newModel.name) {
      toast({
        title: "Validation Error",
        description: "Please enter a model name",
        variant: "destructive",
      });
      return;
    }

    if (!newModel.providerId) {
      toast({
        title: "Validation Error",
        description: "Please select a provider",
        variant: "destructive",
      });
      return;
    }

    if (!newModel.endpoint) {
      toast({
        title: "Validation Error",
        description: "Please enter an endpoint",
        variant: "destructive",
      });
      return;
    }

    try {
      const response = await crewAIApi.addModel({
        model: {
          name: newModel.name,
          type: newModel.type,
          providerId: newModel.providerId,
          endpoint: newModel.endpoint,
        },
      });

      setModels([...models, response.model]);
      setNewModel({ name: "", type: "llm", providerId: "", endpoint: "" });
      
      toast({
        title: "Success",
        description: "Model added successfully",
      });
    } catch (error: any) {
      console.error("Failed to add model:", error);
      toast({
        title: "Error",
        description: error.message || "Failed to add model",
        variant: "destructive",
      });
    }
  };

  const removeProvider = (id: string) => {
    setCustomProviders(customProviders.filter(provider => provider.id !== id));
  };

  const removeModel = (id: string) => {
    setModels(models.filter(model => model.id !== id));
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
          <h3 className="font-medium">Custom Providers</h3>
          <Badge variant="secondary">{customProviders.length} configured</Badge>
        </div>
        
        <div className="space-y-3 mb-4">
          {customProviders.map((provider) => (
            <div key={provider.id} className="flex items-center justify-between p-3 bg-muted rounded-md">
              <div>
                <div className="font-medium">{provider.name}</div>
                <div className="text-sm text-muted-foreground truncate max-w-[200px]">{provider.baseUrl || "No URL"}</div>
              </div>
              <div className="flex items-center gap-2">
                <Badge variant="outline" className="text-xs">
                  {provider.type}
                </Badge>
                <Button 
                  variant="ghost" 
                  size="icon"
                  onClick={() => removeProvider(provider.id)}
                >
                  <Trash2 className="h-4 w-4" />
                </Button>
              </div>
            </div>
          ))}
        </div>

        <Card>
          <CardHeader>
            <CardTitle className="text-sm">Add New Provider</CardTitle>
          </CardHeader>
          <CardContent className="space-y-3">
            <div className="space-y-2">
              <Label htmlFor="provider-name">Name *</Label>
              <Input 
                id="provider-name"
                placeholder="My Custom Provider"
                value={newProvider.name}
                onChange={(e) => setNewProvider({...newProvider, name: e.target.value})}
              />
            </div>
            
            <div className="space-y-2">
              <Label htmlFor="provider-type">Type</Label>
              <Select 
                value={newProvider.type} 
                onValueChange={(value) => setNewProvider({...newProvider, type: value as "openai" | "anthropic" | "ollama" | "azure" | "custom"})}
              >
                <SelectTrigger id="provider-type">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="openai">OpenAI</SelectItem>
                  <SelectItem value="anthropic">Anthropic</SelectItem>
                  <SelectItem value="ollama">Ollama</SelectItem>
                  <SelectItem value="azure">Azure OpenAI</SelectItem>
                  <SelectItem value="custom">Custom</SelectItem>
                </SelectContent>
              </Select>
            </div>
            
            <div className="space-y-2">
              <Label htmlFor="provider-url">Base URL {newProvider.type === "custom" && "*"}</Label>
              <Input 
                id="provider-url"
                placeholder="https://api.example.com/v1"
                value={newProvider.baseUrl}
                onChange={(e) => setNewProvider({...newProvider, baseUrl: e.target.value})}
              />
            </div>
            
            <Button className="w-full" onClick={addProvider}>
              <Plus className="mr-2 h-4 w-4" />
              Add Provider
            </Button>
          </CardContent>
        </Card>
      </div>

      <Separator />

      <div>
        <div className="flex justify-between items-center mb-3">
          <h3 className="font-medium">Models</h3>
          <Badge variant="secondary">{models.length} configured</Badge>
        </div>
        
        <div className="space-y-3 mb-4">
          {models.map((model) => (
            <div key={model.id} className="flex items-center justify-between p-3 bg-muted rounded-md">
              <div>
                <div className="font-medium">{model.name}</div>
                <div className="text-sm text-muted-foreground">{model.endpoint}</div>
              </div>
              <div className="flex items-center gap-2">
                <Badge variant="outline" className="text-xs">
                  {model.type}
                </Badge>
                <Button 
                  variant="ghost" 
                  size="icon"
                  onClick={() => removeModel(model.id)}
                >
                  <Trash2 className="h-4 w-4" />
                </Button>
              </div>
            </div>
          ))}
        </div>

        <Card>
          <CardHeader>
            <CardTitle className="text-sm">Add New Model</CardTitle>
          </CardHeader>
          <CardContent className="space-y-3">
            <div className="space-y-2">
              <Label htmlFor="model-name">Name *</Label>
              <Input 
                id="model-name"
                placeholder="gpt-4-turbo"
                value={newModel.name}
                onChange={(e) => setNewModel({...newModel, name: e.target.value})}
              />
            </div>
            
            <div className="space-y-2">
              <Label htmlFor="model-provider">Provider *</Label>
              <Select 
                value={newModel.providerId} 
                onValueChange={(value) => setNewModel({...newModel, providerId: value})}
              >
                <SelectTrigger id="model-provider">
                  <SelectValue placeholder="Select a provider" />
                </SelectTrigger>
                <SelectContent>
                  {customProviders.map(provider => (
                    <SelectItem key={provider.id} value={provider.id}>
                      {provider.name}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
            
            <div className="space-y-2">
              <Label htmlFor="model-endpoint">Endpoint *</Label>
              <Input 
                id="model-endpoint"
                placeholder="/chat/completions"
                value={newModel.endpoint}
                onChange={(e) => setNewModel({...newModel, endpoint: e.target.value})}
              />
            </div>
            
            <div className="space-y-2">
              <Label htmlFor="model-type">Type</Label>
              <Select 
                value={newModel.type} 
                onValueChange={(value) => setNewModel({...newModel, type: value as "llm" | "embedder"})}
              >
                <SelectTrigger id="model-type">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="llm">LLM Model</SelectItem>
                  <SelectItem value="embedder">Embedder</SelectItem>
                </SelectContent>
              </Select>
            </div>
            
            <Button className="w-full" onClick={addModel}>
              <Plus className="mr-2 h-4 w-4" />
              Add Model
            </Button>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
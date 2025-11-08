/**
 * MCPManagement Page - Main page for managing MCP servers and tools
 */

import { useState, useEffect } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Textarea } from "@/components/ui/textarea";
import { Label } from "@/components/ui/label";
import { 
  Server, 
  Wrench, 
  Upload, 
  Download,
  Plus,
  RefreshCw,
  Loader2
} from "lucide-react";
import { ServerCard } from "@/components/mcp/ServerCard";
import { ServerConfigForm } from "@/components/mcp/ServerConfigForm";
import { ToolExplorer } from "@/components/mcp/ToolExplorer";
import { MCPServer, MCPServerConfig, MCPTool } from "@/types/mcp";
import { mcpApi } from "@/services/mcp-api";
import { useToast } from "@/hooks/use-toast";

export default function MCPManagement() {
  const { toast } = useToast();
  const [servers, setServers] = useState<MCPServer[]>([]);
  const [tools, setTools] = useState<MCPTool[]>([]);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [showAddForm, setShowAddForm] = useState(false);
  const [editingServer, setEditingServer] = useState<MCPServer | null>(null);
  const [testingServerId, setTestingServerId] = useState<string | null>(null);
  const [importConfig, setImportConfig] = useState("");
  const [activeTab, setActiveTab] = useState("servers");

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      setLoading(true);
      const [serversList, toolsList] = await Promise.all([
        mcpApi.listServers(),
        mcpApi.listAllTools(),
      ]);
      setServers(serversList);
      setTools(toolsList);
    } catch (error) {
      toast({
        title: "Failed to load data",
        description: error instanceof Error ? error.message : "Unknown error",
        variant: "destructive",
      });
    } finally {
      setLoading(false);
    }
  };

  const handleRefresh = async () => {
    setRefreshing(true);
    await loadData();
    setRefreshing(false);
  };

  const handleAddServer = async (config: MCPServerConfig) => {
    try {
      const server = await mcpApi.addServer(config);
      setServers([...servers, server]);
      setShowAddForm(false);
      toast({
        title: "Server added",
        description: `${server.name} has been added successfully`,
      });
    } catch (error) {
      toast({
        title: "Failed to add server",
        description: error instanceof Error ? error.message : "Unknown error",
        variant: "destructive",
      });
    }
  };

  const handleUpdateServer = async (config: MCPServerConfig) => {
    if (!editingServer) return;

    try {
      const updated = await mcpApi.updateServer(editingServer.id, config);
      setServers(servers.map((s) => (s.id === updated.id ? updated : s)));
      setEditingServer(null);
      toast({
        title: "Server updated",
        description: `${updated.name} has been updated successfully`,
      });
    } catch (error) {
      toast({
        title: "Failed to update server",
        description: error instanceof Error ? error.message : "Unknown error",
        variant: "destructive",
      });
    }
  };

  const handleDeleteServer = async (serverId: string) => {
    try {
      await mcpApi.deleteServer(serverId);
      setServers(servers.filter((s) => s.id !== serverId));
      toast({
        title: "Server deleted",
        description: "Server has been removed successfully",
      });
    } catch (error) {
      toast({
        title: "Failed to delete server",
        description: error instanceof Error ? error.message : "Unknown error",
        variant: "destructive",
      });
    }
  };

  const handleTestConnection = async (serverId: string) => {
    setTestingServerId(serverId);
    try {
      const status = await mcpApi.testConnection(serverId);
      
      // Update server status in list
      setServers(
        servers.map((s) =>
          s.id === serverId
            ? { ...s, status: status.status, error_message: status.message }
            : s
        )
      );

      if (status.status === "connected") {
        toast({
          title: "Connection successful",
          description: `Latency: ${status.latency_ms?.toFixed(2)}ms`,
        });
        // Refresh tools after successful connection
        await handleRefresh();
      } else {
        toast({
          title: "Connection failed",
          description: status.message,
          variant: "destructive",
        });
      }
    } catch (error) {
      toast({
        title: "Connection test failed",
        description: error instanceof Error ? error.message : "Unknown error",
        variant: "destructive",
      });
    } finally {
      setTestingServerId(null);
    }
  };

  const handleViewTools = async (serverId: string) => {
    try {
      const serverTools = await mcpApi.listServerTools(serverId);
      // Update server tools
      setServers(
        servers.map((s) =>
          s.id === serverId
            ? { ...s, tools: serverTools.map((t) => t.name) }
            : s
        )
      );
      // Switch to tools tab
      setActiveTab("tools");
      // Refresh all tools
      await handleRefresh();
    } catch (error) {
      toast({
        title: "Failed to load tools",
        description: error instanceof Error ? error.message : "Unknown error",
        variant: "destructive",
      });
    }
  };

  const handleImportConfig = async () => {
    if (!importConfig.trim()) {
      toast({
        title: "No configuration",
        description: "Please paste a configuration file",
        variant: "destructive",
      });
      return;
    }

    try {
      const result = await mcpApi.importConfig(importConfig, "claude_desktop");
      setServers([...servers, ...result.servers]);
      setImportConfig("");
      toast({
        title: "Import successful",
        description: `Imported ${result.imported_count} server(s)`,
      });
      await handleRefresh();
    } catch (error) {
      toast({
        title: "Import failed",
        description: error instanceof Error ? error.message : "Unknown error",
        variant: "destructive",
      });
    }
  };

  const handleExportConfig = async () => {
    try {
      const result = await mcpApi.exportConfig("custom");
      await navigator.clipboard.writeText(result.config_content);
      toast({
        title: "Configuration exported",
        description: "Configuration copied to clipboard",
      });
    } catch (error) {
      toast({
        title: "Export failed",
        description: error instanceof Error ? error.message : "Unknown error",
        variant: "destructive",
      });
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <Loader2 className="h-8 w-8 animate-spin" />
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-background">
      <div className="container mx-auto py-8">
        <div className="mb-8">
          <h1 className="text-4xl font-bold mb-2">MCP Server Management</h1>
          <p className="text-muted-foreground">
            Manage Model Context Protocol servers and discover available tools
          </p>
        </div>

        <Tabs value={activeTab} onValueChange={setActiveTab}>
          <div className="flex justify-between items-center mb-4">
            <TabsList>
              <TabsTrigger value="servers" className="flex items-center gap-2">
                <Server className="h-4 w-4" />
                Servers ({servers.length})
              </TabsTrigger>
              <TabsTrigger value="tools" className="flex items-center gap-2">
                <Wrench className="h-4 w-4" />
                Tools ({tools.length})
              </TabsTrigger>
              <TabsTrigger value="import" className="flex items-center gap-2">
                <Upload className="h-4 w-4" />
                Import/Export
              </TabsTrigger>
            </TabsList>

            <Button
              onClick={handleRefresh}
              disabled={refreshing}
              variant="outline"
            >
              {refreshing ? (
                <Loader2 className="h-4 w-4 animate-spin" />
              ) : (
                <RefreshCw className="h-4 w-4" />
              )}
            </Button>
          </div>

          {/* Servers Tab */}
          <TabsContent value="servers" className="space-y-4">
            {showAddForm || editingServer ? (
              <ServerConfigForm
                server={editingServer || undefined}
                onSubmit={editingServer ? handleUpdateServer : handleAddServer}
                onCancel={() => {
                  setShowAddForm(false);
                  setEditingServer(null);
                }}
              />
            ) : (
              <>
                <Button onClick={() => setShowAddForm(true)}>
                  <Plus className="mr-2 h-4 w-4" />
                  Add Server
                </Button>

                {servers.length === 0 ? (
                  <Card>
                    <CardContent className="text-center py-12">
                      <Server className="h-12 w-12 mx-auto text-muted-foreground mb-4" />
                      <h3 className="text-lg font-semibold mb-2">No servers configured</h3>
                      <p className="text-muted-foreground mb-4">
                        Add your first MCP server to get started
                      </p>
                      <Button onClick={() => setShowAddForm(true)}>
                        <Plus className="mr-2 h-4 w-4" />
                        Add Server
                      </Button>
                    </CardContent>
                  </Card>
                ) : (
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    {servers.map((server) => (
                      <ServerCard
                        key={server.id}
                        server={server}
                        onTest={handleTestConnection}
                        onDelete={handleDeleteServer}
                        onEdit={setEditingServer}
                        onViewTools={handleViewTools}
                        testing={testingServerId === server.id}
                      />
                    ))}
                  </div>
                )}
              </>
            )}
          </TabsContent>

          {/* Tools Tab */}
          <TabsContent value="tools">
            <ToolExplorer tools={tools} onRefresh={handleRefresh} />
          </TabsContent>

          {/* Import/Export Tab */}
          <TabsContent value="import" className="space-y-4">
            <Card>
              <CardHeader>
                <CardTitle>Import Configuration</CardTitle>
                <CardDescription>
                  Import MCP servers from Claude Desktop, Cline, or other MCP client configurations
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-4">
                <div>
                  <Label htmlFor="import-config">Configuration (JSON)</Label>
                  <Textarea
                    id="import-config"
                    value={importConfig}
                    onChange={(e) => setImportConfig(e.target.value)}
                    placeholder='Paste your claude_desktop_config.json or similar configuration here...'
                    className="font-mono text-sm mt-2"
                    rows={12}
                  />
                  <p className="text-xs text-muted-foreground mt-2">
                    Example: Paste contents from ~/Library/Application Support/Claude/claude_desktop_config.json
                  </p>
                </div>
                <Button onClick={handleImportConfig}>
                  <Upload className="mr-2 h-4 w-4" />
                  Import Servers
                </Button>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Export Configuration</CardTitle>
                <CardDescription>
                  Export current MCP server configuration to use in other tools
                </CardDescription>
              </CardHeader>
              <CardContent>
                <Button onClick={handleExportConfig}>
                  <Download className="mr-2 h-4 w-4" />
                  Export & Copy to Clipboard
                </Button>
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>
      </div>
    </div>
  );
}

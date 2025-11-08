/**
 * ToolExplorer Component - Browse, search, and test MCP tools
 */

import { useState, useEffect } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Textarea } from "@/components/ui/textarea";
import { Label } from "@/components/ui/label";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { 
  Search, 
  Play, 
  Copy, 
  FileCode, 
  Loader2,
  CheckCircle,
  XCircle
} from "lucide-react";
import { MCPTool, MCPToolTestResult, ExportFramework } from "@/types/mcp";
import { mcpApi } from "@/services/mcp-api";
import { useToast } from "@/hooks/use-toast";

interface ToolExplorerProps {
  tools: MCPTool[];
  onRefresh: () => void;
}

export function ToolExplorer({ tools, onRefresh }: ToolExplorerProps) {
  const { toast } = useToast();
  const [searchTerm, setSearchTerm] = useState("");
  const [selectedTool, setSelectedTool] = useState<MCPTool | null>(null);
  const [parameters, setParameters] = useState("{}");
  const [testResult, setTestResult] = useState<MCPToolTestResult | null>(null);
  const [isTesting, setIsTesting] = useState(false);
  const [exportFramework, setExportFramework] = useState<ExportFramework>("crewai");

  const filteredTools = tools.filter(
    (tool) =>
      tool.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
      tool.description?.toLowerCase().includes(searchTerm.toLowerCase()) ||
      tool.server_name.toLowerCase().includes(searchTerm.toLowerCase())
  );

  const handleToolSelect = (tool: MCPTool) => {
    setSelectedTool(tool);
    setTestResult(null);
    // Initialize parameters with example from schema
    if (tool.input_schema?.properties) {
      const example: Record<string, any> = {};
      Object.entries(tool.input_schema.properties).forEach(([key, value]: [string, any]) => {
        if (value.type === "string") example[key] = "";
        else if (value.type === "number") example[key] = 0;
        else if (value.type === "boolean") example[key] = false;
        else if (value.type === "array") example[key] = [];
        else if (value.type === "object") example[key] = {};
      });
      setParameters(JSON.stringify(example, null, 2));
    } else {
      setParameters("{}");
    }
  };

  const handleTestTool = async () => {
    if (!selectedTool) return;

    setIsTesting(true);
    setTestResult(null);

    try {
      let params: Record<string, any> = {};
      try {
        params = JSON.parse(parameters);
      } catch (e) {
        toast({
          title: "Invalid JSON",
          description: "Parameters must be valid JSON",
          variant: "destructive",
        });
        setIsTesting(false);
        return;
      }

      const result = await mcpApi.testTool(
        selectedTool.server_id,
        selectedTool.name,
        params
      );
      setTestResult(result);

      if (result.success) {
        toast({
          title: "Tool executed successfully",
          description: `Execution time: ${result.execution_time_ms.toFixed(2)}ms`,
        });
      } else {
        toast({
          title: "Tool execution failed",
          description: result.error,
          variant: "destructive",
        });
      }
    } catch (error) {
      toast({
        title: "Test failed",
        description: error instanceof Error ? error.message : "Unknown error",
        variant: "destructive",
      });
    } finally {
      setIsTesting(false);
    }
  };

  const handleExportTool = async () => {
    if (!selectedTool) return;

    try {
      const exportData = await mcpApi.exportTool(selectedTool.id, exportFramework);
      
      // Copy to clipboard
      await navigator.clipboard.writeText(exportData.tool_definition);
      
      toast({
        title: "Tool exported",
        description: `${exportFramework.toUpperCase()} definition copied to clipboard`,
      });
    } catch (error) {
      toast({
        title: "Export failed",
        description: error instanceof Error ? error.message : "Unknown error",
        variant: "destructive",
      });
    }
  };

  return (
    <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
      {/* Tool List */}
      <Card className="lg:col-span-1">
        <CardHeader>
          <CardTitle>Available Tools ({filteredTools.length})</CardTitle>
          <CardDescription>
            Browse and select tools from connected servers
          </CardDescription>
          <div className="relative">
            <Search className="absolute left-2 top-2.5 h-4 w-4 text-muted-foreground" />
            <Input
              placeholder="Search tools..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="pl-8"
            />
          </div>
        </CardHeader>
        <CardContent className="max-h-[600px] overflow-y-auto space-y-2">
          {filteredTools.length === 0 ? (
            <p className="text-sm text-muted-foreground text-center py-4">
              No tools found. Connect a server first.
            </p>
          ) : (
            filteredTools.map((tool) => (
              <div
                key={tool.id}
                className={`p-3 border rounded-lg cursor-pointer hover:bg-accent transition-colors ${
                  selectedTool?.id === tool.id ? "bg-accent border-primary" : ""
                }`}
                onClick={() => handleToolSelect(tool)}
              >
                <div className="font-medium text-sm">{tool.name}</div>
                <div className="text-xs text-muted-foreground mt-1">
                  {tool.description || "No description"}
                </div>
                <Badge variant="secondary" className="mt-2 text-xs">
                  {tool.server_name}
                </Badge>
              </div>
            ))
          )}
        </CardContent>
      </Card>

      {/* Tool Details and Testing */}
      <Card className="lg:col-span-2">
        <CardHeader>
          <CardTitle>
            {selectedTool ? selectedTool.name : "Select a tool"}
          </CardTitle>
          {selectedTool && (
            <CardDescription>
              Server: {selectedTool.server_name} | ID: {selectedTool.id}
            </CardDescription>
          )}
        </CardHeader>
        <CardContent className="space-y-4">
          {!selectedTool ? (
            <p className="text-muted-foreground text-center py-8">
              Select a tool from the list to view details and test
            </p>
          ) : (
            <>
              {/* Tool Description */}
              {selectedTool.description && (
                <div>
                  <h4 className="font-medium mb-2">Description</h4>
                  <p className="text-sm text-muted-foreground">
                    {selectedTool.description}
                  </p>
                </div>
              )}

              {/* Input Schema */}
              <div>
                <h4 className="font-medium mb-2">Input Schema</h4>
                <pre className="bg-muted p-3 rounded text-xs overflow-x-auto">
                  {JSON.stringify(selectedTool.input_schema, null, 2)}
                </pre>
              </div>

              {/* Test Tool */}
              <div>
                <Label htmlFor="parameters">Test Parameters (JSON)</Label>
                <Textarea
                  id="parameters"
                  value={parameters}
                  onChange={(e) => setParameters(e.target.value)}
                  placeholder='{"param": "value"}'
                  className="font-mono text-sm mt-2"
                  rows={6}
                />
                <Button
                  onClick={handleTestTool}
                  disabled={isTesting}
                  className="mt-2"
                >
                  {isTesting ? (
                    <>
                      <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                      Testing...
                    </>
                  ) : (
                    <>
                      <Play className="mr-2 h-4 w-4" />
                      Execute Tool
                    </>
                  )}
                </Button>
              </div>

              {/* Test Result */}
              {testResult && (
                <div>
                  <h4 className="font-medium mb-2 flex items-center gap-2">
                    Test Result
                    {testResult.success ? (
                      <CheckCircle className="h-4 w-4 text-green-500" />
                    ) : (
                      <XCircle className="h-4 w-4 text-red-500" />
                    )}
                  </h4>
                  <div className="space-y-2">
                    <div className="text-sm">
                      <span className="font-medium">Execution time:</span>{" "}
                      {testResult.execution_time_ms.toFixed(2)}ms
                    </div>
                    {testResult.error && (
                      <div className="bg-red-50 dark:bg-red-950 p-3 rounded text-sm text-red-600 dark:text-red-400">
                        {testResult.error}
                      </div>
                    )}
                    {testResult.result && (
                      <div>
                        <span className="font-medium text-sm">Result:</span>
                        <pre className="bg-muted p-3 rounded text-xs overflow-x-auto mt-2">
                          {JSON.stringify(testResult.result, null, 2)}
                        </pre>
                      </div>
                    )}
                  </div>
                </div>
              )}

              {/* Export Tool */}
              <div className="pt-4 border-t">
                <h4 className="font-medium mb-2">Export Tool Definition</h4>
                <div className="flex gap-2">
                  <Select
                    value={exportFramework}
                    onValueChange={(value) => setExportFramework(value as ExportFramework)}
                  >
                    <SelectTrigger className="w-40">
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="crewai">CrewAI</SelectItem>
                      <SelectItem value="langgraph">LangGraph</SelectItem>
                      <SelectItem value="yaml">YAML</SelectItem>
                    </SelectContent>
                  </Select>
                  <Button onClick={handleExportTool} variant="outline">
                    <FileCode className="mr-2 h-4 w-4" />
                    Export & Copy
                  </Button>
                </div>
              </div>
            </>
          )}
        </CardContent>
      </Card>
    </div>
  );
}

/**
 * ServerConfigForm Component - Form for adding/editing MCP servers
 */

import { useState, useEffect } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Switch } from "@/components/ui/switch";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { MCPServer, MCPServerConfig, TransportType } from "@/types/mcp";

interface ServerConfigFormProps {
  server?: MCPServer;
  onSubmit: (config: MCPServerConfig) => Promise<void>;
  onCancel: () => void;
}

export function ServerConfigForm({ server, onSubmit, onCancel }: ServerConfigFormProps) {
  const [name, setName] = useState(server?.name || "");
  const [description, setDescription] = useState(server?.description || "");
  const [transportType, setTransportType] = useState<TransportType>(
    server?.transport.type || "stdio"
  );
  const [command, setCommand] = useState(server?.transport.command || "");
  const [args, setArgs] = useState(server?.transport.args?.join(" ") || "");
  const [host, setHost] = useState(server?.transport.host || "");
  const [port, setPort] = useState(server?.transport.port?.toString() || "");
  const [url, setUrl] = useState(server?.transport.url || "");
  const [env, setEnv] = useState(
    server?.env ? JSON.stringify(server.env, null, 2) : "{}"
  );
  const [enabled, setEnabled] = useState(server?.enabled ?? true);
  const [isSubmitting, setIsSubmitting] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setIsSubmitting(true);

    try {
      let envObj: Record<string, string> = {};
      try {
        envObj = JSON.parse(env);
      } catch (e) {
        alert("Invalid JSON in environment variables");
        setIsSubmitting(false);
        return;
      }

      const config: MCPServerConfig = {
        name,
        description: description || undefined,
        transport: {
          type: transportType,
          ...(command && { command }),
          ...(args && { args: args.split(" ").filter(Boolean) }),
          ...(host && { host }),
          ...(port && { port: parseInt(port) }),
          ...(url && { url }),
        },
        env: envObj,
        tools: server?.tools || [],
        enabled,
      };

      await onSubmit(config);
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle>{server ? "Edit Server" : "Add New Server"}</CardTitle>
        <CardDescription>
          Configure MCP server connection parameters
        </CardDescription>
      </CardHeader>
      <CardContent>
        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="space-y-2">
            <Label htmlFor="name">Server Name *</Label>
            <Input
              id="name"
              value={name}
              onChange={(e) => setName(e.target.value)}
              placeholder="my-mcp-server"
              required
            />
          </div>

          <div className="space-y-2">
            <Label htmlFor="description">Description</Label>
            <Input
              id="description"
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              placeholder="Optional server description"
            />
          </div>

          <div className="space-y-2">
            <Label htmlFor="transport">Transport Type *</Label>
            <Select
              value={transportType}
              onValueChange={(value) => setTransportType(value as TransportType)}
            >
              <SelectTrigger>
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="stdio">stdio</SelectItem>
                <SelectItem value="http">http</SelectItem>
                <SelectItem value="websocket">websocket</SelectItem>
              </SelectContent>
            </Select>
          </div>

          {transportType === "stdio" && (
            <>
              <div className="space-y-2">
                <Label htmlFor="command">Command *</Label>
                <Input
                  id="command"
                  value={command}
                  onChange={(e) => setCommand(e.target.value)}
                  placeholder="npx"
                  required
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="args">Arguments</Label>
                <Input
                  id="args"
                  value={args}
                  onChange={(e) => setArgs(e.target.value)}
                  placeholder="-y @modelcontextprotocol/server-filesystem /path"
                />
                <p className="text-xs text-muted-foreground">
                  Space-separated arguments
                </p>
              </div>
            </>
          )}

          {(transportType === "http" || transportType === "websocket") && (
            <>
              <div className="space-y-2">
                <Label htmlFor="host">Host</Label>
                <Input
                  id="host"
                  value={host}
                  onChange={(e) => setHost(e.target.value)}
                  placeholder="localhost"
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="port">Port</Label>
                <Input
                  id="port"
                  type="number"
                  value={port}
                  onChange={(e) => setPort(e.target.value)}
                  placeholder="8080"
                />
              </div>

              <div className="space-y-2">
                <Label htmlFor="url">URL</Label>
                <Input
                  id="url"
                  value={url}
                  onChange={(e) => setUrl(e.target.value)}
                  placeholder="http://localhost:8080/mcp"
                />
              </div>
            </>
          )}

          <div className="space-y-2">
            <Label htmlFor="env">Environment Variables (JSON)</Label>
            <Textarea
              id="env"
              value={env}
              onChange={(e) => setEnv(e.target.value)}
              placeholder='{"API_KEY": "value"}'
              className="font-mono text-sm"
              rows={4}
            />
          </div>

          <div className="flex items-center space-x-2">
            <Switch
              id="enabled"
              checked={enabled}
              onCheckedChange={setEnabled}
            />
            <Label htmlFor="enabled">Enabled</Label>
          </div>

          <div className="flex gap-2">
            <Button type="submit" disabled={isSubmitting}>
              {isSubmitting ? "Saving..." : server ? "Update Server" : "Add Server"}
            </Button>
            <Button type="button" variant="outline" onClick={onCancel}>
              Cancel
            </Button>
          </div>
        </form>
      </CardContent>
    </Card>
  );
}

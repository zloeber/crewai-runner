/**
 * ServerCard Component - Displays individual MCP server with status and actions
 */

import { useState } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { 
  Server, 
  Plug, 
  Trash2, 
  Edit, 
  CheckCircle, 
  XCircle, 
  AlertCircle,
  Loader2
} from "lucide-react";
import { MCPServer } from "@/types/mcp";

interface ServerCardProps {
  server: MCPServer;
  onTest: (serverId: string) => Promise<void>;
  onDelete: (serverId: string) => Promise<void>;
  onEdit: (server: MCPServer) => void;
  onViewTools: (serverId: string) => void;
  testing?: boolean;
}

export function ServerCard({ 
  server, 
  onTest, 
  onDelete, 
  onEdit, 
  onViewTools,
  testing = false 
}: ServerCardProps) {
  const [isDeleting, setIsDeleting] = useState(false);

  const getStatusIcon = () => {
    switch (server.status) {
      case "connected":
        return <CheckCircle className="h-4 w-4 text-green-500" />;
      case "disconnected":
        return <XCircle className="h-4 w-4 text-gray-400" />;
      case "error":
        return <AlertCircle className="h-4 w-4 text-red-500" />;
    }
  };

  const getStatusBadge = () => {
    const variants: Record<typeof server.status, "default" | "destructive" | "secondary"> = {
      connected: "default",
      disconnected: "secondary",
      error: "destructive",
    };
    return (
      <Badge variant={variants[server.status]} className="ml-2">
        {server.status}
      </Badge>
    );
  };

  const handleDelete = async () => {
    if (confirm(`Are you sure you want to delete server "${server.name}"?`)) {
      setIsDeleting(true);
      try {
        await onDelete(server.id);
      } finally {
        setIsDeleting(false);
      }
    }
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Server className="h-5 w-5" />
            {server.name}
            {getStatusBadge()}
          </div>
          <div className="flex items-center gap-2">
            {getStatusIcon()}
          </div>
        </CardTitle>
        {server.description && (
          <CardDescription>{server.description}</CardDescription>
        )}
      </CardHeader>
      <CardContent className="space-y-4">
        <div className="grid grid-cols-2 gap-2 text-sm">
          <div>
            <span className="font-medium">Transport:</span> {server.transport.type}
          </div>
          {server.transport.command && (
            <div className="col-span-2">
              <span className="font-medium">Command:</span>{" "}
              <code className="bg-muted px-1 rounded">{server.transport.command}</code>
            </div>
          )}
          <div>
            <span className="font-medium">Tools:</span> {server.tools.length}
          </div>
          <div>
            <span className="font-medium">Enabled:</span>{" "}
            {server.enabled ? "Yes" : "No"}
          </div>
        </div>

        {server.error_message && (
          <div className="text-sm text-red-500 bg-red-50 dark:bg-red-950 p-2 rounded">
            <span className="font-medium">Error:</span> {server.error_message}
          </div>
        )}

        <div className="flex gap-2 flex-wrap">
          <Button
            size="sm"
            variant="outline"
            onClick={() => onTest(server.id)}
            disabled={testing}
          >
            {testing ? (
              <>
                <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                Testing...
              </>
            ) : (
              <>
                <Plug className="mr-2 h-4 w-4" />
                Test Connection
              </>
            )}
          </Button>
          <Button
            size="sm"
            variant="outline"
            onClick={() => onViewTools(server.id)}
          >
            View Tools ({server.tools.length})
          </Button>
          <Button
            size="sm"
            variant="outline"
            onClick={() => onEdit(server)}
          >
            <Edit className="mr-2 h-4 w-4" />
            Edit
          </Button>
          <Button
            size="sm"
            variant="destructive"
            onClick={handleDelete}
            disabled={isDeleting}
          >
            {isDeleting ? (
              <>
                <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                Deleting...
              </>
            ) : (
              <>
                <Trash2 className="mr-2 h-4 w-4" />
                Delete
              </>
            )}
          </Button>
        </div>
      </CardContent>
    </Card>
  );
}

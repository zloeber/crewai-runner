# CrewAI Workflow Interface API Schema

This document defines the API endpoints required for the CrewAI Workflow Interface application. These endpoints can be used to scaffold a FastAPI backend.

## Base URL
```
http://localhost:8000/api
```

## Authentication
All endpoints require an API key in the `Authorization` header:
```
Authorization: Bearer <API_KEY>
```

## Endpoints

### Providers

#### List Providers
- **URL**: `GET /providers`
- **Description**: Get all configured providers
- **Response**:
```json
{
  "providers": [
    {
      "id": "string",
      "name": "string",
      "type": "openai|anthropic|ollama|azure|custom",
      "apiKey": "string (optional)",
      "baseUrl": "string (optional)",
      "models": [
        {
          "id": "string",
          "name": "string",
          "type": "llm|embedder",
          "providerId": "string",
          "endpoint": "string",
          "default": "boolean"
        }
      ]
    }
  ]
}
```

#### Add Provider
- **URL**: `POST /providers`
- **Description**: Add a new provider
- **Request Body**:
```json
{
  "provider": {
    "name": "string",
    "type": "openai|anthropic|ollama|azure|custom",
    "apiKey": "string (optional)",
    "baseUrl": "string (optional)",
    "models": []
  }
}
```
- **Response**:
```json
{
  "provider": {
    "id": "string",
    "name": "string",
    "type": "openai|anthropic|ollama|azure|custom",
    "apiKey": "string (optional)",
    "baseUrl": "string (optional)",
    "models": []
  }
}
```

### Models

#### List Models
- **URL**: `GET /models`
- **Description**: Get all configured models
- **Response**:
```json
{
  "models": [
    {
      "id": "string",
      "name": "string",
      "type": "llm|embedder",
      "providerId": "string",
      "endpoint": "string",
      "default": "boolean"
    }
  ]
}
```

#### Add Model
- **URL**: `POST /models`
- **Description**: Add a new model
- **Request Body**:
```json
{
  "model": {
    "name": "string",
    "type": "llm|embedder",
    "providerId": "string",
    "endpoint": "string",
    "default": "boolean (optional, default: false)"
  }
}
```
- **Response**:
```json
{
  "model": {
    "id": "string",
    "name": "string",
    "type": "llm|embedder",
    "providerId": "string",
    "endpoint": "string",
    "default": "boolean"
  }
}
```

### Workflows

#### Start Workflow
- **URL**: `POST /workflows/start`
- **Description**: Start a new workflow with support for multiple frameworks
- **Request Body**:
```json
{
  "workflow": {
    "name": "string",
    "description": "string (optional)",
    "framework": "crewai|langgraph (optional, default: crewai)",
    "agents": [
      {
        "name": "string",
        "role": "string",
        "goal": "string",
        "backstory": "string",
        "model": "string",
        "tools": ["string"] (optional),
        "allowDelegation": "boolean (optional)",
        "verbose": "boolean (optional)"
      }
    ],
    "tasks": [
      {
        "name": "string",
        "description": "string",
        "expectedOutput": "string",
        "agent": "string",
        "tools": ["string"] (optional),
        "asyncExecution": "boolean (optional)",
        "context": ["string"] (optional),
        "outputJson": "boolean (optional)"
      }
    ],
    "nodes": [
      {
        "id": "string",
        "type": "string",
        "config": "object"
      }
    ] (optional, LangGraph only),
    "edges": [
      {
        "source": "string",
        "target": "string",
        "condition": "string (optional)"
      }
    ] (optional, LangGraph only)
  },
  "framework": "crewai|langgraph (optional, overrides workflow.framework)",
  "providerConfig": {
    "id": "string",
    "name": "string",
    "type": "openai|anthropic|ollama|azure|custom",
    "apiKey": "string (optional)",
    "baseUrl": "string (optional)",
    "models": []
  } (optional)
}
```
- **Response**:
```json
{
  "workflowId": "string",
  "status": "started|running|completed|failed",
  "message": "string"
}
```

#### Get Supported Frameworks
- **URL**: `GET /workflows/frameworks`
- **Description**: Get list of supported frameworks
- **Response**:
```json
{
  "frameworks": ["crewai", "langgraph"],
  "default": "crewai"
}
```

#### Stop Workflow
- **URL**: `POST /workflows/stop`
- **Description**: Stop a running workflow
- **Request Body**:
```json
{
  "workflowId": "string"
}
```
- **Response**:
```json
{
  "workflowId": "string",
  "status": "stopped|failed",
  "message": "string"
}
```

#### Get Workflow Status
- **URL**: `GET /workflows/{workflowId}/status`
- **Description**: Get the status of a workflow
- **Response**:
```json
{
  "workflowId": "string",
  "status": "idle|running|completed|failed|stopped",
  "agents": [
    {
      "name": "string",
      "status": "idle|working|completed|failed",
      "task": "string (optional)"
    }
  ],
  "currentTask": "string (optional)",
  "progress": "number (0-100)"
}
```

### Chat

#### Send Message
- **URL**: `POST /chat`
- **Description**: Send a message to a running workflow
- **Request Body**:
```json
{
  "workflowId": "string",
  "message": "string"
}
```
- **Response**:
```json
{
  "workflowId": "string",
  "response": "string",
  "timestamp": "string (ISO 8601)"
}
```

### YAML

#### Validate YAML
- **URL**: `POST /yaml/validate?framework=crewai|langgraph`
- **Description**: Validate a YAML workflow definition against a specific framework
- **Query Parameters**:
  - `framework` (optional): Framework to validate against (default: "crewai")
- **Request Body**:
```json
{
  "yamlContent": "string"
}
```
- **Response**:
```json
{
  "valid": "boolean",
  "errors": ["string"] (optional),
  "workflow": {
    "name": "string",
    "description": "string (optional)",
    "framework": "crewai|langgraph",
    "agents": [
      {
        "name": "string",
        "role": "string",
        "goal": "string",
        "backstory": "string",
        "model": "string",
        "tools": ["string"] (optional),
        "allowDelegation": "boolean (optional)",
        "verbose": "boolean (optional)"
      }
    ],
    "tasks": [
      {
        "name": "string",
        "description": "string",
        "expectedOutput": "string",
        "agent": "string",
        "tools": ["string"] (optional),
        "asyncExecution": "boolean (optional)",
        "context": ["string"] (optional),
        "outputJson": "boolean (optional)"
      }
    ]
  } (optional)
}
```

### Profiles

#### List Profiles
- **URL**: `GET /profiles`
- **Description**: Get all available profiles
- **Response**:
```json
{
  "profiles": [
    {
      "name": "string",
      "description": "string (optional)",
      "version": "string",
      "created": "string (optional)",
      "tags": ["string"]
    }
  ]
}
```

#### Load Profile
- **URL**: `POST /profiles/load`
- **Description**: Load a specific profile by name
- **Request Body**:
```json
{
  "name": "string"
}
```
- **Response**:
```json
{
  "profile": {
    "apiVersion": "string",
    "kind": "string", 
    "metadata": {
      "name": "string",
      "description": "string (optional)",
      "version": "string",
      "created": "string (optional)",
      "tags": ["string"]
    },
    "mcpServers": [
      {
        "name": "string",
        "description": "string (optional)",
        "transport": {
          "type": "stdio|http|websocket",
          "command": "string (optional)",
          "args": ["string"] (optional),
          "host": "string (optional)",
          "port": "number (optional)",
          "url": "string (optional)"
        },
        "env": {"key": "value"},
        "tools": ["string"],
        "enabled": "boolean"
      }
    ],
    "providers": [
      {
        "name": "string",
        "type": "openai|anthropic|ollama|azure|custom",
        "apiKey": "string (optional)",
        "baseUrl": "string (optional)",
        "models": [
          {
            "name": "string",
            "type": "llm|embedder",
            "endpoint": "string",
            "default": "boolean"
          }
        ]
      }
    ],
    "modelOverrides": [
      {
        "pattern": "string (optional)",
        "agentName": "string (optional)",
        "model": "string",
        "reason": "string (optional)"
      }
    ],
    "defaultToolSets": {
      "researcher": ["string"],
      "writer": ["string"],
      "analyst": ["string"]
    },
    "workflowDefaults": {
      "verbose": "boolean",
      "allowDelegation": "boolean",
      "maxConcurrentTasks": "number",
      "timeoutMinutes": "number",
      "agentDefaults": {
        "verbose": "boolean",
        "allowDelegation": "boolean",
        "model": "string (optional)",
        "tools": ["string"] (optional)
      },
      "taskDefaults": {
        "asyncExecution": "boolean",
        "outputJson": "boolean",
        "timeoutMinutes": "number (optional)"
      }
    },
    "environment": {"key": "value"},
    "security": {
      "allowedDomains": ["string"],
      "restrictedTools": ["string"],
      "rateLimits": {"key": "number"}
    }
  }
}
```

#### Save Profile
- **URL**: `POST /profiles/save`
- **Description**: Save a profile configuration
- **Request Body**:
```json
{
  "profile": {
    "apiVersion": "string",
    "kind": "string",
    "metadata": {
      "name": "string",
      "description": "string (optional)",
      "version": "string",
      "tags": ["string"]
    },
    "mcpServers": [...],
    "providers": [...],
    "modelOverrides": [...],
    "defaultToolSets": {...},
    "workflowDefaults": {...},
    "environment": {...},
    "security": {...}
  },
  "overwrite": "boolean (optional, default: false)"
}
```
- **Response**:
```json
{
  "name": "string",
  "message": "string"
}
```

#### Get Profile
- **URL**: `GET /profiles/{name}`
- **Description**: Get a specific profile by name
- **Response**: Same as Load Profile response

#### Delete Profile
- **URL**: `DELETE /profiles/{name}`
- **Description**: Delete a profile by name
- **Response**:
```json
{
  "name": "string",
  "message": "string"
}
```

#### Export Profile
- **URL**: `GET /profiles/{name}/export`
- **Description**: Export a profile as YAML content
- **Response**:
```json
{
  "name": "string",
  "yamlContent": "string"
}
```

#### Import Profile
- **URL**: `POST /profiles/import`
- **Description**: Import a profile from YAML content
- **Request Body**:
```json
{
  "yamlContent": "string",
  "overwrite": "boolean (optional, default: false)"
}
```
- **Response**:
```json
{
  "name": "string",
  "message": "string"
}
```

### MCP (Model Context Protocol)

#### List MCP Servers
- **URL**: `GET /mcp/servers`
- **Description**: List all registered MCP servers
- **Response**:
```json
{
  "servers": [
    {
      "id": "string",
      "name": "string",
      "description": "string (optional)",
      "transport": {
        "type": "stdio|http|websocket",
        "command": "string (optional)",
        "args": ["string"] (optional),
        "host": "string (optional)",
        "port": "number (optional)",
        "url": "string (optional)"
      },
      "env": {"key": "value"},
      "tools": ["string"],
      "enabled": "boolean",
      "status": "connected|disconnected|error",
      "error_message": "string (optional)"
    }
  ]
}
```

#### Add MCP Server
- **URL**: `POST /mcp/servers`
- **Description**: Register a new MCP server
- **Request Body**:
```json
{
  "server": {
    "name": "string",
    "description": "string (optional)",
    "transport": {
      "type": "stdio|http|websocket",
      "command": "string (optional)",
      "args": ["string"] (optional),
      "host": "string (optional)",
      "port": "number (optional)",
      "url": "string (optional)"
    },
    "env": {"key": "value"},
    "tools": ["string"],
    "enabled": "boolean"
  }
}
```
- **Response**:
```json
{
  "server": {
    "id": "string",
    "name": "string",
    "description": "string (optional)",
    "transport": {...},
    "env": {...},
    "tools": [...],
    "enabled": "boolean",
    "status": "connected|disconnected|error"
  }
}
```

#### Update MCP Server
- **URL**: `PUT /mcp/servers/{id}`
- **Description**: Update an existing MCP server configuration
- **Request Body**: Same as Add MCP Server
- **Response**: Same as Add MCP Server

#### Delete MCP Server
- **URL**: `DELETE /mcp/servers/{id}`
- **Description**: Remove an MCP server
- **Response**:
```json
{
  "id": "string",
  "message": "string"
}
```

#### Test MCP Connection
- **URL**: `POST /mcp/servers/{id}/connect`
- **Description**: Test connection to an MCP server
- **Response**:
```json
{
  "server_id": "string",
  "connection_status": {
    "status": "connected|disconnected|error",
    "message": "string",
    "latency_ms": "number (optional)",
    "transport_type": "string",
    "initialization_success": "boolean"
  }
}
```

#### Get MCP Server Status
- **URL**: `GET /mcp/servers/{id}/status`
- **Description**: Get current connection status of an MCP server
- **Response**:
```json
{
  "status": "connected|disconnected|error",
  "message": "string",
  "latency_ms": "number (optional)",
  "transport_type": "string",
  "initialization_success": "boolean"
}
```

#### List Server Tools
- **URL**: `GET /mcp/servers/{id}/tools`
- **Description**: List all tools provided by a specific MCP server
- **Response**:
```json
{
  "tools": [
    {
      "id": "string",
      "server_id": "string",
      "server_name": "string",
      "name": "string",
      "description": "string (optional)",
      "input_schema": {...},
      "output_schema": {...} (optional)
    }
  ]
}
```

#### List All Tools
- **URL**: `GET /mcp/tools`
- **Description**: List all tools from all connected MCP servers
- **Response**: Same as List Server Tools

#### Test MCP Tool
- **URL**: `POST /mcp/tools/test`
- **Description**: Execute a tool for testing purposes
- **Request Body**:
```json
{
  "server_id": "string",
  "tool_name": "string",
  "parameters": {...}
}
```
- **Response**:
```json
{
  "tool_name": "string",
  "success": "boolean",
  "result": "any (optional)",
  "error": "string (optional)",
  "execution_time_ms": "number",
  "request": {...},
  "response": {...}
}
```

#### Get Tool Schema
- **URL**: `GET /mcp/tools/{tool_id}/schema`
- **Description**: Get detailed schema for a specific tool (tool_id format: "server_id:tool_name")
- **Response**:
```json
{
  "tool_id": "string",
  "name": "string",
  "description": "string (optional)",
  "input_schema": {...},
  "output_schema": {...} (optional)
}
```

#### Import MCP Configuration
- **URL**: `POST /mcp/import/config`
- **Description**: Import MCP servers from configuration file (Claude Desktop, Cline, etc.)
- **Request Body**:
```json
{
  "config_content": "string (JSON content)",
  "config_format": "claude_desktop|cline|custom"
}
```
- **Response**:
```json
{
  "imported_count": "number",
  "servers": [...],
  "message": "string"
}
```

#### Export MCP Configuration
- **URL**: `GET /mcp/export/config?format=custom`
- **Description**: Export current MCP server configuration
- **Query Parameters**:
  - `format` (optional): Export format (default: "custom")
- **Response**:
```json
{
  "config_content": "string",
  "format": "string"
}
```

#### Export Tool Definition
- **URL**: `POST /mcp/tools/{tool_id}/export`
- **Description**: Export tool definition in framework-specific format
- **Request Body**:
```json
{
  "framework": "crewai|langgraph|yaml"
}
```
- **Response**:
```json
{
  "tool_definition": "string",
  "framework": "string",
  "instructions": "string (optional)"
}
```

## Error Responses
All endpoints may return the following error responses:

- **400 Bad Request**: Invalid request data
- **401 Unauthorized**: Missing or invalid API key
- **404 Not Found**: Resource not found
- **500 Internal Server Error**: Server error

Error response format:
```json
{
  "error": "string",
  "message": "string"
}
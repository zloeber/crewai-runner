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
- **Description**: Start a new workflow
- **Request Body**:
```json
{
  "workflow": {
    "name": "string",
    "description": "string (optional)",
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
  },
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
- **URL**: `POST /yaml/validate`
- **Description**: Validate a YAML workflow definition
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
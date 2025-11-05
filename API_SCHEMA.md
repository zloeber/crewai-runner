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
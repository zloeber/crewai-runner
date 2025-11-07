# CrewAI Profile Configuration System

## Overview

The CrewAI Profile Configuration system allows you to define and manage high-level configurations that can be applied to workflows. Profiles contain:

- **MCP Server Definitions**: Configure Model Context Protocol servers with their transport, environment, and tools
- **Model Provider Configurations**: Define AI model providers and their available models
- **Model Override Rules**: Automatically apply specific models to agents based on patterns or names
- **Default Tool Sets**: Pre-defined tool combinations for common agent roles
- **Workflow Defaults**: Standard configurations for workflow execution
- **Environment Variables**: Shared environment configuration
- **Security Settings**: Access controls and rate limits

## API Endpoints

The profile system provides a complete REST API for managing profiles:

### List Profiles
```http
GET /api/profiles
```
Returns all available profiles with their metadata.

### Load Profile
```http
POST /api/profiles/load
Content-Type: application/json

{
  "name": "default"
}
```

### Save Profile
```http
POST /api/profiles/save
Content-Type: application/json

{
  "profile": { ... },
  "overwrite": false
}
```

### Get Profile
```http
GET /api/profiles/{name}
```

### Delete Profile
```http
DELETE /api/profiles/{name}
```

### Export Profile as YAML
```http
GET /api/profiles/{name}/export
```

### Import Profile from YAML
```http
POST /api/profiles/import
Content-Type: application/json

{
  "yamlContent": "...",
  "overwrite": false
}
```

## Profile YAML Structure

```yaml
apiVersion: crewai/v1
kind: Profile
metadata:
  name: profile-name
  description: Profile description
  version: "1.0.0"
  created: "2024-11-07T00:00:00Z"
  tags: ["tag1", "tag2"]

# MCP Server configurations
mcpServers:
  - name: searxng
    description: Web search and content retrieval
    transport:
      type: stdio
      command: "uvx"
      args: ["mcp-server-searxng"]
    env:
      SEARXNG_BASE_URL: "https://search.inetol.net"
    tools:
      - mcp_searxng_searxng_web_search
      - mcp_searxng_web_url_read

# Model provider configurations
providers:
  - name: openai
    type: openai
    apiKey: "${OPENAI_API_KEY}"
    models:
      - name: gpt-4o
        type: llm
        providerId: openai
        endpoint: "gpt-4o"
        default: true

# Model override rules
modelOverrides:
  - pattern: "*researcher*"
    model: gpt-4o
    reason: "Research agents benefit from GPT-4's capabilities"
  
  - agentName: "specific_agent"
    model: claude-3-5-sonnet-20241022
    reason: "This agent works better with Claude"

# Default tool sets for common roles
defaultToolSets:
  researcher:
    - mcp_searxng_searxng_web_search
    - mcp_searxng_web_url_read
  writer:
    - mcp_server-filesy_write_file
    - mcp_sequential-th_sequentialthinking

# Workflow-level defaults
workflowDefaults:
  verbose: true
  allowDelegation: false
  maxConcurrentTasks: 3
  timeoutMinutes: 30
  agentDefaults:
    verbose: true
    allowDelegation: false
  taskDefaults:
    asyncExecution: false
    outputJson: false

# Environment variables
environment:
  OPENAI_API_KEY: "${OPENAI_API_KEY}"
  ANTHROPIC_API_KEY: "${ANTHROPIC_API_KEY}"

# Security settings
security:
  allowedDomains:
    - "*.openai.com"
    - "*.anthropic.com"
  restrictedTools: []
  rateLimits:
    requestsPerMinute: 60
    tokensPerMinute: 100000
```

## Usage Examples

### Creating a Research Profile

```yaml
apiVersion: crewai/v1
kind: Profile
metadata:
  name: research
  description: Optimized for research workflows
  version: "1.0.0"
  tags: ["research", "analysis"]

mcpServers:
  - name: searxng
    description: Web search
    transport:
      type: stdio
      command: "uvx"
      args: ["mcp-server-searxng"]
    tools:
      - mcp_searxng_searxng_web_search
      - mcp_searxng_web_url_read

providers:
  - name: openai
    type: openai
    apiKey: "${OPENAI_API_KEY}"
    models:
      - name: gpt-4o
        type: llm
        providerId: openai
        endpoint: "gpt-4o"
        default: true

modelOverrides:
  - pattern: "*"
    model: gpt-4o
    reason: "Research benefits from GPT-4's capabilities"

defaultToolSets:
  researcher:
    - mcp_searxng_searxng_web_search
    - mcp_searxng_web_url_read
```

### Creating a Writing Profile

```yaml
apiVersion: crewai/v1
kind: Profile
metadata:
  name: writing
  description: Optimized for content creation
  version: "1.0.0"
  tags: ["writing", "content"]

mcpServers:
  - name: filesy
    description: File operations
    transport:
      type: stdio
      command: "npx"
      args: ["-y", "@dyad-ai/mcp-server-filesy"]
    tools:
      - mcp_server-filesy_write_file
      - mcp_server-filesy_create_directory

providers:
  - name: anthropic
    type: anthropic
    apiKey: "${ANTHROPIC_API_KEY}"
    models:
      - name: claude-3-5-sonnet-20241022
        type: llm
        providerId: anthropic
        endpoint: "claude-3-5-sonnet-20241022"
        default: true

modelOverrides:
  - pattern: "*writer*"
    model: claude-3-5-sonnet-20241022
    reason: "Claude excels at creative writing"

defaultToolSets:
  writer:
    - mcp_server-filesy_write_file
    - mcp_server-filesy_create_directory
```

## Implementation Details

### File Structure
```
api/
├── src/engine/
│   ├── models.py          # Pydantic models for profiles
│   ├── routers/
│   │   └── profiles.py    # FastAPI router for profile endpoints
│   └── main.py           # Main FastAPI app (includes profiles router)
├── profiles/             # Profile storage directory
│   └── default.yaml      # Default profile
└── test_profiles.py      # API test script
```

### Key Components

1. **ProfileConfig Model**: Main Pydantic model that validates the entire profile structure
2. **MCPServerConfig Model**: Defines MCP server configuration including transport and tools
3. **ModelOverride Model**: Rules for automatically applying models to agents
4. **Profile Router**: FastAPI router with endpoints for CRUD operations
5. **Profile Storage**: YAML files stored in the `profiles/` directory

### Security Features

- API key authentication required for all endpoints
- Configurable domain allowlists
- Tool restriction capabilities
- Rate limiting configuration
- Environment variable templating with `${VAR}` syntax

### Testing

The implementation includes comprehensive testing:

- Model validation tests
- YAML loading/parsing tests
- API endpoint tests
- Profile import/export tests

### Future Enhancements

Potential future improvements:
- Profile inheritance (profiles extending other profiles)
- Profile versioning and migration
- Git-based profile storage
- Profile validation rules
- Template profiles for common use cases
- Integration with workflow execution to automatically apply profile settings

## Example Profile

See `examples/profile.default.yaml` for a complete example profile that demonstrates all features of the profile system.
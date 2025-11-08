# CrewAI Profile Schema and Components

This document describes the comprehensive profile management system for CrewAI, including common schemas, validation utilities, and React components.

## Overview

The profile system provides a standardized way to configure and manage CrewAI deployments including:

- **MCP Server configurations** - Define which MCP servers are available to workflows
- **Provider configurations** - Configure AI providers (OpenAI, Anthropic, Ollama, etc.)
- **Model overrides** - Override default models for specific agents or patterns
- **Workflow defaults** - Set default behavior for workflows, agents, and tasks
- **Security settings** - Define security constraints and permissions
- **Environment variables** - Configure environment-specific settings

## Directory Structure

```
schemas/
├── profile.schema.json      # JSON Schema for validation
├── profile.types.ts         # TypeScript type definitions
├── profile.validator.ts     # Validation utilities
├── profile.manager.ts       # Profile management client
└── index.ts                 # Exports and utilities

frontend/src/
├── components/
│   ├── ProfileDisplay.tsx   # Component to display profile information
│   └── ProfileSelector.tsx  # Component to select and load profiles
├── hooks/
│   └── use-profiles.ts      # React hook for profile management
└── types/
    └── crewai-api.ts        # API types (includes profile types)
```

## Schema Structure

### Profile Configuration

A profile configuration follows this structure:

```yaml
apiVersion: crewai/v1
kind: Profile
metadata:
  name: profile-name
  description: "Profile description"
  version: "1.0.0"
  created: "2024-11-07T00:00:00Z"
  tags:
    - production
    - default

mcpServers:
  - name: searxng
    description: "Web search capabilities"
    transport:
      type: stdio
      command: "uvx"
      args: ["mcp-server-searxng"]
    env:
      SEARXNG_BASE_URL: "https://search.example.com"
    tools:
      - mcp_searxng_searxng_web_search
      - mcp_searxng_web_url_read
    enabled: true

providers:
  - name: openai
    type: openai
    apiKey: "sk-..."
    models:
      - name: gpt-4
        type: llm
        endpoint: "/v1/chat/completions"
        default: true

modelOverrides:
  - pattern: "researcher.*"
    model: "gpt-4"
    reason: "Researchers need high-quality reasoning"

workflowDefaults:
  verbose: true
  allowDelegation: false
  maxConcurrentTasks: 3
  timeoutMinutes: 30
  agentDefaults:
    verbose: true
    allowDelegation: false
    tools: []
  taskDefaults:
    asyncExecution: false
    outputJson: false

environment:
  NODE_ENV: "production"
  LOG_LEVEL: "info"

security:
  allowedDomains:
    - "api.openai.com"
    - "api.anthropic.com"
  restrictedTools: []
  rateLimits:
    requests_per_minute: 60
```

## TypeScript Types

All profile types are available in `frontend/src/types/crewai-api.ts`:

```typescript
import type { 
  ProfileConfig, 
  ProfileMetadata,
  MCPServerConfig,
  ProviderConfig,
  ModelOverride,
  WorkflowDefaults 
} from '../types/crewai-api';
```

## Validation

### JSON Schema Validation

The `profile.schema.json` file provides comprehensive JSON Schema validation for profile configurations. Use it with JSON Schema validators to ensure profile validity.

### TypeScript Validation

The `ProfileValidator` class provides client-side validation:

```typescript
import { ProfileValidator } from './schemas/profile.validator';

const validation = ProfileValidator.validateProfile(profileConfig);
if (!validation.isValid) {
  console.error('Validation errors:', validation.errors);
}
```

### Validation Features

- **Required field validation** - Ensures all required fields are present
- **Format validation** - Validates profile names, versions, URLs, etc.
- **Type validation** - Ensures correct data types
- **Cross-reference validation** - Validates relationships between fields
- **Security validation** - Checks security settings for consistency

## Profile Management

### Server-side Management

Use the `ProfileManager` class for server-side profile operations:

```typescript
import { ProfileManager } from './schemas/profile.manager';

const manager = new ProfileManager('http://localhost:8000', 'your-api-token');

// List profiles
const profiles = await manager.listProfiles();

// Load a profile
const profile = await manager.loadProfile('default');

// Save a profile
await manager.saveProfile(profileConfig, false);

// Export/Import
const exported = await manager.exportProfile('default');
await manager.importProfile(yamlContent, false);
```

### React Components

#### ProfileSelector

A component for selecting and loading profiles:

```tsx
import { ProfileSelector } from '../components/ProfileSelector';

<ProfileSelector
  onProfileSelected={(profile) => console.log('Profile loaded:', profile)}
  onManageProfiles={() => console.log('Manage profiles')}
/>
```

#### ProfileDisplay

A component for displaying detailed profile information:

```tsx
import { ProfileDisplay } from '../components/ProfileDisplay';

<ProfileDisplay
  profile={currentProfile}
  onExport={(name) => console.log('Export profile:', name)}
  onEdit={(profile) => console.log('Edit profile:', profile)}
/>
```

### React Hook

Use the `useProfiles` hook for profile state management:

```tsx
import { useProfiles } from '../hooks/use-profiles';

function MyComponent() {
  const {
    profiles,
    currentProfile,
    loading,
    error,
    loadProfile,
    saveProfile,
    deleteProfile
  } = useProfiles();

  // Component logic here
}
```

## API Endpoints

The profile system integrates with the following API endpoints:

- `GET /api/profiles` - List all profiles
- `POST /api/profiles/load` - Load a specific profile
- `GET /api/profiles/{name}` - Get a profile by name
- `POST /api/profiles/save` - Save a profile
- `DELETE /api/profiles/{name}` - Delete a profile
- `GET /api/profiles/{name}/export` - Export profile as YAML
- `POST /api/profiles/import` - Import profile from YAML

## Usage Examples

### Creating a New Profile

```typescript
const newProfile: ProfileConfig = {
  apiVersion: 'crewai/v1',
  kind: 'Profile',
  metadata: {
    name: 'my-profile',
    description: 'My custom profile',
    version: '1.0.0',
    tags: ['custom']
  },
  mcpServers: [],
  providers: [],
  modelOverrides: [],
  workflowDefaults: {
    verbose: true,
    allowDelegation: false,
    maxConcurrentTasks: 3,
    timeoutMinutes: 30
  }
};

await saveProfile(newProfile);
```

### Loading and Using a Profile

```typescript
// Load profile
await loadProfile('default');

// Access profile data
if (currentProfile) {
  console.log('Profile name:', currentProfile.metadata.name);
  console.log('MCP servers:', currentProfile.mcpServers?.length);
  console.log('Providers:', currentProfile.providers?.length);
}
```

### Exporting a Profile

```typescript
const exported = await exportProfile('default');
console.log('YAML content:', exported.yamlContent);

// Save to file
const blob = new Blob([exported.yamlContent], { type: 'text/yaml' });
const url = URL.createObjectURL(blob);
const a = document.createElement('a');
a.href = url;
a.download = `${exported.name}.yaml`;
a.click();
```

## Best Practices

1. **Profile Naming** - Use lowercase, alphanumeric characters with hyphens
2. **Versioning** - Follow semantic versioning (major.minor.patch)
3. **Descriptions** - Always provide meaningful descriptions
4. **Tags** - Use tags to categorize profiles (e.g., 'production', 'development')
5. **Validation** - Always validate profiles before saving
6. **Security** - Be careful with API keys and sensitive data
7. **Environment Variables** - Use environment variables for deployment-specific settings

## Error Handling

The system provides comprehensive error handling:

- **Validation errors** - Detailed field-level validation errors
- **API errors** - HTTP status codes and error messages
- **Network errors** - Connection and timeout handling
- **Authentication errors** - Token validation and refresh

## Security Considerations

- API keys are masked in UI displays
- Sensitive environment variables should be handled carefully
- Profile imports/exports should be validated
- Access control should be implemented at the API level
- Rate limiting should be configured appropriately
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
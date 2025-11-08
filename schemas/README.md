# CrewAI Profile Schema Library

This directory contains the comprehensive schema definition and utilities for CrewAI profile management.

## Files

- **`profile.schema.json`** - JSON Schema definition for profile validation
- **`profile.types.ts`** - TypeScript type definitions 
- **`profile.validator.ts`** - Client-side validation utilities
- **`profile.manager.ts`** - Profile management API client
- **`index.ts`** - Main exports and utility functions

## Quick Start

### TypeScript/JavaScript Usage

```typescript
// Import everything
import { ProfileManager, ProfileValidator, ProfileConfig } from './schemas';

// Create a profile manager
const manager = new ProfileManager('http://localhost:8000', 'your-api-token');

// List available profiles
const profiles = await manager.listProfiles();

// Load a specific profile
const profile = await manager.loadProfile('default');

// Validate a profile
const validation = ProfileValidator.validateProfile(profile);
if (!validation.isValid) {
  console.error('Validation errors:', validation.errors);
}
```

### React Usage

```tsx
import { ProfileSelector, ProfileDisplay } from '../components';
import { useProfiles } from '../hooks/use-profiles';

function MyComponent() {
  const { currentProfile } = useProfiles();
  
  return (
    <div>
      <ProfileSelector />
      <ProfileDisplay profile={currentProfile} />
    </div>
  );
}
```

## Schema Structure

### Basic Profile

```yaml
apiVersion: crewai/v1
kind: Profile
metadata:
  name: my-profile
  description: "Profile description"
  version: "1.0.0"
  tags: ["production"]
```

### With MCP Servers

```yaml
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
    enabled: true
```

### With Providers

```yaml
providers:
  - name: openai
    type: openai
    apiKey: "${OPENAI_API_KEY}"
    models:
      - name: gpt-4
        type: llm
        endpoint: "/v1/chat/completions"
        default: true
```

## Validation Rules

### Profile Names
- Must be lowercase
- Alphanumeric characters and hyphens only
- Pattern: `^[a-z0-9-]+$`

### Versions
- Must follow semantic versioning
- Pattern: `^\d+\.\d+\.\d+$`
- Example: `1.0.0`, `2.1.3`

### Required Fields
- `apiVersion`: Must be `"crewai/v1"`
- `kind`: Must be `"Profile"`
- `metadata.name`: Required string
- `metadata.version`: Required semantic version

### MCP Servers
- `name`: Required, unique within profile
- `transport.type`: Must be one of `stdio`, `http`, `websocket`
- For `stdio`: `command` is required
- For `http`/`websocket`: Either `url` or `host`+`port` required

### Providers
- `name`: Required, unique within profile
- `type`: Must be one of `openai`, `anthropic`, `ollama`, `azure`, `custom`

## Error Handling

The validation system provides detailed error information:

```typescript
interface ProfileValidationError {
  path: string;        // e.g., "metadata.name", "mcpServers[0].transport.command"
  message: string;     // Human-readable error message
  code: string;        // Error type code
}
```

### Error Codes
- `REQUIRED_FIELD` - Missing required field
- `INVALID_VALUE` - Value doesn't match allowed options
- `INVALID_FORMAT` - Format validation failed (regex, etc.)
- `DUPLICATE_VALUE` - Duplicate value where uniqueness required
- `MISSING_REQUIRED_COMBINATION` - Missing required field combination

## Frontend Integration

### Components

- **ProfileSelector** - Dropdown for selecting profiles
- **ProfileDisplay** - Rich display of profile information

### Hooks

- **useProfiles** - State management for profiles

### Services

- Profile methods added to `crewAIApi` service

## API Integration

All schema types align with the REST API endpoints:

- `GET /api/profiles` → `ProfileListResponse`
- `POST /api/profiles/load` → `LoadProfileRequest/Response`
- `POST /api/profiles/save` → `SaveProfileRequest/Response`
- `DELETE /api/profiles/{name}` → `DeleteProfileResponse`
- `GET /api/profiles/{name}/export` → `ExportProfileResponse`
- `POST /api/profiles/import` → `ImportProfileRequest/Response`

## Development

### Adding New Fields

1. Update `profile.schema.json`
2. Update TypeScript types in `profile.types.ts`
3. Add validation rules to `profile.validator.ts`
4. Update frontend components if needed
5. Update documentation

### Testing

```bash
# Validate schema files
npm run validate-schemas

# Run TypeScript compilation
npm run type-check

# Test validation
npm run test-validation
```

## Examples

See the `/examples` directory for complete profile examples:

- `profile.default.yaml` - Basic profile with common MCP servers
- Profile configurations for different environments and use cases

For more detailed documentation, see `/docs/profiles.md`.
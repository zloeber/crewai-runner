I need to add MCP (Model Context Protocol) server management capabilities to my React + FastAPI application that's used for testing AI orchestration frameworks (CrewAI, LangGraph, etc.).

## Current Context
- Monorepo with FastAPI backend and React frontend
- Already integrates MCP servers as tools in orchestration workflows
- Uses YAML for configuration import/export

## Feature Requirements

### MCP Server Management Page/Component

**1. Server Registry & Configuration**
- List all registered MCP servers with status (connected/disconnected/error)
- Add new MCP servers via:
  - Manual form (name, connection type: stdio/sse/http, command/URL, args, env vars)
  - Import from MCP config files (JSON format from Claude Desktop, Cline, etc.)
  - Example: Import from `~/Library/Application Support/Claude/claude_desktop_config.json`
- Edit/delete existing server configurations
- Persist server configs (database or config file)

**2. Server Connection Testing**
- "Test Connection" button for each server
- Display connection status with clear success/error messages
- Show connection diagnostics (latency, transport type, initialization success)
- Real-time connection status indicators

**3. Tool Discovery & Inspection**
- Auto-discover and list all tools provided by each connected server
- Display for each tool:
  - Tool name and description
  - Input schema (parameters, types, required fields)
  - Output schema/format
  - Usage examples
- Search/filter tools across all servers

**4. Tool Testing Interface**
- Interactive tool testing panel
- Select server → select tool → fill parameters → execute
- Display:
  - Raw JSON request/response
  - Formatted output
  - Execution time
  - Error messages with stack traces
- Save test cases for repeated testing

**5. Tool Export for Orchestrations**
- "Add to Orchestration" button for each tool
- Export tool definitions in framework-specific formats:
  - CrewAI Tool format
  - LangGraph tool binding format
  - Generic YAML for custom workflows
- Copy tool reference strings (e.g., "filesystem.read_file")

## Technical Requirements

### Backend (FastAPI)

**Endpoints needed:**
#### Server management
GET    /mcp/servers              # List all registered servers
POST   /mcp/servers              # Register new server
PUT    /mcp/servers/{id}         # Update server config
DELETE /mcp/servers/{id}         # Remove server
POST   /mcp/servers/{id}/connect # Test connection
GET    /mcp/servers/{id}/status  # Get current status

#### Tool operations
GET    /mcp/servers/{id}/tools   # List tools from server
GET    /mcp/tools                # List all tools from all servers
POST   /mcp/tools/test           # Execute tool for testing
GET    /mcp/tools/{tool_id}/schema # Get detailed tool schema

#### Import/Export
POST   /mcp/import/config        # Import from Claude/Cline config
GET    /mcp/export/config        # Export current MCP configuration
POST   /mcp/tools/{tool_id}/export # Export tool definition for framework

**Backend implementation needs:**
- MCPServerManager class to handle server lifecycle
- Connection pooling/caching for active MCP clients
- Tool schema introspection
- Config file parsers for different MCP client formats (Claude Desktop, Cline, etc.)
- Framework-specific tool exporters (CrewAI, LangGraph adapters)

### Frontend (React)

**Component structure:**
```
<MCPManagementPage>
  <ServerList>
    <ServerCard status={status} onTest={...} onDelete={...} />
  </ServerList>
<ServerConfigForm 
 onSubmit={...} 
 onImportConfig={...} 
/>
  <ToolExplorer>
    <ToolList servers={servers} />
    <ToolDetails tool={selectedTool} />
    <ToolTester 
      tool={selectedTool}
      onExecute={...}
      results={...}
    />
  </ToolExplorer>
<ToolExportDialog
 tool={tool}
 framework={selectedFramework}
/>
</MCPManagementPage>
```

**UI/UX needs:**
- Visual status indicators (green/red/yellow dots)
- Collapsible sections for server details
- Code editor for JSON config import with syntax highlighting
- Modal for tool testing with parameter inputs
- Copy-to-clipboard for exported tool definitions
- Toast notifications for connection success/failure
- Loading states during async operations

## Key Considerations

1. **Config format compatibility** - Support importing from:
   - Claude Desktop config (`claude_desktop_config.json`)
   - Cline/VSCode configs
   - Custom MCP config formats

2. **Error handling** - Gracefully handle:
   - Server startup failures
   - Connection timeouts
   - Invalid tool schemas
   - Missing dependencies

3. **Security** - 
   - Validate server commands before execution
   - Sandbox MCP server processes
   - Sanitize tool inputs in testing interface

4. **Performance** -
   - Cache tool schemas
   - Lazy-load server connections
   - Debounce connection tests

## Desired Output

Please provide:
1. Detailed backend API route handlers with Pydantic models
2. React component structure with state management approach
3. Example MCP config import logic (parsing Claude Desktop format)
4. Tool testing execution flow (frontend → backend → MCP server → response)
5. Framework-specific export formatters (CrewAI Tool, LangGraph tool binding)

The goal is a production-ready feature that makes MCP server management intuitive and integrates seamlessly with the existing orchestration workflow builder.
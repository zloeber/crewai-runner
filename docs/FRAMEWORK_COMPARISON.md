# Framework Comparison: CrewAI vs LangGraph

This document compares the two AI agent frameworks supported by crewai-runner.

## Overview

crewai-runner now supports multiple AI agent frameworks, allowing you to choose the best tool for your workflow needs:

- **CrewAI**: Agent-based framework focused on collaborative task completion
- **LangGraph**: Graph-based framework with flexible node and edge definitions

## When to Use Each Framework

### Use CrewAI When:
- You need agents with specific roles and responsibilities
- Your workflow follows a linear or hierarchical task structure
- You want agents to delegate tasks to each other
- You need built-in task dependencies and context sharing
- You're building multi-agent collaboration systems

### Use LangGraph When:
- You need complex conditional logic and branching
- Your workflow requires loops or cycles
- You want fine-grained control over execution flow
- You need to model state machines or decision trees
- You're building graph-based reasoning systems

## Configuration Structure

### CrewAI Configuration

```yaml
name: My Workflow
framework: crewai
description: Workflow description

agents:
  - name: researcher
    role: Research Analyst
    goal: Research topics
    backstory: Background story
    model: gpt-4
    tools: []
    allowDelegation: false
    verbose: true

tasks:
  - name: research_task
    description: Task description
    expected_output: Expected output
    agent: researcher
    context: []  # Task dependencies
    asyncExecution: false
```

### LangGraph Configuration

```yaml
name: My Workflow
framework: langgraph
description: Workflow description

nodes:
  - id: node1
    type: agent
    config:
      role: Research Analyst
      goal: Research topics
      model: gpt-4
      prompt: Full prompt text

  - id: node2
    type: agent
    config:
      role: Writer
      model: gpt-4

edges:
  - source: node1
    target: node2
  - source: node2
    target: END
    condition: "success"  # Optional conditional
```

## Key Differences

| Feature | CrewAI | LangGraph |
|---------|--------|-----------|
| Structure | Agent + Task based | Node + Edge based |
| Execution | Sequential/Hierarchical | Graph traversal |
| Delegation | Built-in | Manual via edges |
| Context Sharing | Automatic via task context | Manual state management |
| Conditional Logic | Limited | Full support |
| Loops | Not supported | Supported |
| Learning Curve | Lower | Higher |
| Flexibility | Medium | High |

## Migration Between Frameworks

### CrewAI to LangGraph

1. Convert each agent to a node with `type: agent`
2. Convert tasks to edges connecting nodes
3. Add start and end nodes
4. Task context becomes edge connections
5. Add conditional logic as needed

### LangGraph to CrewAI

1. Convert agent nodes to agents
2. Create tasks for each edge connection
3. Use task context for dependencies
4. Simplify conditional edges to linear flow
5. Note: Complex loops may need redesign

## Performance Considerations

### CrewAI
- **Strengths**: Optimized for agent collaboration, automatic context management
- **Best For**: Medium-complexity workflows (2-10 agents)
- **Overhead**: Low to medium

### LangGraph
- **Strengths**: Flexible execution, efficient graph traversal
- **Best For**: Complex workflows with conditional logic
- **Overhead**: Medium (requires state management)

## Example Workflows

See the `/examples` directory for sample configurations:

- `workflow.crewai-simple.yaml` - Basic CrewAI workflow
- `workflow.langgraph-simple.yaml` - Basic LangGraph workflow
- `workflow.ai-news-blog.yaml` - Complex CrewAI workflow with MCP tools

## API Usage

### Starting a Workflow

Both frameworks use the same API endpoint with the `framework` parameter:

```bash
POST /api/workflows/start
{
  "workflow": { ... },
  "framework": "crewai"  # or "langgraph"
}
```

### Validation

Validation is framework-specific:

```bash
POST /api/yaml/validate?framework=crewai
{
  "yamlContent": "..."
}
```

### Listing Supported Frameworks

```bash
GET /api/workflows/frameworks
```

Returns:
```json
{
  "frameworks": ["crewai", "langgraph"],
  "default": "crewai"
}
```

## Best Practices

### For Both Frameworks
1. Always specify the framework in your YAML configuration
2. Use descriptive names for agents/nodes
3. Test workflows with validation before execution
4. Monitor execution progress via status endpoints

### CrewAI Specific
1. Design clear agent roles with distinct responsibilities
2. Use task context to share information between tasks
3. Keep task descriptions specific and actionable
4. Consider delegation for complex workflows

### LangGraph Specific
1. Plan your graph structure before implementation
2. Use meaningful node IDs for clarity
3. Handle edge cases with conditional edges
4. Manage state carefully to avoid cycles

## Troubleshooting

### Common Issues

**CrewAI:**
- Agent references in tasks must match agent names exactly
- Tasks with context dependencies must reference valid task names
- Agents must have all required fields (name, role, goal, backstory, model)

**LangGraph:**
- All edges must reference valid node IDs
- Graph must have clear start and end points
- Avoid infinite loops without termination conditions
- Node configurations must match node type requirements

## Future Enhancements

Planned features for both frameworks:
- Real-time execution streaming
- Advanced tool integration
- Workflow templates library
- Visual workflow editor
- Performance analytics
- Multi-framework composition

## Support

For issues or questions:
- Check the examples in `/examples`
- Review the API documentation
- Open an issue on GitHub

# Configuration Management System Documentation

## Overview

The CrewAI Runner API now includes a comprehensive persistent configuration system that allows you to manage crew configurations, API settings, and application state through both CLI commands and REST API endpoints.

## Architecture

The configuration system is built using:
- **Pydantic models** for type-safe configuration validation
- **YAML files** for human-readable configuration storage
- **Click CLI** for command-line management
- **FastAPI endpoints** for programmatic access
- **File-based storage** in `~/.crewai-runner/` directory

## Core Components

### 1. Configuration Models

#### AgentConfig
```python
class AgentConfig(BaseModel):
    name: str
    role: str
    goal: str
    backstory: str
    tools: List[str] = []
    llm_config: Optional[Dict[str, Any]] = None
    max_iter: int = 5
    verbose: bool = True
    allow_delegation: bool = False
```

#### CrewConfig
```python
class CrewConfig(BaseModel):
    name: str
    description: str
    agents: List[AgentConfig]
    tasks: List[Dict[str, Any]] = []
    process: str = "sequential"  # or "hierarchical"
    verbose: bool = True
```

#### APIConfig
```python
class APIConfig(BaseModel):
    host: str = "localhost"
    port: int = 8000
    debug: bool = False
    cors_origins: List[str] = ["*"]
```

#### RunnerConfig
```python
class RunnerConfig(BaseModel):
    api: APIConfig
    crews: Dict[str, CrewConfig] = {}
    default_crew: Optional[str] = None
    config_version: str = "1.0"
```

### 2. Configuration Manager

The `ConfigManager` class handles all file operations:
- Loading/saving main configuration
- Managing crew configurations
- Directory structure management
- Validation and error handling

### 3. CLI Commands

Access through `crewai-runner-api config`:

```bash
# Initialize configuration
crewai-runner-api config init

# List crews
crewai-runner-api config list-crews

# Show crew details
crewai-runner-api config show-crew <crew_name>

# Show current configuration
crewai-runner-api config show-config

# Export crew to file
crewai-runner-api config export-crew <crew_name> -o <file.yaml>

# Import crew from file
crewai-runner-api config import-crew <file.yaml>

# Delete crew
crewai-runner-api config delete-crew <crew_name>
```

### 4. REST API Endpoints

Base path: `/api/config`

#### Configuration Endpoints
- `GET /api/config` - Get current configuration
- `GET /api/config/info` - Get configuration directory info
- `POST /api/config/init` - Initialize configuration

#### Crew Management Endpoints
- `GET /api/config/crews` - List all crews
- `GET /api/config/crews/{crew_name}` - Get specific crew
- `POST /api/config/crews` - Create/update crew
- `PUT /api/config/crews/{crew_name}` - Update specific crew
- `DELETE /api/config/crews/{crew_name}` - Delete crew
- `POST /api/config/crews/{crew_name}/duplicate?new_name=<name>` - Duplicate crew

## File Structure

Configuration files are stored in `~/.crewai-runner/`:

```
~/.crewai-runner/
├── config.yaml           # Main configuration
└── crews/                # Crew configurations
    ├── research_team.yaml
    ├── development_team.yaml
    └── marketing_team.yaml
```

## Example Configurations

### Main Configuration (config.yaml)
```yaml
api:
  host: "localhost"
  port: 8000
  debug: true
  cors_origins:
    - "http://localhost:3000"
    - "http://localhost:5173"

crews: {}
default_crew: "research_team"
config_version: "1.0"
```

### Crew Configuration (research_team.yaml)
```yaml
name: "research_team"
description: "A team for conducting research and creating content"
process: "sequential"
verbose: true

agents:
  - name: "researcher"
    role: "Senior Research Analyst"
    goal: "Conduct thorough research on given topics"
    backstory: "You are an experienced researcher with expertise in data analysis."
    tools: ["search", "web_scraper"]
    max_iter: 5
    verbose: true
    allow_delegation: false
  
  - name: "writer"
    role: "Content Writer"
    goal: "Create engaging content based on research"
    backstory: "You are a skilled writer who transforms research into compelling content."
    tools: ["text_editor"]
    max_iter: 3
    verbose: true
    allow_delegation: false

tasks:
  - name: "research_task"
    description: "Research the given topic thoroughly"
    agent: "researcher"
    expected_output: "Comprehensive research report with findings and sources"
    tools: ["search", "web_scraper"]
    async_execution: false
    context: []
    output_json: false
  
  - name: "writing_task"
    description: "Write an article based on research findings"
    agent: "writer"
    expected_output: "Well-written article of 800-1200 words"
    tools: ["text_editor"]
    async_execution: false
    context: ["research_task"]
    output_json: false
```

## Usage Examples

### CLI Usage

1. **Initialize configuration:**
```bash
crewai-runner-api config init
```

2. **List available crews:**
```bash
crewai-runner-api config list-crews
```

3. **Show crew details:**
```bash
crewai-runner-api config show-crew research_team
```

4. **Import a crew:**
```bash
crewai-runner-api config import-crew ./examples/config/development_team.yaml
```

### API Usage

1. **Get all crews:**
```bash
curl http://localhost:8000/api/config/crews
```

2. **Create a new crew:**
```bash
curl -X POST http://localhost:8000/api/config/crews \
  -H "Content-Type: application/json" \
  -d @crew_config.json
```

3. **Get specific crew:**
```bash
curl http://localhost:8000/api/config/crews/research_team
```

### Python Usage

```python
from src.engine.config_manager import ConfigManager
from src.engine.models import CrewConfig, AgentConfig

# Initialize manager
manager = ConfigManager()

# Load configuration
config = manager.load_config()

# Create and save a crew
agent = AgentConfig(
    name="analyst",
    role="Data Analyst",
    goal="Analyze data",
    backstory="Expert in data analysis"
)

crew = CrewConfig(
    name="analytics_team",
    description="Data analysis team",
    agents=[agent]
)

manager.save_crew(crew)
```

## Benefits

1. **Type Safety**: Pydantic models ensure configuration validity
2. **Version Control**: YAML files can be tracked in git
3. **Portability**: Easy import/export of configurations
4. **Scalability**: Modular crew configurations
5. **Flexibility**: Both CLI and API access
6. **Validation**: Automatic validation of configuration data
7. **Documentation**: Self-documenting configuration files

## Migration and Compatibility

The configuration system is designed to be:
- **Backward compatible** with existing workflow definitions
- **Forward compatible** with version tracking
- **Extensible** for future features
- **Non-destructive** - existing configurations remain unchanged

## Error Handling

The system includes comprehensive error handling:
- Configuration file corruption recovery
- Missing file automatic creation
- Validation error reporting
- Graceful fallbacks to defaults

## Testing

The configuration system has been tested for:
- Model validation and serialization
- File operations (save/load/delete)
- Directory management
- YAML parsing and generation
- CLI command functionality
- API endpoint responses

All tests pass successfully, confirming the system is ready for production use.
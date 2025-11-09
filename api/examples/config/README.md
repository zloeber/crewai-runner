# Configuration Management System

This directory contains example configuration files for the CrewAI Runner API.

## Files

- `config.yaml` - Main API configuration file
- `research_team.yaml` - Example research and content creation crew
- `development_team.yaml` - Example software development crew  
- `marketing_team.yaml` - Example marketing strategy crew

## Usage

### CLI Commands

Initialize configuration:
```bash
crewai-runner-api config init
```

List available crews:
```bash
crewai-runner-api config list-crews
```

Show crew details:
```bash
crewai-runner-api config show-crew research_team
```

Import a crew from file:
```bash
crewai-runner-api config import-crew research_team.yaml
```

Export a crew to file:
```bash
crewai-runner-api config export-crew research_team -o exported_crew.yaml
```

### API Endpoints

- `GET /api/config` - Get current configuration
- `GET /api/config/crews` - List all crews
- `GET /api/config/crews/{crew_name}` - Get specific crew
- `POST /api/config/crews` - Create/update crew
- `DELETE /api/config/crews/{crew_name}` - Delete crew
- `POST /api/config/init` - Initialize configuration

## Configuration Structure

### Main Configuration (`config.yaml`)

```yaml
api:
  host: "localhost"
  port: 8000
  debug: true
  cors_origins:
    - "http://localhost:3000"

crews: {}
default_crew: "research_team"
config_version: "1.0"
```

### Crew Configuration

```yaml
name: "team_name"
description: "Team description"
process: "sequential"  # or "hierarchical"
verbose: true

agents:
  - name: "agent_name"
    role: "Agent Role"
    goal: "Agent's main objective"
    backstory: "Agent's background and expertise"
    tools: ["tool1", "tool2"]
    max_iter: 5
    verbose: true
    allow_delegation: false

tasks:
  - name: "task_name"
    description: "Task description"
    agent: "agent_name"
    expected_output: "What the task should produce"
    context: ["previous_task"]  # Dependencies
```

## Storage Location

Configuration files are stored in `~/.crewai-runner/` by default:

- Main config: `~/.crewai-runner/config.yaml`
- Crews: `~/.crewai-runner/crews/*.yaml`

You can override the location using the `--config-dir` option with CLI commands.
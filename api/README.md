# CrewAI Workflow Interface API

FastAPI backend service for managing CrewAI workflows, agents, and tasks.

## Features

- **Provider Management**: Configure AI model providers (OpenAI, Anthropic, Ollama, etc.)
- **Model Management**: Register and manage AI models
- **Workflow Execution**: Start, stop, and monitor CrewAI workflows
- **Chat Interface**: Send messages to running workflows
- **YAML Validation**: Validate workflow definitions

## Setup

### Local Development

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Create a `.env` file (copy from `.env.example`):
```bash
cp .env.example .env
```

3. Update the API key in `.env`:
```
API_KEY=your-secure-api-key-here
```

4. Run the development server:
```bash
uvicorn main:app --reload --port 8000
```

The API will be available at:
- API: http://localhost:8000/api
- Documentation: http://localhost:8000/api/docs
- Health Check: http://localhost:8000/health

### Docker

Build and run with Docker:
```bash
docker build -t crewai-api .
docker run -p 8000:8000 -e API_KEY=your-key crewai-api
```

### Docker Compose

From the project root:
```bash
docker-compose up
```

This will start both the frontend and backend services.

## API Documentation

See [API_SCHEMA.md](./API_SCHEMA.md) for detailed API documentation.

### Authentication

All API endpoints require authentication using a Bearer token:

```bash
curl -H "Authorization: Bearer your-api-key" http://localhost:8000/api/providers
```

### Example Requests

List providers:
```bash
curl -H "Authorization: Bearer dev-api-key-change-in-production" \
  http://localhost:8000/api/providers
```

Add a provider:
```bash
curl -X POST -H "Authorization: Bearer dev-api-key-change-in-production" \
  -H "Content-Type: application/json" \
  -d '{"provider": {"name": "OpenAI", "type": "openai", "apiKey": "sk-..."}}' \
  http://localhost:8000/api/providers
```

Start a workflow:
```bash
curl -X POST -H "Authorization: Bearer dev-api-key-change-in-production" \
  -H "Content-Type: application/json" \
  -d @workflow.json \
  http://localhost:8000/api/workflows/start
```

## Project Structure

```
api/
├── __init__.py           # Package initialization
├── main.py               # FastAPI application
├── config.py             # Configuration management
├── auth.py               # Authentication middleware
├── models.py             # Pydantic models
├── routers/              # API route handlers
│   ├── __init__.py
│   ├── providers.py      # Provider endpoints
│   ├── models.py         # Model endpoints
│   ├── workflows.py      # Workflow endpoints
│   ├── chat.py           # Chat endpoints
│   └── yaml_validator.py # YAML validation endpoints
├── requirements.txt      # Python dependencies
├── Dockerfile            # Docker configuration
└── .env.example          # Example environment variables
```

## Development

### Running Tests

```bash
pytest
```

### Code Formatting

```bash
black .
ruff check --fix .
```

## Environment Variables

- `API_KEY`: API authentication key (required)
- `API_BASE_URL`: API base path (default: `/api`)
- `API_HOST`: Server host (default: `0.0.0.0`)
- `API_PORT`: Server port (default: `8000`)
- `API_RELOAD`: Enable auto-reload in development (default: `false`)

## TODO

- Integrate with CrewAI for actual workflow execution
- Add database persistence (currently using in-memory storage)
- Implement WebSocket support for real-time updates
- Add workflow result retrieval endpoints
- Implement workflow cancellation
- Add comprehensive test suite

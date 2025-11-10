# CrewAI Runner - Architecture

## System Overview

CrewAI Runner is a full-stack application that provides a web interface for managing and executing CrewAI workflows. It consists of a React frontend, FastAPI backend, and uses Docker for containerization.

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                        Client Browser                        │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           │ HTTP/HTTPS
                           │
┌──────────────────────────▼──────────────────────────────────┐
│                     Frontend Container                       │
│                                                              │
│  ┌────────────────────────────────────────────────────┐    │
│  │              Nginx (Port 80)                       │    │
│  │  - Serve static files (React build)                │    │
│  │  - Proxy /api/* to backend:8000                    │    │
│  │  - Gzip compression                                 │    │
│  │  - Security headers                                 │    │
│  └────────────────────────────────────────────────────┘    │
│                                                              │
│  ┌────────────────────────────────────────────────────┐    │
│  │         React Application (Vite)                   │    │
│  │  - TypeScript                                       │    │
│  │  - TailwindCSS                                      │    │
│  │  - shadcn/ui components                            │    │
│  └────────────────────────────────────────────────────┘    │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           │ Internal Network
                           │ /api/* requests
                           │
┌──────────────────────────▼──────────────────────────────────┐
│                     Backend Container                        │
│                                                              │
│  ┌────────────────────────────────────────────────────┐    │
│  │            FastAPI (Port 8000)                     │    │
│  │  - RESTful API                                      │    │
│  │  - OpenAPI/Swagger docs                            │    │
│  │  - Bearer token auth                               │    │
│  │  - CORS middleware                                  │    │
│  └────────────────────────────────────────────────────┘    │
│                                                              │
│  ┌────────────────────────────────────────────────────┐    │
│  │               API Routers                          │    │
│  │  ┌──────────────────────────────────────────┐     │    │
│  │  │ Providers Router                          │     │    │
│  │  │  - GET/POST /api/providers               │     │    │
│  │  └──────────────────────────────────────────┘     │    │
│  │  ┌──────────────────────────────────────────┐     │    │
│  │  │ Models Router                             │     │    │
│  │  │  - GET/POST /api/models                  │     │    │
│  │  └──────────────────────────────────────────┘     │    │
│  │  ┌──────────────────────────────────────────┐     │    │
│  │  │ Workflows Router                          │     │    │
│  │  │  - POST /api/workflows/start             │     │    │
│  │  │  - POST /api/workflows/stop              │     │    │
│  │  │  - GET /api/workflows/{id}/status        │     │    │
│  │  └──────────────────────────────────────────┘     │    │
│  │  ┌──────────────────────────────────────────┐     │    │
│  │  │ Chat Router                               │     │    │
│  │  │  - POST /api/chat                        │     │    │
│  │  └──────────────────────────────────────────┘     │    │
│  │  ┌──────────────────────────────────────────┐     │    │
│  │  │ YAML Router                               │     │    │
│  │  │  - POST /api/yaml/validate               │     │    │
│  │  └──────────────────────────────────────────┘     │    │
│  └────────────────────────────────────────────────────┘    │
│                                                              │
│  ┌────────────────────────────────────────────────────┐    │
│  │             CrewAI Integration                     │    │
│  │  - Workflow execution                              │    │
│  │  - Agent management                                │    │
│  │  - Task orchestration                              │    │
│  └────────────────────────────────────────────────────┘    │
│                                                              │
│  ┌────────────────────────────────────────────────────┐    │
│  │             Data Storage                           │    │
│  │  - In-memory (development)                         │    │
│  │  - Database (production TODO)                      │    │
│  └────────────────────────────────────────────────────┘    │
└──────────────────────────────────────────────────────────────┘
```

## Component Details

### Frontend Layer

#### React Application
- **Framework**: React 18 with TypeScript
- **Build Tool**: Vite for fast development and optimized builds
- **UI Components**: shadcn/ui component library
- **Styling**: TailwindCSS for utility-first styling
- **State Management**: React hooks and context

#### Nginx Server
- **Purpose**: Production web server
- **Responsibilities**:
  - Serve static files (HTML, CSS, JS, images)
  - Proxy API requests to backend
  - Handle gzip compression
  - Set security headers
  - Cache static assets

### Backend Layer

#### FastAPI Application
- **Framework**: FastAPI for modern Python API
- **Python Version**: 3.12
- **ASGI Server**: Uvicorn for async request handling
- **Features**:
  - Automatic OpenAPI documentation
  - Request/response validation with Pydantic
  - Async/await support
  - Dependency injection

#### Authentication Middleware
- **Type**: Bearer token authentication
- **Implementation**: HTTPBearer security scheme
- **Flow**:
  1. Client sends request with `Authorization: Bearer <token>`
  2. Middleware validates token
  3. Request proceeds if valid, returns 401 if invalid

#### API Routers

**Providers Router** (`/api/providers`)
- Manages AI model provider configurations
- CRUD operations for provider entities
- Stores provider credentials securely

**Models Router** (`/api/models`)
- Manages AI model registrations
- Links models to providers
- Tracks model capabilities and settings

**Workflows Router** (`/api/workflows`)
- Start and stop workflow execution
- Query workflow status and progress
- Track agent states within workflows

**Chat Router** (`/api/chat`)
- Send messages to running workflows
- Receive responses from agents
- Enable interactive workflow control

**YAML Router** (`/api/yaml`)
- Validate YAML workflow definitions
- Parse and convert to internal format
- Provide validation errors

### Data Models

#### Pydantic Models
All data structures use Pydantic for validation:
- **Provider**: AI provider configuration
- **Model**: AI model registration
- **Agent**: Workflow agent definition
- **Task**: Workflow task definition
- **Workflow**: Complete workflow specification

### CrewAI Integration

The backend integrates with CrewAI for workflow execution:

```python
# Workflow execution flow
1. Receive workflow definition via API
2. Create CrewAI agents from agent definitions
3. Create CrewAI tasks from task definitions
4. Initialize CrewAI crew with agents and tasks
5. Start crew execution
6. Monitor progress and status
7. Return results to client
```

## Data Flow

### Starting a Workflow

```
Client                Frontend              Backend              CrewAI
  │                      │                    │                   │
  │  Submit Workflow     │                    │                   │
  ├─────────────────────>│                    │                   │
  │                      │  POST /workflows/start                 │
  │                      ├───────────────────>│                   │
  │                      │                    │  Create Crew      │
  │                      │                    ├──────────────────>│
  │                      │                    │                   │
  │                      │                    │  Start Execution  │
  │                      │                    ├──────────────────>│
  │                      │   WorkflowId       │                   │
  │                      │<───────────────────┤                   │
  │   WorkflowId         │                    │                   │
  │<─────────────────────┤                    │                   │
```

### Checking Workflow Status

```
Client                Frontend              Backend              CrewAI
  │                      │                    │                   │
  │  Check Status        │                    │                   │
  ├─────────────────────>│                    │                   │
  │                      │  GET /workflows/{id}/status            │
  │                      ├───────────────────>│                   │
  │                      │                    │  Query Status     │
  │                      │                    ├──────────────────>│
  │                      │                    │   Status Data     │
  │                      │                    │<──────────────────┤
  │                      │   Status Response  │                   │
  │                      │<───────────────────┤                   │
  │   Status Data        │                    │                   │
  │<─────────────────────┤                    │                   │
```

## Network Architecture

### Docker Network

```
┌─────────────────────────────────────────────────────────┐
│              crewai-network (bridge)                    │
│                                                         │
│  ┌─────────────────┐         ┌──────────────────┐     │
│  │   frontend:80   │────────>│  backend:8000    │     │
│  │  (nginx)        │         │  (uvicorn)       │     │
│  └─────────────────┘         └──────────────────┘     │
│         │                                               │
└─────────│───────────────────────────────────────────────┘
          │
          │ Port mapping
          │
     Host:80 ────> Container:80 (frontend)
     Host:8000 ──> Container:8000 (backend)
```

### Service Discovery

Services communicate using Docker's built-in DNS:
- Frontend can reach backend at `http://backend:8000`
- Backend is isolated from direct external access (except port 8000 for dev)
- Frontend acts as API gateway

## Security Architecture

### Authentication Flow

```
1. Client obtains API key from configuration
2. Client includes key in Authorization header
3. Backend validates key via security dependency
4. Request proceeds if valid, 401 if invalid
```

### Security Measures

- **HTTPS**: Should be enabled in production via reverse proxy
- **CORS**: Configured to allow frontend domain
- **API Key**: Bearer token authentication on all endpoints
- **Input Validation**: Pydantic models validate all inputs
- **Error Handling**: Sanitized error messages
- **Security Headers**: X-Frame-Options, X-Content-Type-Options, etc.

## Scalability Considerations

### Current Architecture
- Single backend instance
- In-memory data storage
- Synchronous workflow execution

### Production Recommendations

1. **Database**: Add PostgreSQL or MongoDB for persistent storage
2. **Message Queue**: Add Redis/RabbitMQ for async tasks
3. **Load Balancer**: Add nginx or HAProxy for multiple backend instances
4. **Caching**: Add Redis for API response caching
5. **Monitoring**: Add Prometheus + Grafana for metrics
6. **Logging**: Centralized logging with ELK stack

### Scaling Diagram

```
                    ┌─────────────┐
                    │Load Balancer│
                    └──────┬──────┘
                           │
           ┌───────────────┼───────────────┐
           │               │               │
    ┌──────▼─────┐  ┌──────▼─────┐  ┌─────▼──────┐
    │Backend #1  │  │Backend #2  │  │Backend #3  │
    └──────┬─────┘  └──────┬─────┘  └─────┬──────┘
           │               │               │
           └───────────────┼───────────────┘
                           │
                    ┌──────▼──────┐
                    │  Database   │
                    └──────┬──────┘
                           │
                    ┌──────▼──────┐
                    │Message Queue│
                    └─────────────┘
```

## Development vs Production

### Development Mode
- Hot reloading enabled
- Volume mounts for code changes
- Debug logging
- CORS allows all origins
- Development Dockerfile

### Production Mode
- Optimized builds
- No volume mounts
- Production logging
- CORS restricted to frontend domain
- Multi-stage Dockerfiles
- Health checks enabled

## Configuration Management

### Environment Variables

**Backend**:
```env
API_KEY          # Authentication key
API_BASE_URL     # API path prefix
API_HOST         # Server host
API_PORT         # Server port
API_RELOAD       # Enable hot reload
```

**Frontend**:
```env
VITE_API_URL     # Backend API URL
```

### Configuration Sources
1. Environment variables (highest priority)
2. .env file
3. Default values in code

## Monitoring and Health Checks

### Health Check Endpoints

**Backend**: `GET /health`
```json
{
  "status": "healthy"
}
```

**Docker Health Checks**:
- Backend: `curl -f http://localhost:8000/health`
- Frontend: `wget --quiet --tries=1 --spider http://localhost:80`

### Metrics (TODO)
- Request count
- Response time
- Error rate
- Workflow execution time
- Active workflows

## Future Enhancements

1. **WebSocket Support**: Real-time workflow updates
2. **User Management**: Multi-user support with roles
3. **Workflow Templates**: Pre-defined workflow templates
4. **Result Storage**: Persistent workflow results
5. **Scheduling**: Scheduled workflow execution
6. **API Versioning**: Version management for API
7. **Rate Limiting**: Request rate limiting
8. **Audit Logging**: Complete audit trail
9. **Backup/Restore**: Data backup mechanisms
10. **Multi-tenancy**: Support for multiple organizations

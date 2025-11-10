# Deployment Guide

This document describes how to deploy the CrewAI Runner application using Docker and docker-compose.

## Prerequisites

- Docker (version 20.10 or later)
- Docker Compose (version 2.0 or later)
- Git

## Quick Start

### 1. Clone the Repository

```bash
git clone https://github.com/zloeber/crewai-runner.git
cd crewai-runner
```

### 2. Configure Environment Variables

Create a `.env` file in the root directory:

```bash
cp .env.example .env
```

Edit the `.env` file and set your API key:

```env
API_KEY=your-secure-api-key-here
```

### 3. Build and Start Services

```bash
docker-compose up -d
```

This will:
- Build the backend API service (FastAPI)
- Build the frontend service (React/Vite)
- Start both services with proper networking

### 4. Access the Application

- **Frontend**: http://localhost
- **API Documentation**: http://localhost/api/docs
- **API Redoc**: http://localhost/api/redoc
- **Health Check**: http://localhost:8000/health

## Service Architecture

```
┌─────────────────┐
│   Frontend      │
│   (React/Vite)  │
│   Port: 80      │
└────────┬────────┘
         │
         │ Nginx Proxy
         │ /api -> backend
         │
┌────────▼────────┐
│   Backend       │
│   (FastAPI)     │
│   Port: 8000    │
└─────────────────┘
```

## Services

### Backend API

- **Technology**: Python 3.12, FastAPI, CrewAI
- **Port**: 8000
- **Location**: `./api`
- **Features**:
  - RESTful API for workflow management
  - Provider and model configuration
  - Workflow execution with CrewAI
  - Chat interface for workflow interaction
  - YAML workflow validation

### Frontend

- **Technology**: Node.js 20, React, Vite, TypeScript
- **Port**: 80
- **Location**: `./frontend`
- **Features**:
  - Web-based UI for CrewAI workflows
  - Provider and model management
  - Real-time workflow monitoring
  - Interactive chat interface

## Docker Commands

### Build Services

```bash
# Build all services
docker-compose build

# Build specific service
docker-compose build backend
docker-compose build frontend
```

### Start Services

```bash
# Start in foreground
docker-compose up

# Start in background (detached)
docker-compose up -d

# Start specific service
docker-compose up backend
```

### Stop Services

```bash
# Stop all services
docker-compose down

# Stop and remove volumes
docker-compose down -v
```

### View Logs

```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f backend
docker-compose logs -f frontend
```

### Rebuild and Restart

```bash
# Rebuild and restart all services
docker-compose up -d --build

# Rebuild specific service
docker-compose up -d --build backend
```

## Development Mode

For local development without Docker:

### Backend Development

```bash
cd api
pip install -r requirements.txt
cp .env.example .env
# Edit .env with your settings
uvicorn main:app --reload --port 8000
```

### Frontend Development

```bash
cd frontend
pnpm install
pnpm dev
```

## Environment Variables

### Backend (.env)

```env
API_KEY=your-secure-api-key-here
API_BASE_URL=/api
API_HOST=0.0.0.0
API_PORT=8000
API_RELOAD=false
```

### Frontend

Frontend configuration is built into the Docker image. To customize, edit the `frontend/.env` file before building.

## Health Checks

Both services include health checks:

- **Backend**: `curl http://localhost:8000/health`
- **Frontend**: `curl http://localhost/`

Docker Compose will automatically monitor service health.

## Networking

All services communicate through a Docker bridge network named `crewai-network`. This provides:

- Service discovery by name (e.g., `http://backend:8000`)
- Isolation from other Docker networks
- Easy service-to-service communication

## Volume Management

The backend service mounts the local `./api` directory for development. To persist data in production, add volume mounts in `docker-compose.yml`:

```yaml
volumes:
  - ./data:/app/data  # For database files
  - ./logs:/app/logs  # For log files
```

## Troubleshooting

### Services Won't Start

1. Check logs: `docker-compose logs`
2. Verify ports are available: `netstat -an | grep -E '80|8000'`
3. Check Docker status: `docker ps -a`

### API Connection Issues

1. Verify backend is running: `docker-compose ps`
2. Check backend health: `curl http://localhost:8000/health`
3. Verify API key in `.env` file

### Frontend Not Loading

1. Check nginx logs: `docker-compose logs frontend`
2. Verify backend is accessible: `docker-compose exec frontend curl http://backend:8000/health`
3. Check browser console for errors

### Permission Issues

If you encounter permission issues, ensure Docker has proper permissions:

```bash
# Linux: Add user to docker group
sudo usermod -aG docker $USER
# Logout and login again
```

## Production Deployment

For production deployment:

1. **Update API Key**: Use a strong, random API key
2. **Enable HTTPS**: Configure SSL certificates (use Let's Encrypt)
3. **Database**: Replace in-memory storage with persistent database
4. **Logging**: Configure centralized logging
5. **Monitoring**: Add monitoring and alerting
6. **Backups**: Implement backup strategy for data
7. **Security**: Review and harden security settings

### Example Production docker-compose.yml

```yaml
version: '3.8'

services:
  backend:
    build: ./api
    restart: always
    environment:
      - API_KEY=${API_KEY}
      - DATABASE_URL=postgresql://user:pass@db:5432/crewai
    depends_on:
      - db

  frontend:
    build: ./frontend
    restart: always
    depends_on:
      - backend

  db:
    image: postgres:15
    restart: always
    environment:
      - POSTGRES_DB=crewai
      - POSTGRES_USER=user
      - POSTGRES_PASSWORD=${DB_PASSWORD}
    volumes:
      - pgdata:/var/lib/postgresql/data

  nginx:
    image: nginx:alpine
    restart: always
    ports:
      - "443:443"
      - "80:80"
    volumes:
      - ./nginx/nginx.conf:/etc/nginx/nginx.conf
      - ./nginx/ssl:/etc/nginx/ssl
    depends_on:
      - frontend

volumes:
  pgdata:
```

## Support

For issues and questions:
- GitHub Issues: https://github.com/zloeber/crewai-runner/issues
- Documentation: See README.md and API_SCHEMA.md

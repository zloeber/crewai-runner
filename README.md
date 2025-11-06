# CrewAI Runner

A full-stack application for managing and executing CrewAI workflows with a modern web interface.

## 🚀 Quick Start

### Using Docker (Recommended)

```bash
# Clone the repository
git clone https://github.com/zloeber/crewai-runner.git
cd crewai-runner

# Configure environment
cp .env.example .env
# Edit .env and set your API_KEY

# Start all services
docker-compose up -d
```

Access the application:
- **Frontend**: http://localhost
- **API Documentation**: http://localhost/api/docs
- **Health Check**: http://localhost:8000/health

### Local Development

See [DEPLOYMENT.md](./DEPLOYMENT.md) for detailed deployment instructions.

## 📁 Project Structure

```
crewai-runner/
├── api/                    # FastAPI Backend
│   ├── routers/           # API route handlers
│   ├── main.py            # FastAPI application
│   ├── models.py          # Pydantic models
│   ├── config.py          # Configuration
│   ├── auth.py            # Authentication
│   ├── requirements.txt   # Python dependencies
│   ├── Dockerfile         # Backend Docker image
│   └── README.md          # API documentation
├── frontend/              # React/Vite Frontend
│   ├── src/              # React components
│   ├── Dockerfile        # Frontend Docker image
│   ├── nginx.conf        # Nginx configuration
│   └── package.json      # Node.js dependencies
├── docker-compose.yml    # Docker orchestration
├── DEPLOYMENT.md         # Deployment guide
└── README.md             # This file
```

## 🎯 Features

### Backend API
- ✅ **Provider Management**: Configure AI model providers (OpenAI, Anthropic, Ollama, etc.)
- ✅ **Model Management**: Register and manage AI models
- ✅ **Workflow Execution**: Start, stop, and monitor CrewAI workflows
- ✅ **Chat Interface**: Send messages to running workflows
- ✅ **YAML Validation**: Validate workflow definitions
- ✅ **API Authentication**: Bearer token authentication
- ✅ **Auto-generated Docs**: OpenAPI/Swagger documentation

### Frontend
- 🎨 Modern React UI with TypeScript
- 📱 Responsive design with TailwindCSS
- 🔧 Built with Vite for fast development

## 🔌 API Endpoints

### Providers
- `GET /api/providers` - List all providers
- `POST /api/providers` - Add a new provider

### Models
- `GET /api/models` - List all models
- `POST /api/models` - Add a new model

### Workflows
- `POST /api/workflows/start` - Start a workflow
- `POST /api/workflows/stop` - Stop a workflow
- `GET /api/workflows/{id}/status` - Get workflow status

### Chat
- `POST /api/chat` - Send message to workflow

### YAML
- `POST /api/yaml/validate` - Validate YAML workflow

See [api/API_SCHEMA.md](./api/API_SCHEMA.md) for detailed API documentation.

## 🔒 Authentication

All API endpoints require authentication using a Bearer token:

```bash
curl -H "Authorization: Bearer your-api-key" \
  http://localhost:8000/api/providers
```

Configure the API key in your `.env` file:

```env
API_KEY=your-secure-api-key-here
```

## 🛠️ Development

### Backend Development

```bash
cd api
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

### Frontend Development

```bash
cd frontend
pnpm install
pnpm dev
```

### Verification

Run the verification script to check the structure:

```bash
./verify_structure.sh
```

## 📚 Documentation

- [API Schema](./api/API_SCHEMA.md) - Complete API specification
- [API README](./api/README.md) - Backend documentation
- [Deployment Guide](./DEPLOYMENT.md) - Comprehensive deployment instructions

## 🐳 Docker

The application is fully containerized with Docker:

- **Backend**: Python 3.12 with FastAPI
- **Frontend**: Node 20 build → Nginx serve
- **Networking**: Bridge network for service communication
- **Health Checks**: Automatic service health monitoring

### Docker Commands

```bash
# Start services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down

# Rebuild
docker-compose up -d --build
```

## 🧪 Testing

### API Structure Verification

```bash
cd api
python3 minimal_test.py
```

### Endpoint Verification

```bash
./verify_structure.sh
```

## 🔄 Architecture

```
┌─────────────────┐
│   Frontend      │  React/Vite Application
│   (Port 80)     │  Static files + API proxy
└────────┬────────┘
         │
         │ Nginx Proxy (/api → backend)
         │
┌────────▼────────┐
│   Backend       │  FastAPI Application
│   (Port 8000)   │  CrewAI Integration
└─────────────────┘
```

## 📝 Environment Variables

### Backend

```env
API_KEY=your-api-key-here
API_BASE_URL=/api
API_HOST=0.0.0.0
API_PORT=8000
API_RELOAD=false
```

See [api/.env.example](./api/.env.example) for more details.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

See LICENSE file for details.

## 🆘 Support

- **Issues**: [GitHub Issues](https://github.com/zloeber/crewai-runner/issues)
- **Documentation**: See [DEPLOYMENT.md](./DEPLOYMENT.md) for troubleshooting

## 🎉 Credits

Built with:
- [FastAPI](https://fastapi.tiangolo.com/) - Modern Python web framework
- [CrewAI](https://www.crewai.com/) - Multi-agent AI framework
- [React](https://react.dev/) - Frontend library
- [Vite](https://vitejs.dev/) - Build tool
- [Docker](https://www.docker.com/) - Containerization

---

Made with ❤️ for the CrewAI community

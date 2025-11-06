.PHONY: help up down logs build rebuild clean verify test dev prod backend frontend

# Default target
help:
	@echo "CrewAI Runner - Available Commands"
	@echo "=================================="
	@echo ""
	@echo "Production:"
	@echo "  make up          - Start all services (production mode)"
	@echo "  make down        - Stop all services"
	@echo "  make logs        - View logs from all services"
	@echo "  make build       - Build Docker images"
	@echo "  make rebuild     - Rebuild and restart services"
	@echo ""
	@echo "Development:"
	@echo "  make dev         - Start in development mode (hot reload)"
	@echo "  make dev-down    - Stop development services"
	@echo "  make dev-logs    - View development logs"
	@echo ""
	@echo "Testing & Verification:"
	@echo "  make verify      - Run structure verification"
	@echo "  make test        - Run API structure test"
	@echo ""
	@echo "Maintenance:"
	@echo "  make clean       - Clean up containers and volumes"
	@echo "  make backend     - Access backend shell"
	@echo "  make frontend    - Access frontend shell"
	@echo ""

# Production commands
up:
	@echo "Starting services in production mode..."
	docker-compose up -d

down:
	@echo "Stopping services..."
	docker-compose down

logs:
	@echo "Viewing logs (Ctrl+C to exit)..."
	docker-compose logs -f

build:
	@echo "Building Docker images..."
	docker-compose build

rebuild:
	@echo "Rebuilding and restarting services..."
	docker-compose up -d --build

# Development commands
dev:
	@echo "Starting services in development mode..."
	docker-compose -f docker-compose.dev.yml up -d
	@echo ""
	@echo "Services started:"
	@echo "  Frontend: http://localhost:5173"
	@echo "  Backend:  http://localhost:8000"
	@echo "  API Docs: http://localhost:8000/api/docs"

dev-down:
	@echo "Stopping development services..."
	docker-compose -f docker-compose.dev.yml down

dev-logs:
	@echo "Viewing development logs (Ctrl+C to exit)..."
	docker-compose -f docker-compose.dev.yml logs -f

# Testing & Verification
verify:
	@echo "Running structure verification..."
	@./verify_structure.sh

test:
	@echo "Running API structure test..."
	@cd api && python3 minimal_test.py

# Maintenance
clean:
	@echo "Cleaning up containers and volumes..."
	docker-compose down -v
	@echo "Removing __pycache__ directories..."
	@find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	@echo "Cleanup complete!"

backend:
	@echo "Accessing backend container shell..."
	docker-compose exec backend /bin/sh

frontend:
	@echo "Accessing frontend container shell..."
	docker-compose exec frontend /bin/sh

# Status
status:
	@echo "Service Status:"
	@echo "==============="
	@docker-compose ps

# Configuration
config:
	@echo "Docker Compose Configuration:"
	@echo "============================="
	@docker-compose config

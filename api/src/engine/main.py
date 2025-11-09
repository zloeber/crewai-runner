"""FastAPI main application for CrewAI Workflow Interface."""

from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from .config import settings
from .models import ErrorResponse
from .routers import (
    providers,
    models,
    workflows,
    chat,
    yaml_validator,
    profiles,
    mcp,
    config,
)
from .services.orchestrator_factory import OrchestratorFactory
from .adapters import CrewAIAdapter, LangGraphAdapter

# Create FastAPI app
app = FastAPI(
    title="CrewAI Workflow Interface API",
    description="API for managing CrewAI workflows, agents, and tasks with multi-framework support",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json",
)

# Register orchestrators
OrchestratorFactory.register("crewai", CrewAIAdapter)
OrchestratorFactory.register("langgraph", LangGraphAdapter)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, restrict to specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(providers.router, prefix=settings.api_base_url)
app.include_router(models.router, prefix=settings.api_base_url)
app.include_router(workflows.router, prefix=settings.api_base_url)
app.include_router(chat.router, prefix=settings.api_base_url)
app.include_router(yaml_validator.router, prefix=settings.api_base_url)
app.include_router(profiles.router, prefix=settings.api_base_url)
app.include_router(mcp.router, prefix=settings.api_base_url)
app.include_router(config.router, prefix=settings.api_base_url)


# Exception handlers
@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """Handle HTTP exceptions."""
    return JSONResponse(
        status_code=exc.status_code,
        content=ErrorResponse(
            error=exc.detail,
            message=str(exc.detail),
        ).model_dump(),
    )


@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """Handle general exceptions."""
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=ErrorResponse(
            error="Internal Server Error",
            message=str(exc),
        ).model_dump(),
    )


# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "CrewAI Workflow Interface API",
        "docs": "/api/docs",
        "health": "/health",
    }


def run_server(host: str = "0.0.0.0", port: int = 8000):
    """Run the FastAPI server."""
    import uvicorn

    uvicorn.run(app, host=settings.host, port=settings.port, reload=settings.reload)


if __name__ == "__main__":
    run_server()

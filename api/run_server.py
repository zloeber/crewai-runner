#!/usr/bin/env python3
"""Simple script to run the CrewAI API for testing."""

import os
import sys
from pathlib import Path

# Add the src/engine directory to Python path
engine_path = Path(__file__).parent / "src" / "engine"
sys.path.insert(0, str(engine_path))

# Set environment variables for testing
os.environ.setdefault("CREWAI_API_KEY", "test-api-key")
os.environ.setdefault("OPENAI_API_KEY", "test-key")
os.environ.setdefault("ANTHROPIC_API_KEY", "test-key")

if __name__ == "__main__":
    import uvicorn

    # Import the app
    from main import app

    print("Starting CrewAI API server for testing...")
    print("API will be available at: http://localhost:8000")
    print("API docs will be available at: http://localhost:8000/api/docs")
    print("\nProfile endpoints:")
    print("- GET /api/profiles - List all profiles")
    print("- POST /api/profiles/load - Load a profile")
    print("- POST /api/profiles/save - Save a profile")
    print("- GET /api/profiles/{name} - Get a specific profile")
    print("- DELETE /api/profiles/{name} - Delete a profile")
    print("- GET /api/profiles/{name}/export - Export profile as YAML")
    print("- POST /api/profiles/import - Import profile from YAML")
    print("\nMCP endpoints:")
    print("- GET /api/mcp/servers - List all MCP servers")
    print("- POST /api/mcp/servers - Register new MCP server")
    print("- GET /api/mcp/tools - List all tools from all servers")

    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        reload=False,  # Disable reload to avoid import issues
        log_level="info",
    )

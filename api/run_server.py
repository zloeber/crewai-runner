#!/usr/bin/env python3
"""Simple script to run the CrewAI API for testing."""

import os
import sys
from pathlib import Path

# Add the src directory to Python path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

# Set environment variables for testing
os.environ.setdefault("CREWAI_API_KEY", "test-api-key")
os.environ.setdefault("OPENAI_API_KEY", "test-key")
os.environ.setdefault("ANTHROPIC_API_KEY", "test-key")

if __name__ == "__main__":
    import uvicorn
    
    # Import the app directly without going through __init__.py
    from engine.main import app
    
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
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        reload=False,  # Disable reload to avoid import issues
        log_level="info"
    )
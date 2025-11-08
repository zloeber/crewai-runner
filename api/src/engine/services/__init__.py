"""Services module for crewai-runner."""

# Import without relative imports to avoid issues
import sys
from pathlib import Path

# Ensure abstractions are importable
engine_path = Path(__file__).parent.parent
if str(engine_path) not in sys.path:
    sys.path.insert(0, str(engine_path))

from services.orchestrator_factory import OrchestratorFactory

__all__ = ["OrchestratorFactory"]

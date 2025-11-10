"""Services module for crewai-runner."""

# Import without relative imports to avoid issues
import sys
from pathlib import Path
from engine.services.orchestrator_factory import OrchestratorFactory

# Ensure abstractions are importable
engine_path = Path(__file__).parent.parent
if str(engine_path) not in sys.path:
    sys.path.insert(0, str(engine_path))


__all__ = ["OrchestratorFactory"]

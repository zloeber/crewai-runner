"""Orchestrator factory for creating framework-specific orchestrators."""

from typing import Dict, Type
from ..abstractions.base_orchestrator import BaseOrchestrator


class OrchestratorFactory:
    """Factory for creating orchestrator instances based on framework type."""

    _orchestrators: Dict[str, Type[BaseOrchestrator]] = {}

    @classmethod
    def register(cls, framework: str, orchestrator_class: Type[BaseOrchestrator]):
        """
        Register an orchestrator class for a specific framework.
        
        Args:
            framework: Framework name (e.g., "crewai", "langgraph")
            orchestrator_class: Orchestrator class to register
        """
        cls._orchestrators[framework.lower()] = orchestrator_class

    @classmethod
    def get_orchestrator(cls, framework: str) -> BaseOrchestrator:
        """
        Get an orchestrator instance for the specified framework.
        
        Args:
            framework: Framework name (e.g., "crewai", "langgraph")
            
        Returns:
            Orchestrator instance
            
        Raises:
            ValueError: If framework is not supported
        """
        framework_lower = framework.lower()
        if framework_lower not in cls._orchestrators:
            raise ValueError(
                f"Framework '{framework}' is not supported. "
                f"Available frameworks: {', '.join(cls._orchestrators.keys())}"
            )
        
        orchestrator_class = cls._orchestrators[framework_lower]
        return orchestrator_class()

    @classmethod
    def get_supported_frameworks(cls) -> list[str]:
        """
        Get list of supported frameworks.
        
        Returns:
            List of framework names
        """
        return list(cls._orchestrators.keys())

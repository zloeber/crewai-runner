"""Base workflow interface for multi-framework support."""

from abc import ABC, abstractmethod
from typing import Any, Dict, List
from .base_agent import BaseAgent


class BaseWorkflow(ABC):
    """Base workflow interface that all framework workflows must implement."""

    @abstractmethod
    def get_name(self) -> str:
        """Get the workflow's name."""
        pass

    @abstractmethod
    def get_description(self) -> str:
        """Get the workflow's description."""
        pass

    @abstractmethod
    def get_agents(self) -> List[BaseAgent]:
        """Get the list of agents in the workflow."""
        pass

    @abstractmethod
    def get_tasks(self) -> List[Dict[str, Any]]:
        """Get the list of tasks in the workflow."""
        pass

    @abstractmethod
    def to_dict(self) -> Dict[str, Any]:
        """Convert workflow to dictionary representation."""
        pass

    @classmethod
    @abstractmethod
    def from_dict(cls, data: Dict[str, Any]) -> "BaseWorkflow":
        """Create workflow from dictionary representation."""
        pass

    @abstractmethod
    def validate(self) -> tuple[bool, List[str]]:
        """
        Validate the workflow configuration.

        Returns:
            Tuple of (is_valid, error_messages)
        """
        pass

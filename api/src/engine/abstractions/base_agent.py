"""Base agent interface for multi-framework support."""

from abc import ABC, abstractmethod
from typing import Any, Dict, List


class BaseAgent(ABC):
    """Base agent interface that all framework agents must implement."""

    @abstractmethod
    def get_name(self) -> str:
        """Get the agent's name."""
        pass

    @abstractmethod
    def get_role(self) -> str:
        """Get the agent's role."""
        pass

    @abstractmethod
    def get_goal(self) -> str:
        """Get the agent's goal."""
        pass

    @abstractmethod
    def get_tools(self) -> List[str]:
        """Get the list of tools available to the agent."""
        pass

    @abstractmethod
    def get_model(self) -> str:
        """Get the LLM model used by the agent."""
        pass

    @abstractmethod
    def to_dict(self) -> Dict[str, Any]:
        """Convert agent to dictionary representation."""
        pass

    @classmethod
    @abstractmethod
    def from_dict(cls, data: Dict[str, Any]) -> "BaseAgent":
        """Create agent from dictionary representation."""
        pass

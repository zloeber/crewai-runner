"""Base orchestrator interface for multi-framework support."""

from abc import ABC, abstractmethod
from typing import Any, Dict, AsyncIterator, Optional


class BaseOrchestrator(ABC):
    """Base orchestrator interface that all framework adapters must implement."""

    @abstractmethod
    async def execute(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a workflow with the given configuration.
        
        Args:
            config: Workflow configuration dictionary
            
        Returns:
            Execution results dictionary
        """
        pass

    @abstractmethod
    async def validate(self, config: Dict[str, Any]) -> tuple[bool, Optional[list[str]]]:
        """
        Validate a workflow configuration.
        
        Args:
            config: Workflow configuration dictionary
            
        Returns:
            Tuple of (is_valid, error_messages)
        """
        pass

    @abstractmethod
    async def stream(self, config: Dict[str, Any]) -> AsyncIterator[Dict[str, Any]]:
        """
        Execute a workflow and stream progress updates.
        
        Args:
            config: Workflow configuration dictionary
            
        Yields:
            Progress update dictionaries
        """
        pass

    @abstractmethod
    async def get_status(self, workflow_id: str) -> Dict[str, Any]:
        """
        Get the current status of a running workflow.
        
        Args:
            workflow_id: Unique workflow identifier
            
        Returns:
            Status dictionary
        """
        pass

    @abstractmethod
    async def stop(self, workflow_id: str) -> bool:
        """
        Stop a running workflow.
        
        Args:
            workflow_id: Unique workflow identifier
            
        Returns:
            True if stopped successfully, False otherwise
        """
        pass

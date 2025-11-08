"""Base tool adapter interface for MCP tool wrapping."""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional


class BaseToolAdapter(ABC):
    """Base tool adapter interface for wrapping MCP tools for different frameworks."""

    @abstractmethod
    def wrap_tool(self, tool_config: Dict[str, Any]) -> Any:
        """
        Wrap an MCP tool for use with the specific framework.
        
        Args:
            tool_config: MCP tool configuration
            
        Returns:
            Framework-specific tool object
        """
        pass

    @abstractmethod
    def wrap_tools(self, tool_configs: List[Dict[str, Any]]) -> List[Any]:
        """
        Wrap multiple MCP tools for use with the specific framework.
        
        Args:
            tool_configs: List of MCP tool configurations
            
        Returns:
            List of framework-specific tool objects
        """
        pass

    @abstractmethod
    def get_tool_names(self) -> List[str]:
        """
        Get the names of all available tools.
        
        Returns:
            List of tool names
        """
        pass

    @abstractmethod
    def get_tool_description(self, tool_name: str) -> Optional[str]:
        """
        Get the description of a specific tool.
        
        Args:
            tool_name: Name of the tool
            
        Returns:
            Tool description or None if not found
        """
        pass

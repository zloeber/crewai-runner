"""CrewAI adapter implementation."""

from typing import Any, Dict, AsyncIterator, Optional
from abstractions.base_orchestrator import BaseOrchestrator
import uuid


class CrewAIAdapter(BaseOrchestrator):
    """Adapter for CrewAI framework."""

    def __init__(self):
        """Initialize CrewAI adapter."""
        self.workflows: Dict[str, Dict[str, Any]] = {}

    async def execute(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a CrewAI workflow.

        Args:
            config: Workflow configuration dictionary

        Returns:
            Execution results dictionary
        """
        workflow_id = str(uuid.uuid4())

        # Store workflow information
        self.workflows[workflow_id] = {
            "config": config,
            "status": "running",
            "progress": 0,
        }

        # TODO: Implement actual CrewAI execution
        # This is a placeholder that simulates workflow execution

        return {
            "workflow_id": workflow_id,
            "status": "started",
            "message": "CrewAI workflow started successfully",
        }

    async def validate(
        self, config: Dict[str, Any]
    ) -> tuple[bool, Optional[list[str]]]:
        """
        Validate a CrewAI workflow configuration.

        Args:
            config: Workflow configuration dictionary

        Returns:
            Tuple of (is_valid, error_messages)
        """
        errors = []

        # Validate required fields
        if "workflow" not in config:
            errors.append("Missing 'workflow' field")
            return False, errors

        workflow = config["workflow"]

        if "agents" not in workflow:
            errors.append("Missing 'agents' field in workflow")
        elif not isinstance(workflow["agents"], list):
            errors.append("'agents' must be a list")
        elif len(workflow["agents"]) == 0:
            errors.append("At least one agent is required")

        if "tasks" not in workflow:
            errors.append("Missing 'tasks' field in workflow")
        elif not isinstance(workflow["tasks"], list):
            errors.append("'tasks' must be a list")
        elif len(workflow["tasks"]) == 0:
            errors.append("At least one task is required")

        # Validate agent fields
        if "agents" in workflow and isinstance(workflow["agents"], list):
            for i, agent in enumerate(workflow["agents"]):
                if not isinstance(agent, dict):
                    errors.append(f"Agent {i} must be a dictionary")
                    continue

                required_agent_fields = ["name", "role", "goal", "backstory", "model"]
                for field in required_agent_fields:
                    if field not in agent:
                        errors.append(f"Agent {i} missing required field: {field}")

        # Validate task fields
        if "tasks" in workflow and isinstance(workflow["tasks"], list):
            agent_names = [
                a.get("name") for a in workflow.get("agents", []) if isinstance(a, dict)
            ]

            for i, task in enumerate(workflow["tasks"]):
                if not isinstance(task, dict):
                    errors.append(f"Task {i} must be a dictionary")
                    continue

                required_task_fields = [
                    "name",
                    "description",
                    "expectedOutput",
                    "agent",
                ]
                for field in required_task_fields:
                    if field not in task:
                        errors.append(f"Task {i} missing required field: {field}")

                # Validate agent reference
                if "agent" in task and task["agent"] not in agent_names:
                    errors.append(f"Task {i} references unknown agent: {task['agent']}")

        return len(errors) == 0, errors if errors else None

    async def stream(self, config: Dict[str, Any]) -> AsyncIterator[Dict[str, Any]]:
        """
        Execute a CrewAI workflow and stream progress updates.

        Args:
            config: Workflow configuration dictionary

        Yields:
            Progress update dictionaries
        """
        result = await self.execute(config)
        workflow_id = result["workflow_id"]

        # TODO: Implement actual streaming
        yield {
            "workflow_id": workflow_id,
            "status": "started",
            "progress": 0,
        }

        yield {
            "workflow_id": workflow_id,
            "status": "completed",
            "progress": 100,
        }

    async def get_status(self, workflow_id: str) -> Dict[str, Any]:
        """
        Get the current status of a CrewAI workflow.

        Args:
            workflow_id: Unique workflow identifier

        Returns:
            Status dictionary
        """
        if workflow_id not in self.workflows:
            return {
                "workflow_id": workflow_id,
                "status": "not_found",
                "error": "Workflow not found",
            }

        workflow = self.workflows[workflow_id]
        return {
            "workflow_id": workflow_id,
            "status": workflow["status"],
            "progress": workflow["progress"],
        }

    async def stop(self, workflow_id: str) -> bool:
        """
        Stop a running CrewAI workflow.

        Args:
            workflow_id: Unique workflow identifier

        Returns:
            True if stopped successfully, False otherwise
        """
        if workflow_id not in self.workflows:
            return False

        self.workflows[workflow_id]["status"] = "stopped"
        return True

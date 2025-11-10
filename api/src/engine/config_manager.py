"""Configuration manager for the CrewAI runner."""

from pathlib import Path
from typing import Optional, List
import yaml
import click
from engine.models import RunnerConfig, CrewConfig, AgentConfig


class ConfigManager:
    """Manages persistent configuration for the CrewAI runner."""

    def __init__(self, config_dir: Optional[Path] = None):
        self.config_dir = config_dir or Path.home() / ".crewai-runner"
        self.config_file = self.config_dir / "config.yaml"
        self.crews_dir = self.config_dir / "crews"

        # Ensure directories exist
        self.config_dir.mkdir(parents=True, exist_ok=True)
        self.crews_dir.mkdir(parents=True, exist_ok=True)

    def load_config(self) -> RunnerConfig:
        """Load the main configuration file."""
        if not self.config_file.exists():
            return self._create_default_config()

        try:
            with open(self.config_file, "r") as f:
                data = yaml.safe_load(f)
            return RunnerConfig(**data)
        except Exception as e:
            click.echo(f"Error loading config: {e}", err=True)
            return self._create_default_config()

    def save_config(self, config: RunnerConfig) -> None:
        """Save the main configuration file."""
        with open(self.config_file, "w") as f:
            yaml.dump(config.model_dump(), f, default_flow_style=False)

    def load_crew(self, name: str) -> Optional[CrewConfig]:
        """Load a specific crew configuration."""
        crew_file = self.crews_dir / f"{name}.yaml"
        if not crew_file.exists():
            return None

        try:
            with open(crew_file, "r") as f:
                data = yaml.safe_load(f)
            return CrewConfig(**data)
        except Exception as e:
            click.echo(f"Error loading crew '{name}': {e}", err=True)
            return None

    def save_crew(self, crew: CrewConfig) -> None:
        """Save a crew configuration."""
        crew_file = self.crews_dir / f"{crew.name}.yaml"
        with open(crew_file, "w") as f:
            yaml.dump(crew.model_dump(), f, default_flow_style=False)

    def list_crews(self) -> List[str]:
        """List all available crew configurations."""
        return [f.stem for f in self.crews_dir.glob("*.yaml")]

    def delete_crew(self, name: str) -> bool:
        """Delete a crew configuration."""
        crew_file = self.crews_dir / f"{name}.yaml"
        if crew_file.exists():
            crew_file.unlink()
            return True
        return False

    def crew_exists(self, name: str) -> bool:
        """Check if a crew configuration exists."""
        crew_file = self.crews_dir / f"{name}.yaml"
        return crew_file.exists()

    def get_config_dir(self) -> Path:
        """Get the configuration directory path."""
        return self.config_dir

    def _create_default_config(self) -> RunnerConfig:
        """Create and save a default configuration."""
        config = RunnerConfig()
        self.save_config(config)
        return config

    def create_example_crew(self) -> CrewConfig:
        """Create an example crew configuration."""
        researcher = AgentConfig(
            name="researcher",
            role="Senior Research Analyst",
            goal="Conduct thorough research on given topics",
            backstory="You are an experienced researcher with expertise in data analysis and information gathering.",
            tools=["search", "web_scraper"],
            max_iter=5,
            verbose=True,
        )

        writer = AgentConfig(
            name="writer",
            role="Content Writer",
            goal="Create engaging content based on research",
            backstory="You are a skilled writer who can transform research into compelling, well-structured content.",
            tools=["text_editor"],
            max_iter=3,
            verbose=True,
        )

        crew = CrewConfig(
            name="research_team",
            description="A team for conducting research and creating content",
            agents=[researcher, writer],
            tasks=[
                {
                    "name": "research_task",
                    "description": "Research the given topic thoroughly",
                    "agent": "researcher",
                    "expected_output": "Comprehensive research report with key findings and sources",
                },
                {
                    "name": "writing_task",
                    "description": "Write an article based on the research findings",
                    "agent": "writer",
                    "expected_output": "Well-written article of 800-1200 words",
                    "context": ["research_task"],
                },
            ],
            process="sequential",
            verbose=True,
        )

        return crew

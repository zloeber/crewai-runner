"""CLI commands for configuration management."""

import click
from pathlib import Path
import yaml
from .config_manager import ConfigManager
from .models import CrewConfig


@click.group()
def config():
    """Manage CrewAI runner configuration."""
    pass


@config.command()
@click.option("--config-dir", type=click.Path(), help="Configuration directory")
def init(config_dir):
    """Initialize configuration directory."""
    manager = ConfigManager(Path(config_dir) if config_dir else None)
    _ = manager.load_config()
    click.echo(f"Configuration initialized at: {manager.config_dir}")
    click.echo(f"Config file: {manager.config_file}")

    # Create an example crew if none exist
    if not manager.list_crews():
        example_crew = manager.create_example_crew()
        manager.save_crew(example_crew)
        click.echo(f"Created example crew: {example_crew.name}")


@config.command("list-crews")
@click.option("--config-dir", type=click.Path(), help="Configuration directory")
def list_crews(config_dir):
    """List all available crews."""
    manager = ConfigManager(Path(config_dir) if config_dir else None)
    crews = manager.list_crews()
    if crews:
        click.echo("Available crews:")
        for crew in crews:
            click.echo(f"  - {crew}")
    else:
        click.echo("No crews configured.")
        click.echo("Run 'crewai-runner-api config init' to create an example crew.")


@config.command("show-crew")
@click.argument("name")
@click.option("--config-dir", type=click.Path(), help="Configuration directory")
def show_crew(name, config_dir):
    """Show details of a specific crew."""
    manager = ConfigManager(Path(config_dir) if config_dir else None)
    crew = manager.load_crew(name)
    if crew:
        click.echo(f"Crew: {crew.name}")
        click.echo(f"Description: {crew.description}")
        click.echo(f"Process: {crew.process}")
        click.echo(f"Agents ({len(crew.agents)}):")
        for agent in crew.agents:
            click.echo(f"  - {agent.name}: {agent.role}")
            click.echo(f"    Goal: {agent.goal}")
            if agent.tools:
                click.echo(f"    Tools: {', '.join(agent.tools)}")
        click.echo(f"Tasks ({len(crew.tasks)}):")
        for i, task in enumerate(crew.tasks, 1):
            click.echo(f"  {i}. {task.get('name', 'Unnamed Task')}")
            click.echo(f"     Description: {task.get('description', 'No description')}")
            click.echo(f"     Agent: {task.get('agent', 'No agent assigned')}")
    else:
        click.echo(f"Crew '{name}' not found.")


@config.command("delete-crew")
@click.argument("name")
@click.option("--config-dir", type=click.Path(), help="Configuration directory")
@click.confirmation_option(prompt="Are you sure you want to delete this crew?")
def delete_crew(name, config_dir):
    """Delete a crew configuration."""
    manager = ConfigManager(Path(config_dir) if config_dir else None)
    if manager.delete_crew(name):
        click.echo(f"Crew '{name}' deleted successfully.")
    else:
        click.echo(f"Crew '{name}' not found.")


@config.command("show-config")
@click.option("--config-dir", type=click.Path(), help="Configuration directory")
def show_config(config_dir):
    """Show current configuration."""
    manager = ConfigManager(Path(config_dir) if config_dir else None)
    _ = manager.load_config()

    click.echo("Current Configuration:")
    click.echo(f"Config Directory: {manager.config_dir}")
    click.echo(f"API Host: {config.api.host}")
    click.echo(f"API Port: {config.api.port}")
    click.echo(f"Debug Mode: {config.api.debug}")
    click.echo(f"CORS Origins: {', '.join(config.api.cors_origins)}")
    click.echo(f"Default Crew: {config.default_crew or 'None'}")
    click.echo(f"Config Version: {config.config_version}")


@config.command("export-crew")
@click.argument("name")
@click.option("--output", "-o", type=click.Path(), help="Output file path")
@click.option("--config-dir", type=click.Path(), help="Configuration directory")
def export_crew(name, output, config_dir):
    """Export a crew configuration to a file."""
    manager = ConfigManager(Path(config_dir) if config_dir else None)
    crew = manager.load_crew(name)
    if not crew:
        click.echo(f"Crew '{name}' not found.")
        return

    output_path = Path(output) if output else Path(f"{name}.yaml")

    with open(output_path, "w") as f:
        yaml.dump(crew.model_dump(), f, default_flow_style=False)

    click.echo(f"Crew '{name}' exported to {output_path}")


@config.command("import-crew")
@click.argument("file_path", type=click.Path(exists=True))
@click.option("--config-dir", type=click.Path(), help="Configuration directory")
def import_crew(file_path, config_dir):
    """Import a crew configuration from a file."""
    manager = ConfigManager(Path(config_dir) if config_dir else None)

    try:
        with open(file_path, "r") as f:
            data = yaml.safe_load(f)

        crew = CrewConfig(**data)

        if manager.crew_exists(crew.name):
            if not click.confirm(f"Crew '{crew.name}' already exists. Overwrite?"):
                click.echo("Import cancelled.")
                return

        manager.save_crew(crew)
        click.echo(f"Crew '{crew.name}' imported successfully.")

    except Exception as e:
        click.echo(f"Error importing crew: {e}", err=True)


if __name__ == "__main__":
    config()

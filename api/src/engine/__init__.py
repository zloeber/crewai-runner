"""CrewAI Runner API Package."""

import os
import pathlib
import click

# from .main import run_server
from .cli import config

# from main import app

# __all__ = ["app"]


@click.group()
def main():
    """CrewAI Runner API - A FastAPI wrapper for CrewAI with configuration management."""
    pass


@main.command()
@click.option("--host", default="0.0.0.0", help="Host to bind to")
@click.option("--port", default=8000, help="Port to bind to")
@click.option("--reload", is_flag=True, help="Enable auto-reload")
def serve(host, port, reload):
    """Start the API server."""
    import uvicorn
    from .config import settings

    # Override settings if provided
    settings.host = host
    settings.port = port
    settings.reload = reload

    uvicorn.run("src.engine.main:app", host=host, port=port, reload=reload)


# Add the config subcommand
main.add_command(config)


"""
Compute the version number and store it in the `__version__` variable.

Based on <https://github.com/maresb/hatch-vcs-footgun-example>.
"""


def _get_hatch_version():
    """Compute the most up-to-date version number in a development environment.

    Returns `None` if Hatchling is not installed, e.g. in a production environment.

    For more details, see <https://github.com/maresb/hatch-vcs-footgun-example/>.
    """
    import os

    try:
        from hatchling.metadata.core import ProjectMetadata
        from hatchling.plugin.manager import PluginManager
        from hatchling.utils.fs import locate_file
    except ImportError:
        # Hatchling is not installed, so probably we are not in
        # a development environment.
        return None

    pyproject_toml = locate_file(__file__, "pyproject.toml")
    if pyproject_toml is None:
        raise RuntimeError("pyproject.toml not found although hatchling is installed")
    root = os.path.dirname(pyproject_toml)
    metadata = ProjectMetadata(root=root, plugin_manager=PluginManager())
    # Version can be either statically set in pyproject.toml or computed dynamically:
    return metadata.core.version or metadata.hatch.version.cached


def _get_importlib_metadata_version():
    """Compute the version number using importlib.metadata.

    This is the official Pythonic way to get the version number of an installed
    package. However, it is only updated when a package is installed. Thus, if a
    package is installed in editable mode, and a different version is checked out,
    then the version number will not be updated.
    """
    from importlib.metadata import version

    __version__ = version(__package__)
    return __version__


SCRIPT_PATH = pathlib.Path(__file__).parent.resolve()
CONFIG_PATH = os.getenv(
    "TERRAFORM_INGEST_CONFIG",
    pathlib.Path().joinpath(pathlib.Path().resolve(), ("config.yaml")),
)

__version__ = _get_hatch_version() or "0.1.0-dev"

# Instructions for crewai-runner

## Rules
- Before running any command, check the current terminal context and use that same terminal ID for all subsequent commands.
- All documentation created must be created in the ./docs folder and should be added to the ./mkdocs.yml file for inclusion in the site.
- When you need to use the `run_in_terminal` tool always use isBackground=false.
- Do not run multiple line python commands in a single execution, instead create temporary scripts if needed and run them as single commands.
- **Always run tests and linting** before committing changes to ensure code quality.
- Use `uv` package manager instead of `pip` for dependency management.
- Do not create comprehensive documentation when finished resolving an issue or implementing a feature unless explicitly told to do so.

## Code Style Guidelines
- Follow PEP 8 style guide
- Use snake_case for variables and functions
- Use PascalCase for classes
- Include docstrings for functions and classes
- Use type hints where appropriate
- Use f-strings for string formatting
- Use `pathlib.Path` for file system operations
- Use `click` for CLI commands and options
- Use `pydantic` for data models and validation
- All imports should be at the top of the file, grouped by standard library, third-party, and local imports
- Using global variables should always be a last resort approved by the user

## Development Workflows

### Setup & Testing
```bash
uv sync                    # Install dependencies (uses uv, not pip)
python -m pytest          # Run tests
python -m terraform_ingest.cli --help  # CLI access
```

## Linting & Formatting
```bash
# Check formatting (required before commit)
uv run black --check src
uv run ruff format --check src

# Auto-fix formatting (required before commit)
uv run black src/
uv run ruff format src/

# Linting with ruff (required before commit)
uv run ruff check src/
uv run ruff check --fix src/
```

## Build & Distribution
```bash
# Build package
uv build

# Install in development mode
uv sync

# Install with specific extras
uv pip install -e ".[test]"    # Test dependencies
uv pip install -e ".[dev]"     # Dev dependencies (ruff, black, mypy)
uv pip install -e ".[docs]"    # Documentation dependencies
```

## Dependency Management
```bash
# Add a new dependency (automatically updates pyproject.toml)
uv add <package-name>

# Add a dev dependency
uv add --dev <package-name>

# Update all dependencies
uv sync --upgrade

# Lock dependencies
uv lock

# Remove a dependency
uv remove <package-name>
```

**Important:** After adding dependencies:
1. Run `uv sync` to install them
2. Run tests to ensure compatibility
3. Commit both `pyproject.toml` and `uv.lock` files

## Environment Variables
- `TERRAFORM_INGEST_OUTPUT_DIR`: Default output directory for JSON summaries (default: `./output`)
- Git credentials automatically detected from system for private repositories
- No required environment variables for basic operation

## Common Tasks
```bash
# Run all tests
task test

# Run linting
task lint

# Auto-fix linting issues
task lint:fix

# Format code
task format

# Build documentation
task docs

# Clean build artifacts
task clean

# Install dependencies
task install
```

## Troubleshooting
- **Import errors**: Run `uv sync` to ensure all dependencies are installed
- **Git authentication**: Ensure SSH keys or credential helpers are configured
- **Test failures**: Check if git is available on PATH for repository tests
- **Module not found**: Verify you're running commands from project root with activated venv

## Git Workflow
- Branch naming: `feature/description`, `fix/description`, `docs/description`
- Commit messages: Use conventional commits (feat:, fix:, docs:, test:, chore:)
- Pre-commit: Ensure tests pass and code is formatted
- PRs: Include tests for new features, update documentation as needed
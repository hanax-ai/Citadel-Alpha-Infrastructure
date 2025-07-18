"""
Main CLI Entry Point

Command-line interface for HXP Vector Database following HXP Governance Coding Standards.
Implements Single Responsibility Principle for CLI coordination.

Author: Citadel AI Team
License: MIT
"""

import typer
from typing import Optional
import logging
from pathlib import Path

from hana_x_vector.cli.commands.database import database_app
from hana_x_vector.cli.commands.migration import migration_app
from hana_x_vector.cli.commands.health import health_app
from hana_x_vector.cli.commands.models import models_app
from hana_x_vector.cli.formatters.output import OutputFormatter
from hana_x_vector.utils.logging import setup_logging

# Create main CLI application
app = typer.Typer(
    name="hana-x-vector",
    help="HANA-X Vector Database CLI - Unified API Gateway & External Model Integration",
    add_completion=False,
    rich_markup_mode="rich"
)

# Add sub-applications
app.add_typer(database_app, name="db", help="Database operations")
app.add_typer(migration_app, name="migrate", help="Migration operations")
app.add_typer(health_app, name="health", help="Health monitoring")
app.add_typer(models_app, name="models", help="Model management")

# Global options
@app.callback()
def main(
    ctx: typer.Context,
    config: Optional[Path] = typer.Option(
        None,
        "--config",
        "-c",
        help="Configuration file path",
        exists=True,
        file_okay=True,
        dir_okay=False,
        readable=True
    ),
    verbose: bool = typer.Option(
        False,
        "--verbose",
        "-v",
        help="Enable verbose logging"
    ),
    debug: bool = typer.Option(
        False,
        "--debug",
        "-d",
        help="Enable debug mode"
    ),
    output_format: str = typer.Option(
        "table",
        "--format",
        "-f",
        help="Output format (table, json, yaml)",
        case_sensitive=False
    )
):
    """
    HANA-X Vector Database CLI
    
    Unified command-line interface for vector database operations,
    API Gateway management, and external model integration.
    """
    # Setup logging
    log_level = "DEBUG" if debug else ("INFO" if verbose else "WARNING")
    setup_logging({"logging": {"level": log_level}})
    
    # Store global context
    ctx.ensure_object(dict)
    ctx.obj["config_path"] = config
    ctx.obj["verbose"] = verbose
    ctx.obj["debug"] = debug
    ctx.obj["output_format"] = output_format
    
    # Initialize output formatter
    ctx.obj["formatter"] = OutputFormatter(output_format)


@app.command()
def version():
    """Show version information."""
    from hana_x_vector import __version__, __author__
    
    typer.echo(f"HANA-X Vector Database CLI v{__version__}")
    typer.echo(f"Author: {__author__}")
    typer.echo("License: MIT")


@app.command()
def init(
    config_path: Optional[Path] = typer.Option(
        Path("config.yaml"),
        "--config",
        "-c",
        help="Configuration file path to create"
    ),
    force: bool = typer.Option(
        False,
        "--force",
        help="Overwrite existing configuration"
    )
):
    """Initialize HXP Vector Database configuration."""
    try:
        from hana_x_vector.utils.config import create_default_config, save_config
        
        # Check if config already exists
        if config_path.exists() and not force:
            typer.echo(
                f"Configuration file already exists: {config_path}",
                err=True
            )
            typer.echo("Use --force to overwrite", err=True)
            raise typer.Exit(1)
        
        # Create default configuration
        config = create_default_config()
        
        # Save configuration
        save_config(config, config_path)
        
        typer.echo(f"✅ Configuration initialized: {config_path}")
        typer.echo("Edit the configuration file to customize settings")
        
    except Exception as e:
        typer.echo(f"❌ Failed to initialize configuration: {e}", err=True)
        raise typer.Exit(1)


@app.command()
def validate_config(
    config_path: Optional[Path] = typer.Option(
        Path("config.yaml"),
        "--config",
        "-c",
        help="Configuration file path to validate",
        exists=True,
        file_okay=True,
        dir_okay=False,
        readable=True
    )
):
    """Validate configuration file."""
    try:
        from hana_x_vector.utils.config import load_config
        
        # Load and validate configuration
        config = load_config(config_path)
        
        typer.echo(f"✅ Configuration is valid: {config_path}")
        typer.echo(f"Environment: {config.environment}")
        typer.echo(f"Debug mode: {config.debug}")
        typer.echo(f"Database: {config.get_database_url()}")
        
    except Exception as e:
        typer.echo(f"❌ Configuration validation failed: {e}", err=True)
        raise typer.Exit(1)


@app.command()
def status(
    ctx: typer.Context,
    config_path: Optional[Path] = typer.Option(
        None,
        "--config",
        "-c",
        help="Configuration file path",
        exists=True,
        file_okay=True,
        dir_okay=False,
        readable=True
    )
):
    """Show system status overview."""
    try:
        from hana_x_vector.utils.config import load_config, create_default_config
        from hana_x_vector import VectorDatabase, APIGateway
        
        # Load configuration
        if config_path:
            config = load_config(config_path)
        else:
            config = create_default_config()
        
        # Get formatter
        formatter = ctx.obj["formatter"]
        
        # System status data
        status_data = {
            "Configuration": {
                "File": str(config_path) if config_path else "Default",
                "Environment": config.environment,
                "Debug": config.debug
            },
            "Database": {
                "Host": config.database.host,
                "Port": config.database.port,
                "URL": config.get_database_url()
            },
            "API Gateway": {
                "REST Port": config.api_gateway.rest_port,
                "GraphQL Port": config.api_gateway.graphql_port,
                "gRPC Port": config.api_gateway.grpc_port
            },
            "Cache": {
                "Enabled": config.cache.enabled,
                "Redis URL": config.cache.redis_url if config.cache.enabled else "Disabled"
            }
        }
        
        # Format and display
        formatter.display_nested_dict(status_data, title="System Status")
        
    except Exception as e:
        typer.echo(f"❌ Failed to get system status: {e}", err=True)
        raise typer.Exit(1)


if __name__ == "__main__":
    app()

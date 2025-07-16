"""
Migration CLI Commands

CLI commands for database migration management.
Implements Single Responsibility Principle for migration operations.

Author: Citadel AI Team
License: MIT
"""

import asyncio
from typing import Optional, List
import typer
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich import print as rprint
from datetime import datetime

from hana_x_vector.migration import (
    MigrationManager, CollectionMigration, IndexMigration, MigrationStatus
)
from hana_x_vector.utils.logging import get_logger
from hana_x_vector.utils.config import get_config

# Create CLI app
migration_app = typer.Typer(
    name="migration",
    help="Database migration management commands",
    no_args_is_help=True
)

console = Console()
logger = get_logger(__name__)


def get_migration_manager():
    """Get migration manager instance."""
    # This would be initialized with actual vector_db instance
    # For now, return mock manager
    return MigrationManager(vector_db=None)


@migration_app.command("status")
def migration_status():
    """Show migration status."""
    try:
        async def _status():
            manager = get_migration_manager()
            status = await manager.get_migration_status()
            
            # Create status table
            table = Table(title="Migration Status", show_header=True)
            table.add_column("Metric", style="cyan")
            table.add_column("Value", style="green")
            
            table.add_row("Total Migrations", str(status.get("total_migrations", 0)))
            
            # Add status counts
            status_counts = status.get("status_counts", {})
            for status_name, count in status_counts.items():
                table.add_row(f"{status_name.title()} Migrations", str(count))
            
            # Add pending migrations
            pending = status.get("pending_migrations", [])
            table.add_row("Pending Migrations", str(len(pending)))
            
            # Add latest migration
            latest = status.get("latest_migration")
            table.add_row("Latest Migration", latest or "None")
            
            console.print(table)
            
            # Show pending migrations if any
            if pending:
                console.print("\n[yellow]Pending Migrations:[/yellow]")
                for migration in pending:
                    console.print(f"  • {migration}")
        
        asyncio.run(_status())
        
    except Exception as e:
        console.print(f"[red]Error getting migration status: {e}[/red]")
        raise typer.Exit(1)


@migration_app.command("history")
def migration_history(
    limit: int = typer.Option(10, "--limit", "-l", help="Number of records to show")
):
    """Show migration history."""
    try:
        async def _history():
            manager = get_migration_manager()
            history = await manager.get_migration_history()
            
            if not history:
                console.print("[yellow]No migration history found[/yellow]")
                return
            
            # Create history table
            table = Table(title="Migration History", show_header=True)
            table.add_column("Version", style="cyan")
            table.add_column("Description", style="white")
            table.add_column("Status", style="green")
            table.add_column("Executed At", style="blue")
            table.add_column("Duration (ms)", style="magenta")
            
            # Show limited records
            for record in history[:limit]:
                status_color = {
                    "completed": "green",
                    "failed": "red",
                    "rolled_back": "yellow",
                    "running": "blue"
                }.get(record["status"], "white")
                
                duration = str(record.get("execution_time_ms", "N/A"))
                if duration != "N/A":
                    duration = f"{float(duration):.2f}"
                
                table.add_row(
                    record["version"],
                    record["description"][:50] + "..." if len(record["description"]) > 50 else record["description"],
                    f"[{status_color}]{record['status']}[/{status_color}]",
                    datetime.fromisoformat(record["executed_at"]).strftime("%Y-%m-%d %H:%M:%S"),
                    duration
                )
            
            console.print(table)
            
            if len(history) > limit:
                console.print(f"\n[dim]Showing {limit} of {len(history)} records. Use --limit to show more.[/dim]")
        
        asyncio.run(_history())
        
    except Exception as e:
        console.print(f"[red]Error getting migration history: {e}[/red]")
        raise typer.Exit(1)


@migration_app.command("up")
def migrate_up(
    target_version: Optional[str] = typer.Argument(None, help="Target migration version"),
    dry_run: bool = typer.Option(False, "--dry-run", help="Show what would be executed without running")
):
    """Run forward migrations."""
    try:
        async def _migrate_up():
            manager = get_migration_manager()
            
            if dry_run:
                console.print("[yellow]DRY RUN: The following migrations would be executed:[/yellow]")
                # This would show the migration plan
                console.print("  • Mock migration plan")
                return
            
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=console
            ) as progress:
                task = progress.add_task("Running migrations...", total=None)
                
                result = await manager.migrate_up(target_version)
                
                progress.update(task, completed=True)
            
            if result["status"] == "success":
                console.print(f"[green]✓ {result['message']}[/green]")
                
                executed = result.get("executed_migrations", [])
                if executed:
                    console.print("\n[green]Executed migrations:[/green]")
                    for migration in executed:
                        console.print(f"  • {migration}")
            else:
                console.print(f"[red]✗ Migration failed: {result['message']}[/red]")
                raise typer.Exit(1)
        
        asyncio.run(_migrate_up())
        
    except Exception as e:
        console.print(f"[red]Error running migrations: {e}[/red]")
        raise typer.Exit(1)


@migration_app.command("down")
def migrate_down(
    target_version: str = typer.Argument(..., help="Target migration version to rollback to"),
    confirm: bool = typer.Option(False, "--confirm", help="Skip confirmation prompt")
):
    """Rollback migrations."""
    try:
        if not confirm:
            confirmed = typer.confirm(
                f"Are you sure you want to rollback to version {target_version}? This action cannot be undone."
            )
            if not confirmed:
                console.print("[yellow]Rollback cancelled[/yellow]")
                return
        
        async def _migrate_down():
            manager = get_migration_manager()
            
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=console
            ) as progress:
                task = progress.add_task("Rolling back migrations...", total=None)
                
                result = await manager.migrate_down(target_version)
                
                progress.update(task, completed=True)
            
            if result["status"] == "success":
                console.print(f"[green]✓ {result['message']}[/green]")
                
                rolled_back = result.get("rolled_back_migrations", [])
                if rolled_back:
                    console.print("\n[green]Rolled back migrations:[/green]")
                    for migration in rolled_back:
                        console.print(f"  • {migration}")
            else:
                console.print(f"[red]✗ Rollback failed: {result['message']}[/red]")
                raise typer.Exit(1)
        
        asyncio.run(_migrate_down())
        
    except Exception as e:
        console.print(f"[red]Error rolling back migrations: {e}[/red]")
        raise typer.Exit(1)


@migration_app.command("validate")
def validate_migrations():
    """Validate all registered migrations."""
    try:
        async def _validate():
            manager = get_migration_manager()
            
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=console
            ) as progress:
                task = progress.add_task("Validating migrations...", total=None)
                
                result = await manager.validate_migrations()
                
                progress.update(task, completed=True)
            
            if result.get("all_valid", False):
                console.print("[green]✓ All migrations are valid[/green]")
            else:
                console.print("[red]✗ Some migrations failed validation[/red]")
            
            # Show validation results
            validations = result.get("validations", {})
            if validations:
                table = Table(title="Validation Results", show_header=True)
                table.add_column("Version", style="cyan")
                table.add_column("Description", style="white")
                table.add_column("Status", style="green")
                table.add_column("Dependencies", style="blue")
                
                for version, validation in validations.items():
                    status = "✓ Valid" if validation["valid"] else "✗ Invalid"
                    status_color = "green" if validation["valid"] else "red"
                    
                    dependencies = ", ".join(validation.get("dependencies", []))
                    if not dependencies:
                        dependencies = "None"
                    
                    table.add_row(
                        version,
                        validation["description"][:40] + "..." if len(validation["description"]) > 40 else validation["description"],
                        f"[{status_color}]{status}[/{status_color}]",
                        dependencies
                    )
                
                console.print(table)
        
        asyncio.run(_validate())
        
    except Exception as e:
        console.print(f"[red]Error validating migrations: {e}[/red]")
        raise typer.Exit(1)


@migration_app.command("create")
def create_migration(
    name: str = typer.Argument(..., help="Migration name"),
    migration_type: str = typer.Option("collection", "--type", "-t", help="Migration type (collection, index)"),
    collection_name: Optional[str] = typer.Option(None, "--collection", help="Collection name"),
    dimension: Optional[int] = typer.Option(None, "--dimension", help="Vector dimension"),
    description: Optional[str] = typer.Option(None, "--description", help="Migration description")
):
    """Create a new migration."""
    try:
        # Generate version (timestamp-based)
        version = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Create migration based on type
        if migration_type == "collection":
            if not collection_name or not dimension:
                console.print("[red]Collection migrations require --collection and --dimension[/red]")
                raise typer.Exit(1)
            
            migration = CollectionMigration(
                version=version,
                description=description or f"Create collection {collection_name}",
                collection_name=collection_name,
                dimension=dimension
            )
        elif migration_type == "index":
            if not collection_name:
                console.print("[red]Index migrations require --collection[/red]")
                raise typer.Exit(1)
            
            migration = IndexMigration(
                version=version,
                description=description or f"Create index for {collection_name}",
                collection_name=collection_name,
                index_config={}
            )
        else:
            console.print(f"[red]Unknown migration type: {migration_type}[/red]")
            raise typer.Exit(1)
        
        # Register migration (this would be saved to file in real implementation)
        manager = get_migration_manager()
        manager.register_migration(migration)
        
        console.print(f"[green]✓ Created migration: {version}[/green]")
        console.print(f"  Name: {name}")
        console.print(f"  Type: {migration_type}")
        console.print(f"  Description: {migration.description}")
        
    except Exception as e:
        console.print(f"[red]Error creating migration: {e}[/red]")
        raise typer.Exit(1)


@migration_app.command("reset")
def reset_migrations(
    confirm: bool = typer.Option(False, "--confirm", help="Skip confirmation prompt")
):
    """Reset all migration records (use with caution)."""
    try:
        if not confirm:
            console.print("[red]⚠️  WARNING: This will reset all migration records![/red]")
            console.print("This action cannot be undone and may cause data inconsistency.")
            
            confirmed = typer.confirm("Are you absolutely sure you want to proceed?")
            if not confirmed:
                console.print("[yellow]Reset cancelled[/yellow]")
                return
        
        async def _reset():
            manager = get_migration_manager()
            
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=console
            ) as progress:
                task = progress.add_task("Resetting migrations...", total=None)
                
                result = await manager.reset_migrations()
                
                progress.update(task, completed=True)
            
            if result["status"] == "success":
                console.print(f"[green]✓ {result['message']}[/green]")
            else:
                console.print(f"[red]✗ Reset failed: {result['message']}[/red]")
                raise typer.Exit(1)
        
        asyncio.run(_reset())
        
    except Exception as e:
        console.print(f"[red]Error resetting migrations: {e}[/red]")
        raise typer.Exit(1)


@migration_app.command("info")
def migration_info(
    version: str = typer.Argument(..., help="Migration version")
):
    """Show detailed information about a migration."""
    try:
        manager = get_migration_manager()
        
        # Get migration info (this would query the actual migration)
        console.print(f"[cyan]Migration Information: {version}[/cyan]")
        
        # Mock migration info
        panel_content = f"""
[bold]Version:[/bold] {version}
[bold]Description:[/bold] Sample migration description
[bold]Status:[/bold] [green]Completed[/green]
[bold]Dependencies:[/bold] None
[bold]Executed At:[/bold] 2025-07-15 16:30:00
[bold]Execution Time:[/bold] 150.5 ms
[bold]Checksum:[/bold] abc123def456
        """
        
        console.print(Panel(panel_content.strip(), title="Migration Details"))
        
    except Exception as e:
        console.print(f"[red]Error getting migration info: {e}[/red]")
        raise typer.Exit(1)


# Export the migration app
__all__ = ["migration_app"]

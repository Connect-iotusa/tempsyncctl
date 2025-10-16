from pathlib import Path
import json
import typer
from typing import Optional
from pydantic import BaseModel, ValidationError
from rich import print as rprint
from rich.table import Table

app = typer.Typer(help="TempSync control CLI")

__version__ = "0.1.0"

class Config(BaseModel):
    site: str
    units: int
    thermostats: int
    api_base: str
    api_token: str

def load_config(path: Path) -> dict:
    if not path.exists():
        typer.echo(f"Config not found: {path}", err=True)
        raise typer.Exit(1)
    return json.loads(path.read_text(encoding="utf-8-sig"))

@app.command()
def version():
    """Print CLI version."""
    typer.echo(__version__)

@app.command()
def summary(path: Path = typer.Option(Path("config.json"), "--path", "-p", help="Path to config.json")):
    """Print a neat summary table of the config."""
    data = load_config(path)
    table = Table(title="TempSync Configuration")
    table.add_column("Key")
    table.add_column("Value")
    for k in ["site", "units", "thermostats", "api_base"]:
        table.add_row(k, str(data.get(k)))
    masked = ("*" * 8) if data.get("api_token") else ""
    table.add_row("api_token", masked)
    rprint(table)

@app.command()
def validate(path: Path = typer.Option(Path("config.json"), "--path", "-p", help="Path to config.json")):
    """Validate required keys and types."""
    data = load_config(path)
    try:
        Config(**data)
        rprint("[green]Config is valid[/green]")
    except ValidationError as e:
        rprint("[red]Config validation failed[/red]")
        for err in e.errors():
            rprint(f"- {err['loc']}: {err['msg']}")
        raise typer.Exit(2)

if __name__ == "__main__":
    app()


from pathlib import Path
import json`nimport os
import typer
from typing import Optional
from pydantic import BaseModel, ValidationError
from rich import print as rprint
from rich.table import Table`nfrom dotenv import load_dotenv

app = typer.Typer(help="TempSync control CLI")

__version__ = "0.1.0"

class Config(BaseModel):
    site: str
    units: int
    thermostats: int
    api_base: str
    api_token: str

def load_config(path: Path) -> dict:
    load_dotenv()  # read .env if present
    data = json.loads(path.read_text(encoding="utf-8-sig"))
    # env fallback for api_token
    if not data.get("api_token"):
        env_token = os.getenv("TEMPSYNC_API_TOKEN")
        if env_token:
            data["api_token"] = env_token
    return data

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


@app.command()
def schema():
    """Print required keys and types."""
    table = Table(title="TempSync Config Schema")
    table.add_column("Key"); table.add_column("Type"); table.add_column("Notes")
    table.add_row("site", "str", "")
    table.add_row("units", "int", "Total unit count")
    table.add_row("thermostats", "int", "Managed thermostats")
    table.add_row("api_base", "str", "Base URL, e.g. https://api.connect-iot.ai/tempsync")
    table.add_row("api_token", "str", "Read from config or TEMPSYNC_API_TOKEN")
    rprint(table)

@app.command()
def init(path: Path = Path("config.json")):
    """Create a starter config.json if it doesn't exist."""
    if path.exists():
        typer.echo(f"{path} already exists."); raise typer.Exit(0)
    sample = {
        "site": "Embassy Row",
        "units": 240,
        "thermostats": 180,
        "api_base": "https://api.connect-iot.ai/tempsync",
        "api_token": ""
    }
    path.write_text(json.dumps(sample, indent=2), encoding="utf-8")
    typer.echo(f"Wrote {path}. Set api_token or define TEMPSYNC_API_TOKEN in .env")

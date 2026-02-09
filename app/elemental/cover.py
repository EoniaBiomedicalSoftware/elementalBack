import typer
from .settings.state import get_settings


def get_cover(runtime: str) -> None:
    settings = get_settings()
    app = settings.application

    typer.echo("")
    typer.secho(f" ● {app.app_name.upper()}", fg=typer.colors.CYAN, bold=True, nl=False)
    typer.secho(f" ({app.app_version})", fg=typer.colors.BLACK)
    typer.secho(" " + "─" * 40, fg=typer.colors.BLACK)

    _print_minimal("Mode", runtime.upper(), typer.colors.MAGENTA)
    _print_minimal("Env", app.app_env.upper(), typer.colors.YELLOW)

    status_color = typer.colors.RED if app.debug else typer.colors.GREEN
    _print_minimal("Debug", "ENABLED" if app.debug else "DISABLED", status_color)

    if runtime == 'web':
        protocol = "https" if getattr(app, 'ssl_enabled', False) else "http"
        url = f"{protocol}://{app.host}:{app.port}"

        typer.echo("")
        _print_minimal("URL", url, typer.colors.CYAN)
        if app.debug:
            _print_minimal("Docs", f"{url}/docs", typer.colors.BLUE)

    typer.secho(" " + "─" * 40, fg=typer.colors.BLACK)
    typer.echo("")


def _print_minimal(label: str, value: str, color: str):
    """Prints a clean, indented line."""
    typer.secho(f"   {label:<8}", fg=typer.colors.BLACK, nl=False)
    typer.secho(f" {value}", fg=color, bold=True)
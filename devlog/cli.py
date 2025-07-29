import typer

from datetime import datetime
from pathlib import Path
from .session import Session
from .logger import Logger

app = typer.Typer()

DATA_DIR = Path.home() / ".devlog" / "sessions"
CURRENT = DATA_DIR.parent / "current.json"


@app.command()
def start() -> None:
    """
    Start a session.
    """
    session = Session.start_new(DATA_DIR)
    CURRENT.write_text(str(session.json_path))
    typer.echo(f"✅ Session started: {session.id}")


@app.command()
def note(message: str) -> None:
    """
    Add a note to the active session.

    :param message: The note the user want to log.
    :type message: str
    """
    path = Path(CURRENT.read_text())
    session = Session.load(path)
    Logger(session).note(message)
    typer.echo("📝 Note recorded.")


@app.command()
def stop() -> None:
    """
    Stop an active session.
    """
    path = Path(CURRENT.read_text())
    session = Session.load(path)
    session.stop()
    session.save()
    CURRENT.unlink()
    typer.echo("✅ Session ended.")


@app.command()
def export(format: str) -> None:
    """
    Export logs to markdwon, html, etc.

    :param format: The format the user want to export the logs.
    :type format: str
    """
    # TODO: Find a better way to export files
    today_file = DATA_DIR / f"{datetime.now().strftime('%Y-%m-%d')}.json"
    session = Session.load(Path(today_file))
    session.save()
    if format == "md":
        session.export_markdown()
        typer.echo(f"🚀 Log exported to {session.md_path}")


if __name__ == "__main__":
    app()

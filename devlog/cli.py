import typer
import webbrowser

from datetime import datetime
from pathlib import Path

from .session import Session
from .logger import Logger
from .export import Export


app = typer.Typer()

DATA_DIR = Path.home() / ".devlog" / "sessions"
CURRENT = DATA_DIR.parent / "current.json"


@app.command()
def start() -> None:
    """
    Start a session.
    """
    if CURRENT.exists():
        typer.echo("[DEVLOG] session already in progress.")
    else:
        session = Session.start_new(DATA_DIR)
        CURRENT.write_text(str(session.json_path))
        typer.echo(f"[DEVLOG] ✅ Session started: {session.id}")


@app.command()
def note(message: str) -> None:
    """
    Add a note to the active session.

    :param message: The note the user want to log.
    :type message: str
    """
    if CURRENT.exists():
        path = Path(CURRENT.read_text())
        session = Session.load(path)
        Logger(session).note(message)
        typer.echo("[LOG]📝 Note recorded.")
    else:
        # TODO: Find better way to handle unactive session
        # to avoid repetitive logs like the one below from
        # start, note, stop, etc
        typer.echo("[DEVLOG] No current session active.")


@app.command()
def stop() -> None:
    """
    Stop an active session.
    """
    if CURRENT.exists():
        path = Path(CURRENT.read_text())
        session = Session.load(path)
        session.stop()
        session.save()
        CURRENT.unlink()
        typer.echo("[DEVLOG] ✅ Session ended.")
    else:
        typer.echo("[DEVLOG] No current session active.")


@app.command()
def export(format: str) -> None:
    """
    Export logs to markdwon, html, etc.

    :param format: The format the user want to export the logs.
    :type format: str
    """
    # TODO: Find a better way to export files
    today_file = DATA_DIR / f"{datetime.now().strftime('%Y-%m-%d')}.json"
    session = Export(today_file)
    if CURRENT.exists():
        typer.echo("[DEVLOG] Session active. Stop it before exporting.")
    else:
        if format == "md":
            session.export_markdown()
            typer.echo(f"[LOG] 🚀 Log exported to {session.md_path}")

        if format == "html":
            session.export_html(Path("devlog/dashboard/index.html"),)
            typer.echo(f"[LOG] ✅ Data moved to HTML: {session.html_path}")


@app.command()
def dashboard():
    html_path = Path(DATA_DIR / "index.html")
    if html_path.exists():
        webbrowser.open(html_path.as_uri())
        typer.echo(f"[DEVLOG] Dashboard opened from {html_path}")
    else:
        typer.echo(f"{html_path} does not exists.")


if __name__ == "__main__":
    app()

import typer
import webbrowser

from pathlib import Path
from threading import Thread

from .session import Session
from .logger import Logger
from .export import Export


app = typer.Typer()

DATA_DIR = Path.home() / ".devlog" / "sessions"
CURRENT = DATA_DIR.parent / "current.json"
DASH_DIR = DATA_DIR / "dashboard"


@app.command()
def start() -> None:
    """Start a new session."""
    if CURRENT.exists():
        typer.echo("[DEVLOG] session already in progress.")
        return

    session: Session = Session.start_new(DATA_DIR)
    CURRENT.write_text(str(session.json_path))

    typer.echo(f"[DEVLOG] ✅ Session {session.id} started.")

    commit_thread = Thread(target=git_worker, daemon=True)
    commit_thread.start()


def git_worker():
    """Background git worker that keeps listeners alive."""
    session = Session.load(Path(CURRENT.read_text()))
    logger = Logger(session)
    logger.git()


@app.command()
def note(message: str) -> None:
    """
    Add a note to the active session.

    :param message: The note the user wants to log.
    :type message: str
    """
    if not CURRENT.exists():
        # TODO: Find better way to handle unactive session
        # to avoid repetitive logs like the one below from
        # start, note, stop, etc
        typer.echo("[DEVLOG] No current session active.")
        return

    path = Path(CURRENT.read_text())
    session: Session = Session.load(path)
    Logger(session).note(message)
    typer.echo("[LOG]📝 Note recorded.")


@app.command()
def stop() -> None:
    """Stop an active session."""
    if not CURRENT.exists():
        typer.echo("[DEVLOG] No current session active.")
        return

    path = Path(CURRENT.read_text())
    session: Session = Session.load(path)
    Logger(session).stop_signal = True
    session.stop()
    session.save()
    CURRENT.unlink()
    typer.echo("[DEVLOG] ✅ Session ended.")


@app.command()
def export(format: str) -> None:
    """
    Export logs to markdwon, html, etc.

    :param format: The format the user want to export the logs.
    :type format: str
    """
    session: Export = Export(DASH_DIR)
    if CURRENT.exists():
        typer.echo("[DEVLOG] Session active. Stop it before exporting.")
        return

    if format == "md":
        session.export_markdown()
        typer.echo(f"[LOG] 🚀 Logs exported to {DASH_DIR.parent}")

    if format == "html":
        session.export_html(Path("devlog/dashboard/index.html"),)
        typer.echo(f"[LOG] ✅ Data moved to HTML: {DASH_DIR}")


@app.command()
def dashboard():
    """
    Open the dashboard for the logs.

    Required to have run `devlog export html` prior.
    """
    html_path = Path(DASH_DIR / "index.html")
    if not html_path.exists():
        typer.echo(f"{html_path} does not exists. \
            Run `devlog export html` first.")
        return

    webbrowser.open(html_path.as_uri())
    typer.echo(f"[DEVLOG] Dashboard opened from {html_path}")


@app.command()
def logs():
    """Display the logs in the CLI."""
    # TODO: Implement CLI display of the logs
    pass

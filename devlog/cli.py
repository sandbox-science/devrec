import typer
import webbrowser

from pathlib import Path
from threading import Thread, Event
from typing import Optional

from .session import Session
from .logger import Logger, SESSION_MUTEX
from .export import Export


app = typer.Typer()

DATA_DIR = Path.home() / ".devlog" / "sessions"
CURRENT = DATA_DIR.parent / "current.json"
DASH_DIR = DATA_DIR / "dashboard"

SESSION: Optional[Session] = None
GIT_THREAD: Optional[Thread] = None
LOGGER: Optional[Logger] = None


@app.command()
def start() -> None:
    """Start a new session."""
    global SESSION, GIT_THREAD, LOGGER

    if CURRENT.exists():
        typer.echo("[DEVLOG] session already in progress.")
        return

    SESSION = Session.start_new(DATA_DIR)
    CURRENT.write_text(str(SESSION.json_path))
    typer.echo(f"[DEVLOG] ✅ Session {SESSION.id} started.")

    stop_event = Event()
    LOGGER = Logger(SESSION, stop_event)

    GIT_THREAD = Thread(target=git_worker, name="devlog-git", daemon=True)
    GIT_THREAD.start()


def git_worker():
    """Background git worker that keeps listeners alive."""
    if LOGGER is None:
        return
    LOGGER.git()


@app.command()
def note(message: str) -> None:
    """
    Add a note to the active session.

    :param message: The note the user wants to log.
    :type message: str
    """
    if not CURRENT.exists() or SESSION is None or LOGGER is None:
        # TODO: Find better way to handle unactive session
        # to avoid repetitive logs like the one below from
        # start, note, stop, etc
        typer.echo("[DEVLOG] No current session active.")
        return

    msg = message.strip()
    if not msg:
        typer.echo("[DEVLOG] Note cannot be empty.")
        return

    LOGGER.log_activity("note", msg)
    typer.echo("[LOG]📝 Note recorded.")


@app.command()
def stop() -> None:
    """Stop an active session."""
    global SESSION, LOGGER, GIT_THREAD

    if not CURRENT.exists() or SESSION is None:
        typer.echo("[DEVLOG] No current session active.")
        return

    if LOGGER is not None:
        LOGGER.stop()
    if GIT_THREAD is not None:
        GIT_THREAD.join()

    with SESSION_MUTEX:
        SESSION.stop()
        SESSION.save()

    CURRENT.unlink(missing_ok=True)
    typer.echo("[DEVLOG] ✅ Session ended.")

    SESSION = None
    LOGGER = None
    GIT_THREAD = None


@app.command()
def export(format: str) -> None:
    """
    Export logs to markdwon, html, etc.

    :param format: The format the user want to export the logs.
    :type format: str
    """
    if CURRENT.exists():
        typer.echo("[DEVLOG] Session active. Stop it before exporting.")
        return

    event: Export = Export(DASH_DIR)
    fmt: str = format.strip().lower()
    if fmt == "md":
        event.export_markdown()
        typer.echo(f"[LOG] 🚀 Logs exported to {DASH_DIR.parent}")
        return

    from importlib import resources
    from . import dashboard
    html_index = str(resources.files(dashboard) / "index.html")
    if fmt == "html":
        event.export_html(Path(html_index))
        typer.echo(f"[LOG] ✅ Data moved to HTML: {DASH_DIR}")
        return


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
def status():
    """
    Show the current session status and git worker state.
    """
    if SESSION is None or not CURRENT.exists():
        typer.echo("[DEVLOG] No active session.")
        return

    typer.echo(f"[DEVLOG] Active session id: {SESSION.id}")
    typer.echo(f"[DEVLOG] Day file: {SESSION.json_path}")

    alive = GIT_THREAD.is_alive() if GIT_THREAD else False
    typer.echo(f"[DEVLOG] Git worker running: {alive}")

    # Best-effort branch probe
    try:
        import subprocess

        branch = subprocess.check_output(
            ["git", "rev-parse", "--abbrev-ref", "HEAD"],
            stderr=subprocess.PIPE
        ).strip().decode()
        typer.echo(f"[DEVLOG] Git branch: {branch}")
    except Exception:
        typer.echo("[DEVLOG] Git: not a repository or unavailable.")


@app.command()
def logs():
    """Display the logs in the CLI."""
    # TODO: Implement CLI display of the logs
    pass

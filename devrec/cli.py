import typer

from pathlib import Path
from .session import Session
from .logger import Logger

app = typer.Typer()

DATA_DIR = Path.home() / ".devrec" / "sessions"
CURRENT = DATA_DIR.parent / "current.json"


@app.command()
def start():
    session = Session.start_new(DATA_DIR)
    CURRENT.write_text(str(session.json_path))
    typer.echo(f"✅ Session started: {session.id}")


@app.command()
def note(message: str):
    path = Path(CURRENT.read_text())
    session = Session.load(path)
    Logger(session).note(message)
    typer.echo("📝 Note recorded.")


@app.command()
def stop():
    path = Path(CURRENT.read_text())
    session = Session.load(path)
    session.stop()
    session.save()
    session.export_markdown()
    CURRENT.unlink()
    typer.echo(f"✅ Session saved to {session.md_path}")


if __name__ == "__main__":
    app()

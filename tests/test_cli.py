import pytest

from typer.testing import CliRunner
from devlog.cli import app
import devlog.cli as cli

runner = CliRunner()


@pytest.fixture(autouse=True)
def clean_env(tmp_path, monkeypatch):
    sessions_dir = tmp_path / "sessions"
    monkeypatch.setattr("devlog.cli.DATA_DIR", sessions_dir)
    monkeypatch.setattr("devlog.cli.CURRENT", tmp_path / "current.json")
    sessions_dir.mkdir(parents=True)

    yield

    for file in tmp_path.iterdir():
        if file.is_file():
            file.unlink()


def test_start_create_session():
    result = runner.invoke(app, ["start"])
    assert result.exit_code == 0
    assert "✅ Session started" in result.stdout
    assert cli.CURRENT.exists()


def test_start_already_active_session():
    cli.CURRENT.write_text("hello world")
    result = runner.invoke(app, ["start"])
    assert "[DEVLOG] session already in progress." in result.stdout


def test_note_no_session():
    result = runner.invoke(app, ["note", "Hello Test"])
    assert "[DEVLOG] No current session active." in result.stdout


def test_stop_no_session():
    result = runner.invoke(app, ["stop"])
    assert "[DEVLOG] No current session active." in result.stdout

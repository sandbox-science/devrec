import pytest
import devlog.cli as cli

from typer.testing import CliRunner

runner = CliRunner()


@pytest.fixture(autouse=True)
def clean_env(tmp_path, monkeypatch):
    sessions_dir = tmp_path / "sessions"

    monkeypatch.setattr("pathlib.Path.home", lambda: tmp_path)

    monkeypatch.setattr("devlog.cli.DATA_DIR", sessions_dir)
    monkeypatch.setattr("devlog.cli.CURRENT", tmp_path / "current.json")

    sessions_dir.mkdir(parents=True, exist_ok=True)

    yield

    for file in tmp_path.iterdir():
        if file.is_file():
            file.unlink()


def test_start_create_session():
    result = runner.invoke(cli.app, ["start"])
    assert result.exit_code == 0
    assert "✅ Session started" in result.stdout
    assert cli.CURRENT.exists()


def test_start_already_active_session():
    cli.CURRENT.write_text("hello world")
    result = runner.invoke(cli.app, ["start"])
    assert "[DEVLOG] session already in progress." in result.stdout


def test_note():
    runner.invoke(cli.app, ["start"])
    result = runner.invoke(cli.app, ["note", "Hello Test"])
    assert "[LOG]📝 Note recorded." in result.stdout


def test_note_no_session():
    result = runner.invoke(cli.app, ["note", "Hello Test"])
    assert "[DEVLOG] No current session active." in result.stdout


def test_stop():
    runner.invoke(cli.app, ["start"])
    result = runner.invoke(cli.app, ["stop"])
    assert "[DEVLOG] ✅ Session ended." in result.stdout


def test_stop_no_session():
    result = runner.invoke(cli.app, ["stop"])
    assert "[DEVLOG] No current session active." in result.stdout


def test_export_markdown():
    result = runner.invoke(cli.app, ["export", "md"])
    assert "[LOG] 🚀 Logs exported" in result.stdout


def test_export_html():
    result = runner.invoke(cli.app, ["export", "html"])
    assert "[LOG] ✅ Data moved to HTML" in result.stdout


def test_export_fail():
    cli.CURRENT.write_text("hello world")
    result = runner.invoke(cli.app, ["export", "md"])

    assert "[DEVLOG] Session active. Stop it before exporting." \
        in result.stdout

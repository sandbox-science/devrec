from .cli import start, stop, note, export, dashboard, CURRENT, status

import cmd
import os
import signal

BANNER = """
    ░████    ░███████                         ░██                                  ░████
    ░██      ░██   ░██                        ░██                                    ░██
    ░██      ░██    ░██  ░███████  ░██    ░██ ░██          ░███████   ░████████      ░██
    ░██      ░██    ░██ ░██    ░██ ░██    ░██ ░██         ░██    ░██ ░██    ░██      ░██
    ░██      ░██    ░██ ░█████████  ░██  ░██  ░██         ░██    ░██ ░██    ░██      ░██
    ░██      ░██   ░██  ░██          ░██░██   ░██         ░██    ░██ ░██   ░███      ░██
    ░██      ░███████    ░███████     ░███    ░██████████  ░███████   ░█████░██      ░██
    ░██                                                                     ░██      ░██
    ░████                                                             ░███████     ░████
"""

BLUE = "\033[1;34m"
RESET = "\033[0m"


class DevLogShell(cmd.Cmd):
    intro = f"{BANNER}\n\t\tWelcome to DevLog Shell." \
            "Type help or ? to list commands.\n"
    prompt = f"{BLUE}devlog >{RESET} "

    def do_start(self, args):
        """Start a new session."""
        start()

    def do_note(self, arg):
        """
        Add a note to your log.

        example:
        > note your_message
        """
        note(arg)

    def do_stop(self, arg):
        """Stop session."""
        stop()

    def do_export(self, arg):
        """
        Export logs to markdwon, html, etc.

        :param format: The format the user want to export the logs.
        :type format: str
        """
        export(arg)

    def do_dashboard(self, arg):
        """
        Open the dashboard for the logs.

        Required to have run `export html` prior.
        """
        dashboard()

    def do_status(self, arg):
        """
        Display current session status.
        """
        status()

    def emptyline(self):
        """Ignore when an empty line is entered by the user."""
        pass

    def default(self, line):
        """Run any unknown command in the system shell."""
        if not line.strip():
            print()
            return
        try:
            os.system(line)
        except Exception as e:
            print(f"[DEVLOG] Error running command: {e}")

    def do_exit(self, arg):
        """Exit the DevLog shell."""
        if not CURRENT.exists():
            print("\nGood work on today's session.\nCome again!\n")
            return True

        print("\n[DEVLOG] session still in progress. Type `stop` first. \n")


def _handle_signal(_sig, _frame):
    # shutdown on Ctrl-C / SIGTERM
    try:
        if CURRENT.exists():
            print("\n[DEVLOG] Caught interrupt. Stopping session...")
            stop()
    finally:
        raise SystemExit(130)


def init():
    """Entry point of the app. Initialize DevLog Shell."""
    signal.signal(signal.SIGINT, _handle_signal)
    signal.signal(signal.SIGTERM, _handle_signal)
    DevLogShell().cmdloop()

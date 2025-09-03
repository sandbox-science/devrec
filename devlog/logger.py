from .session import Session

from threading import Lock

import subprocess
import time

# mutex to avoid race condition when adding
# a new event between auto detected activites
# and manually added events (notes)
SESSION_MUTEX = Lock()

class Logger:
    def __init__(self, session: Session):
        self.session: Session = session
        self.stop_signal = False

    def log_activity(self, activity_type: str, message: str) -> None:
        """
        Log session activities.

        :param activity_type: The type of the log.
        :type activity_type: str
        :param message: The message to log into the log.
        :type message: str
        """
        with SESSION_MUTEX:
            self.session.add_event(activity_type, message)
            self.session.save()

    def _get_current_commit(self):
        return subprocess.check_output(
            ["git", "rev-parse", "HEAD"]
        ).strip().decode("utf-8")

    def _get_staged_files(self):
        output = subprocess.check_output(
            ["git", "diff", "--cached", "--name-only"]
        ).strip().decode()
        return set(output.splitlines()) if output else set()

    def _get_unstaged_files(self):
        output = subprocess.check_output(
            ["git", "diff", "--name-only"]
        ).strip().decode()
        return set(output.splitlines()) if output else set()

    def _get_current_branch(self):
        return subprocess.check_output(
            ["git", "rev-parse", "--abbrev-ref", "HEAD"]
        ).strip().decode()

    def git(self):
        """Log git activities."""
        current_commit = self._get_current_commit()
        staged_files = self._get_staged_files()
        unstaged_files = self._get_unstaged_files()
        current_branch = self._get_current_branch()

        while not self.stop_signal:
            try:
                # Detect new commits
                new_commit = self._get_current_commit()
                if new_commit != current_commit:
                    result = subprocess.run(
                        ["git", "log", "-1", "--pretty=oneline"],
                        capture_output=True,
                        text=True
                    )
                    commit_msg = result.stdout.strip()
                    self.log_activity("git", f"New commit: {commit_msg}")
                    current_commit = new_commit

                # Detect new staged files
                new_staged = self._get_staged_files()
                if new_staged != staged_files:
                    diff_added = new_staged - staged_files
                    if diff_added:
                        self.log_activity(
                            "git", f"Staged files: {', '.join(diff_added)}"
                        )
                    staged_files = new_staged

                # Detect new unstaged changes
                new_unstaged = self._get_unstaged_files()
                if new_unstaged != unstaged_files:
                    diff_added = new_unstaged - unstaged_files
                    if diff_added:
                        self.log_activity(
                            "git", f"Unstaged files: {', '.join(diff_added)}"
                        )
                    unstaged_files = new_unstaged

                # Detect branch switches
                new_branch = self._get_current_branch()
                if new_branch != current_branch:
                    self.log_activity(
                        "git", f"Switched to branch: {new_branch}"
                    )
                    current_branch = new_branch

            except subprocess.CalledProcessError:
                pass

            time.sleep(10)

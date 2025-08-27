from .session import Session

import subprocess
import time


class Logger:
    def __init__(self, session: Session):
        self.session: Session = session
        self.stop_signal = False

    def note(self, message: str):
        """
        Log a note.

        :param message: The note the user wants to log.
        :type message str:
        """
        self.session.add_event("note", message)
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
                    self.session.add_event("git", f"New commit: {commit_msg}")
                    self.session.save()
                    current_commit = new_commit

                # Detect new staged files
                new_staged = self._get_staged_files()
                if new_staged != staged_files:
                    diff_added = new_staged - staged_files
                    if diff_added:
                        self.session.add_event(
                            "git", f"Staged files: {', '.join(diff_added)}"
                        )
                        self.session.save()
                    staged_files = new_staged

                # Detect new unstaged changes
                new_unstaged = self._get_unstaged_files()
                if new_unstaged != unstaged_files:
                    diff_added = new_unstaged - unstaged_files
                    if diff_added:
                        self.session.add_event(
                            "git", f"Unstaged files: {', '.join(diff_added)}"
                        )
                        self.session.save()
                    unstaged_files = new_unstaged

                # Detect branch switches
                new_branch = self._get_current_branch()
                if new_branch != current_branch:
                    self.session.add_event(
                        "git", f"Switched to branch: {new_branch}"
                    )
                    self.session.save()
                    current_branch = new_branch

            except subprocess.CalledProcessError:
                pass

            time.sleep(10)

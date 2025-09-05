from .session import Session

from threading import Lock, Event
from typing import Optional, Set

import subprocess

# mutex to avoid race condition when adding
# a new event between auto detected activites
# and manually added events (notes)
SESSION_MUTEX = Lock()


class Logger:
    def __init__(self, session: Session, stop_event: Optional[Event]):
        self.session: Session = session
        self._stop_event = stop_event or Event()

    def stop(self) -> None:
        self._stop_event.set()

    def stopped(self) -> bool:
        return self._stop_event.is_set()

    def log_activity(self, event_type: str, message: str) -> None:
        """
        Log session activities.

        :param event_type: The type of the event to log.
        :type event_type: str
        :param message: The message to log into the logger.
        :type message: str
        """
        with SESSION_MUTEX:
            self.session.add_event(event_type, message)
            self.session.save()

    def _get_current_commit(self) -> str:
        return subprocess.check_output(
            ["git", "rev-parse", "HEAD"],
            # I set the following to PIPE instead of DEVNULL
            # in case it is needed in the future for debugging purposes.
            # This help suppress the warning when devlog is used outside
            # a repository where git is init.
            # TODO: Find a better way to handle this case
            stderr=subprocess.PIPE
        ).strip().decode("utf-8")

    def _get_staged_files(self) -> Set[str]:
        output = subprocess.check_output(
            ["git", "diff", "--cached", "--name-only"]
        ).strip().decode()
        return set(output.splitlines()) if output else set()

    def _get_unstaged_files(self) -> Set[str]:
        output = subprocess.check_output(
            ["git", "diff", "--name-only"]
        ).strip().decode()
        return set(output.splitlines()) if output else set()

    def _get_current_branch(self) -> str:
        return subprocess.check_output(
            ["git", "rev-parse", "--abbrev-ref", "HEAD"]
        ).strip().decode()

    def git(self):
        """Background loop to log git activities."""
        try:
            current_commit = self._get_current_commit()
            staged_files = self._get_staged_files()
            unstaged_files = self._get_unstaged_files()
            current_branch = self._get_current_branch()
        except subprocess.CalledProcessError:
            # Disable git loggin if not a repo.
            print("\n[DEVLOG] Not a git repository...")
            print("[DEVLOG] Git activity capture disabled.")
            return

        while not self.stopped():
            try:
                # Detect new commits
                try:
                    new_commit = self._get_current_commit()
                    if new_commit != current_commit:
                        result = subprocess.run(
                            ["git", "log", "-1", "--pretty=oneline"],
                            capture_output=True,
                            text=True,
                            check=False,
                        )
                        commit_msg = result.stdout.strip()
                        self.log_activity("git", f"New commit: {commit_msg}")
                        current_commit = new_commit
                except subprocess.CalledProcessError:
                    return

                # Detect new staged files
                try:
                    new_staged = self._get_staged_files()
                    if new_staged != staged_files:
                        diff_added = new_staged - staged_files
                        if diff_added:
                            self.log_activity(
                                "git", f"Staged files: {', '.join(diff_added)}"
                            )
                        staged_files = new_staged
                except subprocess.CalledProcessError:
                    return

                # Detect new unstaged changes
                try:
                    new_unstaged = self._get_unstaged_files()
                    if new_unstaged != unstaged_files:
                        diff_added = new_unstaged - unstaged_files
                        if diff_added:
                            self.log_activity(
                                "git", f"Unstaged files: {', '.join(diff_added)}"
                            )
                        unstaged_files = new_unstaged
                except subprocess.CalledProcessError:
                    return

                # Detect branch switches
                try:
                    new_branch = self._get_current_branch()
                    if new_branch != current_branch:
                        self.log_activity(
                            "git", f"Switched to branch: {new_branch}"
                        )
                        current_branch = new_branch
                except subprocess.CalledProcessError:
                    return

            except Exception:
                pass

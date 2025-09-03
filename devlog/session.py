from datetime import datetime
from pathlib import Path
from typing import TypedDict, List

import json
import os


class Event(TypedDict):
    timestamp: str
    type: str
    directory: str
    message: str


class SessionData(TypedDict, total=False):
    id: str
    start_time: str
    stop_time: str
    cwd: str
    events: List[Event]


class Session:
    def __init__(self, session_id: str, base_dir: Path) -> None:
        self.id = session_id
        self.base_dir = base_dir
        self.json_path = base_dir / \
            f"{datetime.now().strftime("%Y-%m-%d")}.json"
        self.data: SessionData = {
            "id": session_id,
            "start_time": datetime.now().isoformat(timespec="seconds"),
            "cwd": os.getcwd(),
            "events": []
        }

    @classmethod
    def start_new(cls, base_dir: Path) -> "Session":
        today_file = base_dir / f"{datetime.now().strftime("%Y-%m-%d")}.json"
        if today_file.exists():
            with open(today_file, "r") as f:
                sessions = json.load(f)
            # Next id is count of existing items (excluding header)
            count = sum(1 for it in sessions if it.get("id"))
            session_id = str(count + 1)
        else:
            session_id = "1"
        session = cls(session_id, base_dir)
        session.save()
        return session

    # This function is note used nor necessary no more
    # It is kept here in case we want to continue a session
    # that has not been finished (not sure if we will yet)
    # I just leave it here for now.
    # TODO: decide what to do with this
    @classmethod
    def load(cls, path: Path) -> "Session":
        with open(path, "r") as f:
            sessions = json.load(f)

        latest = None
        for item in sessions:
            if item.get("id"):
                latest = item

        if latest is None:
            return cls("1", path.parent)

        session = cls(item["id"], path.parent)
        session.data = latest
        return session

    def add_event(self, event_type: str, message: str) -> None:
        self.data.setdefault("events", []).append(
            {
                "timestamp": datetime.now().isoformat(timespec="seconds"),
                "type": event_type,
                # TODO: Find a better way to display the directory
                "directory": Path(os.getcwd()).name,
                "message": message
            }
        )

    def stop(self) -> None:
        self.data["stop_time"] = datetime.now().isoformat(timespec="seconds")

    def save(self) -> None:
        self.base_dir.mkdir(parents=True, exist_ok=True)
        today_file = self.json_path

        sessions = []
        if today_file.exists():
            with open(today_file, "r") as f:
                sessions = json.load(f)
        else:
            sessions = [{"log": datetime.now().strftime("%Y-%m-%d")}]

        # Update existing session or add new one
        for i, session in enumerate(sessions):
            if session.get("id") == self.data["id"]:
                sessions[i] = self.data
                break
        else:
            sessions.append(self.data)

        with open(today_file, "w") as f:
            json.dump(sessions, f, indent=2)

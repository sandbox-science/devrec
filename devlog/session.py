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
        self.json_path = base_dir / f"{datetime.now().strftime("%Y-%m-%d")}.json"
        self.md_path = self.json_path.with_suffix(".md")
        self.data: SessionData = {
            "id": session_id,
            "start_time": datetime.now().isoformat(timespec="seconds"),
            "cwd": os.getcwd(),
            "events": []
        }

    @classmethod
    def start_new(cls, base_dir: Path) -> "Session":
        session_id = datetime.now().strftime("%H-%M-%S")
        session = cls(session_id, base_dir)
        session.save()
        return session

    @classmethod
    def load(cls, path: Path) -> "Session":
        with open(path, "r") as f:
            sessions = json.load(f)

        for item in sessions:
            if "id" in item and item["id"]:
                session = cls(item["id"], path.parent)
                session.data = item
        return session

    def add_event(self, event_type: str, message: str) -> None:
        self.data["events"].append({
            "timestamp": datetime.now().isoformat(timespec="seconds"),
            "type": event_type,
            "directory": Path(os.getcwd()).name, # TODO: Find a better way to display directory
            "message": message
        })

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

    def export_markdown(self) -> None:
        with open(self.json_path, "r") as f:
            sessions = json.load(f)

        for data in sessions:
            if "log" in data:
                lines = [
                    f"# DevLog — {data['log']}\n"
                ]
            else:
                start_log = data.get('start_time')
                lines = [
                    f"## Session Log — {data.get("id")}",
                    f"\U0001F4C1 **CWD**: {data.get('cwd')}",
                    f"\U0001F551 **Start**: {start_log[start_log.find("T")+1:]}",
                ]

                for event in data.get("events"):
                    time = event["timestamp"].split("T")[1]
                    lines.append(f"- \U0001F4DD {time}: {event['message']}")

                if "stop_time" in data:
                    stop_log = data.get('stop_time')
                    lines.append(f"\U0001F6D1 **Stop**: {stop_log[stop_log.find("T")+1:]}\n---\n")
            with open(self.md_path, "a") as f:
                f.write("\n".join(lines))

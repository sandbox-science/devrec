from datetime import datetime
from pathlib import Path
from typing import TypedDict, List

import json
import os


class Event(TypedDict):
    timestamp: str
    type: str
    message: str


class SessionData(TypedDict, total=False):
    id: str
    start_time: str
    stop_time: str
    cwd: str
    events: List[Event]


class Session:
    def __init__(self, session_id: str, base_dir: Path):
        self.id = session_id
        self.base_dir = base_dir
        self.json_path = base_dir / f"{session_id}.json"
        self.md_path = self.json_path.with_suffix(".md")
        self.data: SessionData = {
            "id": session_id,
            "start_time": datetime.now().isoformat(timespec="seconds"),
            "cwd": os.getcwd(),
            "events": []
        }

    @classmethod
    def start_new(cls, base_dir: Path) -> "Session":
        session_id = datetime.now().strftime("%Y-%m-%d_%H-%M")
        session = cls(session_id, base_dir)
        session.save()
        return session

    @classmethod
    def load(cls, path: Path) -> "Session":
        with open(path) as f:
            data: SessionData = json.load(f)
        session = cls(data["id"], path.parent)
        session.data = data
        return session

    def add_event(self, event_type: str, message: str):
        self.data["events"].append({
            "timestamp": datetime.now().isoformat(timespec="seconds"),
            "type": event_type,
            "message": message
        })

    def stop(self):
        self.data["stop_time"] = datetime.now().isoformat(timespec="seconds")

    def save(self):
        self.base_dir.mkdir(parents=True, exist_ok=True)
        with open(self.json_path, "w") as f:
            json.dump(self.data, f, indent=2)

    def export_markdown(self):
        lines = [
            f"# DevRec Session — {self.id}",
            f"\U0001F4C1 **CWD**: {self.data['cwd']}",
            f"\U0001F551 **Start**: {self.data['start_time']}",
        ]
        for event in self.data["events"]:
            time = event["timestamp"].split("T")[1]
            lines.append(f"- \U0001F4DD {time}: {event['message']}")
        if "stop_time" in self.data:
            lines.append(f"\U0001F6D1 **Stop**: {self.data['stop_time']}\n")
        with open(self.md_path, "w") as f:
            f.write("\n".join(lines))

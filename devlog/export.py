from datetime import datetime
from bs4 import BeautifulSoup
from pathlib import Path
from typing import Optional

import json
import os
import shutil


class Export:
    def __init__(self, base_dir: Path) -> None:
        self.dash_dir = base_dir
        self.dash_dir.mkdir(parents=True, exist_ok=True)

        self.json_path = base_dir.parent

    def export_markdown(self) -> None:
        """
        Export JSON logs into markdown files.
        """
        files = self._fetch_json_files()
        for file in files:
            json_path = self.json_path / file
            markdown_path = json_path.with_suffix(".md")

            sessions = json.loads(json_path.read_text())
            lines = []

            for data in sessions:
                lines.extend(self._format_session_to_md(data))

            markdown_path.write_text("\n".join(lines))

    def _format_session_to_md(self, data: dict) -> list[str]:
        """
        Convert a single session dict into markdown lines.
        """
        if "log" in data:
            return [f"# DevLog — {data['log']}\n"]

        lines = [
            f"## Session Log — {data.get('id')}",
            f"\U0001F4C1 **CWD**: {data.get('cwd', 'N/A')}",
            f"\U0001F551 **Start**: {self._format_time(data['start_time'])}",
        ]

        for event in data.get("events", []):
            time = event.get("timestamp", "").split("T")[-1]
            lines.append(f"- \U0001F4DD {time}: {event.get('message', '')}")

        if stop := data.get("stop_time"):
            lines.append(
                f"\U0001F6D1 **Stop**: {self._format_time(stop)}\n---\n"
            )

        return lines

    def _format_time(self, timestamp: Optional[str]) -> str:
        if timestamp is None:
            return "Unknown"
        else:
            return datetime.fromisoformat(timestamp).strftime("%H:%M:%S")

    def _fetch_json_files(self) -> list:
        """
        Fetch all JSON files in `/.devlog/sessions/` directory.

        :return: List of JSON files.
        """
        path_to_json = self.json_path
        json_files: list = [
            pos_json for pos_json in os.listdir(path_to_json)
            if pos_json.endswith('.json')
        ]
        return sorted(json_files, reverse=True)

    def _build_sidebar(self, soup, files: list) -> None:
        sidebar_section = soup.find("aside", id="sidebar")
        h3 = soup.new_tag("h3")
        h3.string = "Logs"
        sidebar_section.append(h3)

        ul = soup.new_tag("ul")
        for file in files:
            li = soup.new_tag("li")
            a = soup.new_tag("a", href=f"{Path(file).stem}.html")
            a.string = Path(file).stem
            li.append(a)
            ul.append(li)
        sidebar_section.append(ul)

    def _add_articles(self, soup, articles: list) -> None:
        articles_section = soup.find("section", id="articles")
        for entry in articles:
            new_article = soup.new_tag("article")
            # Daily log header
            if "log" in entry:
                h3 = soup.new_tag("h3")
                dev_log = entry['log'].replace("-", "/")
                h3.string = f"📅 DevLog {dev_log}"
                new_article.append(h3)

            # Session details with events
            if "events" in entry:
                h3 = soup.new_tag("h3")
                h3.string = f"🆔 Session Log -- {entry['id']}"
                new_article.append(h3)

                # Start/Stop time
                p = soup.new_tag("p")
                dt_start = self._format_time(entry['start_time'])
                dt_stop = self._format_time(entry['stop_time'])
                p.string = f"⏱️ Started: {dt_start} | 🛑 Ended: {dt_stop}"
                new_article.append(p)

                # Event list
                ul = soup.new_tag("ul")
                for event in entry["events"]:
                    li = soup.new_tag("li")

                    timestamp = self._format_time(event['timestamp'])

                    time_span = soup.new_tag("span", **{"class": "time"})
                    time_span.string = timestamp
                    strong_tag = soup.new_tag("strong")
                    strong_tag.string = event['directory']

                    type = f" {event['type'].upper()} while in "
                    message = f": {event['message'].capitalize()}"
                    li.append(time_span)
                    li.append(type)
                    li.append(strong_tag)
                    li.append(message)

                    ul.append(li)

                new_article.append(ul)

            articles_section.append(new_article)

    def export_html(self, template_file: Path) -> None:
        """
        Export JSON log to a styled HTML.

        :param template_file: Template for the HTML design
        :type template_file: Path
        """
        files = self._fetch_json_files()
        for file in files:
            with open(template_file, "r", encoding="utf-8") as tpl:
                soup: BeautifulSoup = BeautifulSoup(tpl, "html.parser")

            self._build_sidebar(soup, files)

            with open(
                Path(self.json_path) / file, "r", encoding="utf-8"
            ) as f:
                articles = json.load(f)
            self._add_articles(soup, articles)

            output_html = Path(self.dash_dir / file).with_suffix(".html")

            with open(output_html, "w", encoding="utf-8") as out:
                html_content: str = str(soup.prettify())
                out.write(html_content)

        latest_html = Path(self.dash_dir / files[0]).with_suffix(".html")
        shutil.copy(latest_html, (self.dash_dir) / "index.html")

        self._copy_dashboard_assets(self.dash_dir)

    def _copy_dashboard_assets(self, dest_dir: Path) -> None:
        """
        Copy dashboard static assets into the given destination.

        :param dest_dir: The destination where to copy the assets
        :type dest_dir: Path
        """
        from importlib import resources
        from . import dashboard
        assets = ["styles.css", "toggle-mode.js"]
        for file in assets:
            resource = resources.files(dashboard) / file
            with resources.as_file(resource) as source_path:
                shutil.copy(source_path, dest_dir / file)

from datetime import datetime
from bs4 import BeautifulSoup
from pathlib import Path

import json
import os
import shutil


class Export:
    def __init__(self, base_dir: Path) -> None:
        self.json_path = base_dir
        self.md_path = self.json_path.with_suffix(".md")
        self.html_path = self.json_path.with_suffix(".html")

    def export_markdown(self) -> None:
        with open(self.json_path, "r") as f:
            sessions = json.load(f)

        for data in sessions:
            if "log" in data:
                lines = [
                    f"# DevLog — {data['log']}\n"
                ]
            else:
                start_log = datetime.fromisoformat(data['start_time'])
                lines = [
                    f"## Session Log — {data.get("id")}",
                    f"\U0001F4C1 **CWD**: {data.get('cwd')}",
                    f"\U0001F551 **Start**: {start_log}",
                ]

                for event in data.get("events"):
                    time = event["timestamp"].split("T")[1]
                    lines.append(f"- \U0001F4DD {time}: {event['message']}")

                if "stop_time" in data:
                    stop_log = datetime.fromisoformat(data['stop_time'])
                    lines.append(f"\U0001F6D1 **Stop**: {stop_log}\n---\n")
            with open(self.md_path, "a") as f:
                f.write("\n".join(lines))

    def fetch_json_files(self):
        """
        Fetch all JSON files in `/.devlog/sessions/` directory.
        """
        path_to_json = self.json_path.parent
        json_files = [
            pos_json for pos_json in os.listdir(path_to_json)
            if pos_json.endswith('.json')
        ]
        return sorted(json_files, reverse=True)

    def _build_sidebar(self, soup, files):
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

    def _add_articles(self, soup, articles):
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
                dt_start = datetime.fromisoformat(entry['start_time'])
                dt_stop = datetime.fromisoformat(entry['stop_time'])
                p.string = f"⏱️ Started: {dt_start.strftime('%H:%M:%S')} \
                    | 🛑 Ended: {dt_stop.strftime('%H:%M:%S')}"
                new_article.append(p)

                # Event list
                ul = soup.new_tag("ul")
                for event in entry["events"]:
                    li = soup.new_tag("li")

                    dt_timestamp = datetime.fromisoformat(event['timestamp'])
                    timestamp = dt_timestamp.strftime("%H:%M:%S")

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

    def export_html(self, template_file: Path):
        """
        Export JSON log to a styled HTML.

        :param template_file: Template for the HTML design
        :type template_file: Path
        """
        files = self.fetch_json_files()
        for file in files:
            with open(template_file, "r", encoding="utf-8") as tpl:
                soup = BeautifulSoup(tpl, "html.parser")

            self._build_sidebar(soup, files)

            with open(
                Path(self.json_path.parent) / file, "r", encoding="utf-8"
            ) as f:
                articles = json.load(f)
            self._add_articles(soup, articles)

            output_html = Path((self.json_path.parent) / file) \
                .with_suffix(".html")

            with open(output_html, "w", encoding="utf-8") as out:
                out.write(soup.prettify())

        latest_html = Path((self.json_path.parent) / files[0]) \
            .with_suffix(".html")
        shutil.copy(latest_html, (self.json_path.parent) / "index.html")

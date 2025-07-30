# DevLog Python Prototype

**DevLog** is a lightweight CLI tool that records your local developer workflow. It captures notes, shell activity, and optionally Git actions to produce a structured, timestamped report, perfect for debugging, documentation, or reflection.

> [!NOTE]
>
> More about the idea on this [article](https://listed.to/@Astra/63832/devlog-cli-developer-tool). 

---

## Features

- 📋 Start and stop coding sessions
- 📝 Add timestamped notes during a session
- 📂 Export sessions as Markdown logs
- 📁 Organized logs stored in `~/.devlog/sessions/`

---

## Installation

```bash
# Clone the repository
git clone https://github.com/sandbox-science/devlog.git
cd devlog

# Set up virtual environment (optional but recommended)
python3 -m venv .venv
source .venv/bin/activate

# Install in editable mode with dev dependencies
pip install -e ".[dev]"
```

## Usage

```bash
# Start a session
devlog start

# Add a note
devlog note "Working on Sandbox Science Project"

# End the session and export to Markdown
devlog stop

# Export your logs into markdown or HTML
devlog export md
devlog export html

# Open a dashboard to display your logs
devlog dashboard
```

All session are saved in `~/.devlog/sessions/{timestamp}.json` and `.md`

## Engineering Requirement Document

You can find the ERD on [Proton Doc](https://drive.proton.me/urls/P3WXQMK1FR#HKBehxHS1qO5)

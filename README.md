# DevRec Python Prototype

**DevRec** is a lightweight CLI tool that records your local developer workflow. It captures notes, shell activity, and optionally Git actions to produce a structured, timestamped report, perfect for debugging, documentation, or reflection.

---

## Features

- 📋 Start and stop coding sessions
- 📝 Add timestamped notes during a session
- 📂 Export sessions as Markdown logs
- 📁 Organized logs stored in `~/.devrec/sessions/`

---

## Installation

```bash
# Clone the repository
git clone https://github.com/sandbox-science/devrec.git
cd devrec

# Set up virtual environment (optional but recommended)
python3 -m venv .venv
source .venv/bin/activate

# Install in editable mode with dev dependencies
pip install -e ".[dev]"
```

## Usage

```bash
# Start a session
devrec start

# Add a note
devrec note "Working on Sandbox Science Project"

# End the session and export to Markdown
devrec stop
```

All session are saved in `~/.devrec/sessions/{timestamp}.json` and `.md`


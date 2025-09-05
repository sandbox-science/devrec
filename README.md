```
░████░███████                      ░██                          ░████ 
░██  ░██   ░██                     ░██                            ░██ 
░██  ░██    ░██ ░███████ ░██    ░██░██        ░███████  ░████████ ░██ 
░██  ░██    ░██░██    ░██░██    ░██░██       ░██    ░██░██    ░██ ░██ 
░██  ░██    ░██░█████████ ░██  ░██ ░██       ░██    ░██░██    ░██ ░██ 
░██  ░██   ░██ ░██         ░██░██  ░██       ░██    ░██░██   ░███ ░██ 
░██  ░███████   ░███████    ░███   ░██████████░███████  ░█████░██ ░██ 
░██                                                           ░██ ░██ 
░████                                                   ░███████░████ 
                                                                      
```                                                                                       
**DevLog** is a lightweight CLI tool that records your local development workflow. It captures notes, shell activity, and Git actions to produce a structured, timestamped report, perfect for debugging, documentation, or reflection. The logs are recorded in text format via a JSON file. The tool can generate a Markdown and HTML report for developers to directly visualize their workflow offline directly from their browser.

> [!NOTE]
>
> More about the idea on this [article](https://listed.to/@Astra/63832/devlog-cli-developer-tool). 

---

## Features

- 📋 Start and stop sessions via DevLog shell
- 📝 Add timestamped notes during a session
- 🎟️ Add timestamped git activity during a session
- 📂 Export sessions as Markdown and HTML logs
- 📁 Organized logs stored in `~/.devlog/sessions/`

---

## User Installation
The project is not yet available on `pip`. However, you can install it running the following:

```bash
# Set up virtual environment (optional but recommended)
python3 -m venv .venv
source .venv/bin/activate

# Install with pip from GitHub main branch
pip install git+ssh://git@github.com/sandbox-science/devlog.git@main
```

## Dev Mode Installation

```bash
# Clone the repository
git clone https://github.com/sandbox-science/devlog.git
cd devlog

# Set up virtual environment (optional but recommended)
python3 -m venv .venv
source .venv/bin/activate

# Install with dev dependencies
pip install -e ".[dev]"
```

## Usage

```bash
# Initialize DevLog shell mode
devlog

# Start a session
start

# Add a note
note Working on Sandbox Science Project

# End the session and export to Markdown
stop

# Export all your logs into markdown or HTML
export md
export html

# Open a dashboard to display your logs
dashboard

# Exit DevLog shell mode
exit
```

- All **JSON** session are saved in `~/.devlog/sessions/{timestamp}.json`
- All exported **HTML** sessions are saved in `~/.devlog/sessions/dashboard/index.html`
- All exported **Markdown** sessions are saved in `~/.devlog/sessions/{timestamp}.md`

## Engineering Requirement Document

You can find the ERD on [Proton Doc](https://drive.proton.me/urls/P3WXQMK1FR#HKBehxHS1qO5)

# Rocketlane CLI — Claude Code Setup

This guide walks you through setting up the Rocketlane CLI as a Claude Code skill so you can manage Rocketlane via natural language in your terminal.

## Prerequisites

- **Python 3.9+** installed
- **Claude Code** installed and working (`claude` command available)
- **Rocketlane API key** — get yours from **Settings > API > Create API key** in your Rocketlane instance

## Step 1: Install the CLI

```bash
git clone https://github.com/austinsomer/rocketlane-cli.git
cd rocketlane-cli
pip install -e .
```

Verify it installed:

```bash
rocketlane --help
```

If `rocketlane` isn't found, the binary is likely at `~/Library/Python/3.9/bin/rocketlane` (macOS) or `~/.local/bin/rocketlane` (Linux). You can either:

```bash
# Option A: Add to PATH (add to your ~/.zshrc or ~/.bashrc)
export PATH="$HOME/Library/Python/3.9/bin:$PATH"

# Option B: Use the full path everywhere
~/Library/Python/3.9/bin/rocketlane --help
```

## Step 2: Connect Your Rocketlane Instance

```bash
rocketlane status
```

First run will prompt you for:
1. **Instance URL** — e.g. `acme.rocketlane.com`
2. **API Key** — your Rocketlane API key

The CLI validates the key, auto-generates a short name from the URL (e.g. `acme`), and saves everything to `~/.rocketlane/config.json`.

To add additional instances later:

```bash
rocketlane add-instance
```

## Step 3: Install the Claude Code Skill

Copy the skill file into your Claude Code commands directory:

```bash
# Create the commands directory if it doesn't exist
mkdir -p ~/.claude/commands

# Copy the skill file
cp rocketlane-cli/skills/rocketlane.md ~/.claude/commands/rocketlane.md
```

### Update the Binary Path

Open `~/.claude/commands/rocketlane.md` and update the binary path near the top to match your system:

```
**Binary location:** `/Users/YOUR_USERNAME/Library/Python/3.9/bin/rocketlane`
```

Find your actual path with:

```bash
which rocketlane || find ~/Library/Python ~/.local/bin -name rocketlane 2>/dev/null
```

Replace the path in the skill file with your result.

## Step 4: Verify Everything Works

Open a new Claude Code session:

```bash
claude
```

Then try:

```
> List my Rocketlane projects
> Show Rocketlane status
> What instances do I have configured?
```

Claude should use the `/rocketlane` skill to execute these commands.

## Usage Examples

Once set up, you can use natural language to interact with Rocketlane:

### Projects
- "List all active Rocketlane projects"
- "Create a new project called 'Acme Onboarding' for customer Acme Inc"
- "Archive project 201"
- "Add alice@company.com to project 201"

### Tasks
- "Show tasks for project 5000000023535"
- "Create a kickoff task due April 1st in project 201"
- "Mark task 501 as completed"
- "Assign bob@company.com to task 501"

### Time Tracking
- "Log 2.5 hours against task 501 for today"
- "Show time entries for project 201 this month"
- "What time categories are available?"

### Instance Management
- "Switch to the acme Rocketlane instance"
- "Add a new Rocketlane instance"
- "List all my configured RL instances"
- "Show projects on the globex instance"

### Power Moves
- "List all in-progress projects, then show me the tasks for the first one"
- "Create a project for NewCo, add a Discovery phase, then add three tasks to it"
- "Log 1 hour for today against every open task assigned to me"

## Troubleshooting

### "rocketlane: command not found"

Add the install location to your PATH:

```bash
# Find where it installed
pip show rocketlane-cli | grep Location

# macOS typical location
export PATH="$HOME/Library/Python/3.9/bin:$PATH"

# Linux typical location
export PATH="$HOME/.local/bin:$PATH"
```

Add the `export` line to your `~/.zshrc` or `~/.bashrc` to make it permanent.

### "No API key configured"

Run `rocketlane add-instance` to set up your first instance, or check your config:

```bash
cat ~/.rocketlane/config.json
```

### Claude doesn't use the skill

1. Make sure the skill file is at `~/.claude/commands/rocketlane.md`
2. Verify the binary path in the skill file is correct
3. Start a fresh Claude Code session (skills are loaded at startup)
4. Try invoking it explicitly: `/rocketlane`

### API errors

```bash
# Check connectivity
rocketlane status

# See what instance is active
rocketlane instances

# Try with verbose output
rocketlane projects list --json
```

## Updating

Pull the latest and reinstall:

```bash
cd rocketlane-cli
git pull
pip install -e .
```

If the skill file was updated, re-copy it:

```bash
cp skills/rocketlane.md ~/.claude/commands/rocketlane.md
```

(Remember to update the binary path again if needed.)

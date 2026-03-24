---
name: rocketlane
description: Rocketlane CLI - manage projects, tasks, phases, time tracking, users, spaces, documents, invoices, custom fields, resource allocations, time-offs, and multi-instance switching in Rocketlane (Professional Services Automation). Use when the user wants to create/update/delete projects, manage tasks, assign team members, track time, manage phases, switch Rocketlane instances, or perform any Rocketlane operation. Also trigger for mentions of "Rocketlane", "RL", "PSA", onboarding projects, customer implementations, or professional services workflows.
tools: Bash
---

# Rocketlane CLI

Manage Rocketlane Professional Services Automation via the `rocketlane` CLI tool.

**Binary location:** `/Users/austinsomer/Library/Python/3.9/bin/rocketlane`
**Config:** `~/.rocketlane/config.json` (multi-instance, auto-created on first run)

## IMPORTANT: Execution Rules

1. **Always use the full binary path** since it may not be on PATH:
   ```bash
   /Users/austinsomer/Library/Python/3.9/bin/rocketlane <command>
   ```
2. **Check active instance first** if the user is working across multiple RL accounts:
   ```bash
   /Users/austinsomer/Library/Python/3.9/bin/rocketlane instances
   ```
3. **Use `--json` for structured output** when you need to parse results or chain commands.
4. **Instance flag `-i`** lets you target a specific instance without switching:
   ```bash
   /Users/austinsomer/Library/Python/3.9/bin/rocketlane -i acme projects list
   ```

## Command Structure

```
rocketlane <resource> <action> [options]
```

## Available Resources

| Resource | Description |
|----------|-------------|
| projects | Create, update, delete, archive projects; manage members, templates, placeholders |
| tasks | CRUD tasks; manage assignees, followers, dependencies; move between phases |
| phases | Create, update, delete project phases |
| fields | Manage custom fields and dropdown options |
| users | List and view users |
| spaces | Manage workspaces |
| documents | CRUD documents within spaces |
| time | Log, update, delete time entries; view categories; search |
| time-offs | Create, view, delete time-off requests |
| allocations | View resource allocations |
| invoices | View invoices, payments, and line items |

## Instance Management

| Command | Description |
|---------|-------------|
| `add-instance` | Add a new Rocketlane instance (prompts for URL + API key, validates, saves) |
| `switch` | Interactive numbered menu to switch between saved instances |
| `instances` | Table of all configured instances (● = active) |
| `remove-instance NAME --yes` | Remove a saved instance |
| `status` | Check API connectivity for the active instance |

```bash
# First run — automatically prompts for instance URL + API key

# Add another instance
rocketlane add-instance
# Prompts: Instance URL (e.g. acme.rocketlane.com) → auto-derives short name "acme"
#          API Key → validates against the API, saves, sets as active

# List all instances (● marks active)
rocketlane instances

# Switch active instance (interactive numbered menu — no re-auth needed)
rocketlane switch

# Use a specific instance for one command without switching
rocketlane -i acme projects list

# Remove an instance
rocketlane remove-instance acme --yes
```

## Global Flags

| Flag | Description |
|------|-------------|
| `--json` | Output raw JSON (on most commands) |
| `--api-key TEXT` | Override API key for this invocation |
| `-i, --instance TEXT` | Use a specific instance by short name for this command |
| `--version` | Show CLI version |
| `--help` | Show help for any command |

## Projects

```bash
# List all projects
rocketlane projects list
rocketlane projects list --status "In progress" --limit 10

# Get project details
rocketlane projects get 201

# Create a project
rocketlane projects create --name "Acme Onboarding" --customer "Acme Inc" --owner "john@company.com"
rocketlane projects create --name "Beta Launch" --customer "Beta Corp" --owner "jane@company.com" --start-date 2026-04-01 --due-date 2026-06-30

# Update a project
rocketlane projects update 201 --name "Acme Onboarding v2" --status "In progress"

# Delete / Archive
rocketlane projects delete 201 --yes
rocketlane projects archive 201

# Members
rocketlane projects add-members 201 --emails "alice@company.com,bob@company.com"
rocketlane projects remove-members 201 --emails "bob@company.com"

# Templates
rocketlane projects import-template 201 --template-id 50

# Placeholders
rocketlane projects placeholders
rocketlane projects assign-placeholder 201 --placeholder-id 10 --user-email "alice@company.com"
rocketlane projects unassign-placeholder 201 --placeholder-id 10
```

## Tasks

```bash
# List tasks (with filters)
rocketlane tasks list
rocketlane tasks list --project-id 201 --status "In progress"

# Get task
rocketlane tasks get 501

# Create a task
rocketlane tasks create --project-id 201 --name "Kickoff Call" --due-date 2026-04-01 --effort 2.0
rocketlane tasks create --project-id 201 --name "Config Workshop" --phase-id 10 --description "Initial config session"

# Update
rocketlane tasks update 501 --status "Completed" --effort 3.5

# Delete
rocketlane tasks delete 501 --yes

# Assignees
rocketlane tasks assign 501 --emails "alice@company.com,bob@company.com"
rocketlane tasks unassign 501 --emails "bob@company.com"

# Followers
rocketlane tasks add-followers 501 --emails "manager@company.com"
rocketlane tasks remove-followers 501 --emails "manager@company.com"

# Dependencies
rocketlane tasks add-deps 501 --dep-ids "500,499"
rocketlane tasks remove-deps 501 --dep-ids "500"

# Move to different phase
rocketlane tasks move-to-phase 501 --phase-id 20
```

## Phases

```bash
rocketlane phases list --project-id 201
rocketlane phases get 10
rocketlane phases create --project-id 201 --name "Discovery" --start-date 2026-04-01
rocketlane phases update 10 --name "Discovery & Planning"
rocketlane phases delete 10 --yes
```

## Time Tracking

```bash
# Log time
rocketlane time create --task-id 501 --hours 2.5 --date 2026-03-24 --description "Kickoff prep"
rocketlane time create --project-id 201 --hours 1.0 --date 2026-03-24 --category "Internal"

# List / search
rocketlane time list --project-id 201 --from-date 2026-03-01 --to-date 2026-03-31
rocketlane time search --project-id 201 --user-id 100

# Update / delete
rocketlane time update 701 --hours 3.0
rocketlane time delete 701 --yes

# Categories
rocketlane time categories
```

## Custom Fields

```bash
rocketlane fields list
rocketlane fields create --label "MRR" --type NUMBER --entity-type PROJECT
rocketlane fields update 301 --label "Monthly Recurring Revenue"
rocketlane fields add-option 301 --value "Enterprise" --label "Enterprise Tier"
rocketlane fields update-option 301 --option-id "opt1" --value "Enterprise Plus"
rocketlane fields delete 301 --yes
```

## Users

```bash
rocketlane users list
rocketlane users get 100
```

## Spaces & Documents

```bash
rocketlane spaces list
rocketlane spaces create --name "Engineering" --description "Engineering workspace"
rocketlane spaces update 401 --name "Engineering Hub"
rocketlane spaces delete 401 --yes

rocketlane documents list 401
rocketlane documents create 401 --title "Runbook" --content "Step 1: ..."
rocketlane documents update 401 601 --title "Updated Runbook"
rocketlane documents delete 401 601 --yes
```

## Time-Offs

```bash
rocketlane time-offs list --user-id 100
rocketlane time-offs create --user-email "alice@company.com" --from-date 2026-04-01 --to-date 2026-04-05
rocketlane time-offs delete 801 --yes
```

## Resource Allocations

```bash
rocketlane allocations list --project-id 201
rocketlane allocations list --user-id 100 --from-date 2026-04-01 --to-date 2026-06-30
```

## Invoices

```bash
rocketlane invoices list --project-id 201
rocketlane invoices get 901
rocketlane invoices payments 901
rocketlane invoices line-items 901
```

## JSON Output

Append `--json` to any command for machine-readable output:
```bash
rocketlane projects list --json
rocketlane tasks get 501 --json
```

## Common Workflows

```bash
# See all projects, then drill into tasks for one
rocketlane projects list --json | jq '.[].projectId'
rocketlane tasks list --project-id 5000000023535

# Create a project and immediately add a task
rocketlane projects create --name "New Client Onboarding" --customer "NewCo" --owner "austin@company.com"
# (grab project ID from output)
rocketlane tasks create --project-id <ID> --name "Kickoff Meeting" --due-date 2026-04-01

# Log time for today
rocketlane time create --task-id 501 --hours 1.5 --date 2026-03-24 --description "Client call"

# Switch to a different RL instance and list its projects
rocketlane -i globex projects list
```

## Important Notes

- All destructive operations (delete) require `--yes` confirmation
- Dates use YYYY-MM-DD format
- Email lists are comma-separated (no spaces around commas)
- Config stored at `~/.rocketlane/config.json` — supports multiple instances
- Use `--json` flag for piping output to other tools (jq, etc.)
- Each team member maintains their own instance list (config is per-user)

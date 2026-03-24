#!/usr/bin/env bash
#
# Rocketlane CLI — Environment Setup & Validator
# Run: bash setup.sh
#

set -euo pipefail

# ── Colors ───────────────────────────────────────────────────────────────────
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
DIM='\033[2m'
BOLD='\033[1m'
RESET='\033[0m'

pass()  { echo -e "  ${GREEN}✓${RESET} $1"; }
warn()  { echo -e "  ${YELLOW}⚠${RESET} $1"; }
fail()  { echo -e "  ${RED}✗${RESET} $1"; }
info()  { echo -e "  ${BLUE}●${RESET} $1"; }
step()  { echo -e "\n${CYAN}${BOLD}$1${RESET}"; }

ERRORS=0
WARNINGS=0

# ── Banner ───────────────────────────────────────────────────────────────────
echo ""
echo -e "${BLUE}${BOLD}"
echo "  ╔══════════════════════════════════════════╗"
echo "  ║        Rocketlane CLI Setup              ║"
echo "  ║        Environment Validator             ║"
echo "  ╚══════════════════════════════════════════╝"
echo -e "${RESET}"

# ── 1. OS Detection ─────────────────────────────────────────────────────────
step "1. System"

OS="$(uname -s)"
ARCH="$(uname -m)"
info "OS: ${OS} (${ARCH})"

if [[ "$OS" == "Darwin" ]]; then
    info "macOS $(sw_vers -productVersion 2>/dev/null || echo 'unknown')"
elif [[ "$OS" == "Linux" ]]; then
    info "Linux $(uname -r)"
else
    warn "Untested OS: ${OS} — CLI may still work"
    ((WARNINGS++))
fi

# ── 2. Git ───────────────────────────────────────────────────────────────────
step "2. Git"

if command -v git &>/dev/null; then
    GIT_VERSION=$(git --version | awk '{print $3}')
    pass "git ${GIT_VERSION}"
else
    fail "git not found"
    echo ""
    if [[ "$OS" == "Darwin" ]]; then
        echo -e "    Install with: ${BOLD}xcode-select --install${RESET}"
        echo -e "    Or:           ${BOLD}brew install git${RESET}"
    else
        echo -e "    Install with: ${BOLD}sudo apt install git${RESET}  (Debian/Ubuntu)"
        echo -e "    Or:           ${BOLD}sudo yum install git${RESET}  (RHEL/CentOS)"
    fi
    ((ERRORS++))
fi

# ── 3. Python ────────────────────────────────────────────────────────────────
step "3. Python"

PYTHON_CMD=""
MIN_MAJOR=3
MIN_MINOR=9

# Try python3 first, then python
for cmd in python3 python; do
    if command -v "$cmd" &>/dev/null; then
        PY_VERSION=$("$cmd" --version 2>&1 | awk '{print $2}')
        PY_MAJOR=$(echo "$PY_VERSION" | cut -d. -f1)
        PY_MINOR=$(echo "$PY_VERSION" | cut -d. -f2)

        if [[ "$PY_MAJOR" -ge "$MIN_MAJOR" && "$PY_MINOR" -ge "$MIN_MINOR" ]]; then
            PYTHON_CMD="$cmd"
            pass "${cmd} ${PY_VERSION} (>= ${MIN_MAJOR}.${MIN_MINOR} required)"
            break
        else
            warn "${cmd} ${PY_VERSION} found but ${MIN_MAJOR}.${MIN_MINOR}+ required"
        fi
    fi
done

if [[ -z "$PYTHON_CMD" ]]; then
    fail "Python ${MIN_MAJOR}.${MIN_MINOR}+ not found"
    echo ""
    if [[ "$OS" == "Darwin" ]]; then
        echo -e "    Install with: ${BOLD}brew install python@3.12${RESET}"
        echo -e "    Or:           ${BOLD}xcode-select --install${RESET} (includes Python 3.9)"
    else
        echo -e "    Install with: ${BOLD}sudo apt install python3${RESET}  (Debian/Ubuntu)"
        echo -e "    Or:           ${BOLD}sudo yum install python3${RESET}  (RHEL/CentOS)"
    fi
    ((ERRORS++))
fi

# ── 4. pip ───────────────────────────────────────────────────────────────────
step "4. pip"

PIP_CMD=""
for cmd in pip3 pip; do
    if command -v "$cmd" &>/dev/null; then
        PIP_VERSION=$("$cmd" --version 2>&1 | awk '{print $2}')
        PIP_CMD="$cmd"
        pass "${cmd} ${PIP_VERSION}"
        break
    fi
done

# Also check python -m pip
if [[ -z "$PIP_CMD" && -n "$PYTHON_CMD" ]]; then
    if "$PYTHON_CMD" -m pip --version &>/dev/null; then
        PIP_VERSION=$("$PYTHON_CMD" -m pip --version 2>&1 | awk '{print $2}')
        PIP_CMD="$PYTHON_CMD -m pip"
        pass "python -m pip ${PIP_VERSION}"
    fi
fi

if [[ -z "$PIP_CMD" ]]; then
    fail "pip not found"
    echo ""
    if [[ -n "$PYTHON_CMD" ]]; then
        echo -e "    Install with: ${BOLD}${PYTHON_CMD} -m ensurepip --upgrade${RESET}"
    else
        echo -e "    Install Python first, pip is usually included"
    fi
    ((ERRORS++))
fi

# ── 5. Rocketlane CLI ───────────────────────────────────────────────────────
step "5. Rocketlane CLI"

RL_CMD=""
if command -v rocketlane &>/dev/null; then
    RL_VERSION=$(rocketlane --version 2>&1 | tail -1)
    RL_CMD="rocketlane"
    pass "rocketlane installed (${RL_VERSION})"
else
    # Check common pip install locations
    for candidate in \
        "$HOME/Library/Python/3.9/bin/rocketlane" \
        "$HOME/Library/Python/3.10/bin/rocketlane" \
        "$HOME/Library/Python/3.11/bin/rocketlane" \
        "$HOME/Library/Python/3.12/bin/rocketlane" \
        "$HOME/.local/bin/rocketlane"; do
        if [[ -x "$candidate" ]]; then
            RL_VERSION=$("$candidate" --version 2>&1 | tail -1)
            RL_CMD="$candidate"
            pass "Found at ${candidate} (${RL_VERSION})"
            warn "Not on PATH — add to your shell profile:"
            echo -e "    ${BOLD}export PATH=\"$(dirname "$candidate"):\$PATH\"${RESET}"
            echo ""
            ((WARNINGS++))
            break
        fi
    done

    if [[ -z "$RL_CMD" ]]; then
        info "Not installed yet"
        echo ""
        echo -e "    Install with: ${BOLD}pip install -e .${RESET}  (from this directory)"
    fi
fi

# ── 6. Rocketlane Config ────────────────────────────────────────────────────
step "6. Rocketlane Config"

CONFIG_FILE="$HOME/.rocketlane/config.json"
if [[ -f "$CONFIG_FILE" ]]; then
    INSTANCE_COUNT=0
    if command -v python3 &>/dev/null; then
        INSTANCE_COUNT=$(python3 -c "
import json
try:
    cfg = json.load(open('$CONFIG_FILE'))
    instances = cfg.get('instances', {})
    print(len(instances))
except:
    print(0)
" 2>/dev/null)
    fi

    if [[ "$INSTANCE_COUNT" -gt 0 ]]; then
        pass "${INSTANCE_COUNT} instance(s) configured"
        # Show active
        if command -v python3 &>/dev/null; then
            ACTIVE=$(python3 -c "
import json
try:
    cfg = json.load(open('$CONFIG_FILE'))
    print(cfg.get('active', 'none'))
except:
    print('unknown')
" 2>/dev/null)
            info "Active instance: ${BOLD}${ACTIVE}${RESET}"
        fi
    else
        info "Config exists but no instances configured"
        echo -e "    Run: ${BOLD}rocketlane add-instance${RESET}"
    fi
else
    info "No config yet — will be created on first run"
    echo -e "    Run: ${BOLD}rocketlane status${RESET} to start setup"
fi

# ── 7. Claude Code Skill (optional) ─────────────────────────────────────────
step "7. Claude Code Skill (optional)"

SKILL_FILE="$HOME/.claude/commands/rocketlane.md"
if [[ -f "$SKILL_FILE" ]]; then
    pass "Skill installed at ${SKILL_FILE}"
else
    info "Not installed"
    echo -e "    Copy with: ${BOLD}cp skills/rocketlane.md ~/.claude/commands/rocketlane.md${RESET}"
    echo -e "    ${DIM}Then update the binary path inside the file${RESET}"
fi

# ── Summary ──────────────────────────────────────────────────────────────────
echo ""
echo -e "${BOLD}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${RESET}"

if [[ "$ERRORS" -eq 0 && "$WARNINGS" -eq 0 ]]; then
    echo -e "${GREEN}${BOLD}  All checks passed! You're good to go.${RESET}"
elif [[ "$ERRORS" -eq 0 ]]; then
    echo -e "${YELLOW}${BOLD}  ${WARNINGS} warning(s) — see above for recommendations.${RESET}"
else
    echo -e "${RED}${BOLD}  ${ERRORS} issue(s) found — fix the items marked ✗ above.${RESET}"
    if [[ "$WARNINGS" -gt 0 ]]; then
        echo -e "${YELLOW}  Plus ${WARNINGS} warning(s).${RESET}"
    fi
fi

echo ""

# ── Auto-install prompt ─────────────────────────────────────────────────────
if [[ -z "$RL_CMD" && -n "$PIP_CMD" && "$ERRORS" -eq 0 ]]; then
    SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
    if [[ -f "$SCRIPT_DIR/pyproject.toml" ]]; then
        echo -e "${CYAN}${BOLD}  Ready to install Rocketlane CLI?${RESET}"
        echo ""
        read -p "  Install now? (y/n) " -n 1 -r
        echo ""
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            echo ""
            info "Installing..."
            (cd "$SCRIPT_DIR" && $PIP_CMD install -e .)
            echo ""

            # Check if it landed on PATH
            if command -v rocketlane &>/dev/null; then
                pass "Installed! Run: ${BOLD}rocketlane status${RESET}"
            else
                # Find where it installed
                RL_BIN=$(find "$HOME/Library/Python" "$HOME/.local/bin" -name rocketlane -type f 2>/dev/null | head -1)
                if [[ -n "$RL_BIN" ]]; then
                    pass "Installed at ${RL_BIN}"
                    BIN_DIR=$(dirname "$RL_BIN")
                    warn "Add to PATH:"
                    echo ""
                    echo -e "    ${BOLD}echo 'export PATH=\"${BIN_DIR}:\$PATH\"' >> ~/.zshrc && source ~/.zshrc${RESET}"
                else
                    pass "Installed! You may need to find the binary location."
                fi
            fi
            echo ""
        fi
    fi
fi

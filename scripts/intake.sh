#!/usr/bin/env bash
# barenode Intake Valve
# ======================
# Run on first load to intake credentials and configure the environment.
# The agent runs this automatically via AGENTS.md instructions.
#
# Usage:
#   source scripts/intake.sh   (preferred — sources into current shell)
#   bash scripts/intake.sh     (runs in subshell — env vars won't persist)

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
cd "$PROJECT_DIR"

echo "=== barenode Intake Valve ==="
echo ""

# ------------------------------------------------------------------
# 1. Environment files
# ------------------------------------------------------------------
if [ -f .env ]; then
    echo "[✓] .env found — sourcing..."
    set -a
    source .env
    set +a
else
    echo "[ ] .env not found. Copy .env.example to .env to configure providers."
fi

# ------------------------------------------------------------------
# 2. GitHub authentication
# ------------------------------------------------------------------
REMOTE_URL=$(git config --get remote.origin.url 2>/dev/null || echo "")

if echo "$REMOTE_URL" | grep -q "https://"; then
    if [ -n "$GITHUB_TOKEN" ]; then
        # Inject token into remote URL for this session
        REPO_URL=$(echo "$REMOTE_URL" | sed 's|https://github.com/||')
        git remote set-url origin "https://oauth2:${GITHUB_TOKEN}@github.com/${REPO_URL}"
        echo "[✓] GitHub token configured via remote URL"
    elif git credential fill <<< "protocol=https host=github.com" >/dev/null 2>&1; then
        echo "[✓] GitHub credentials available via credential helper"
    else
        echo "[ ] No GitHub token found."
        echo "    To push: export GITHUB_TOKEN=ghp_... or set up SSH"
    fi
elif echo "$REMOTE_URL" | grep -q "git@"; then
    if ssh -T git@github.com 2>&1 | grep -q "successfully authenticated"; then
        echo "[✓] GitHub SSH key authenticated"
    else
        echo "[!] SSH remote configured but authentication failed"
    fi
fi

# ------------------------------------------------------------------
# 3. Provider availability
# ------------------------------------------------------------------
if command -v ollama &>/dev/null; then
    echo "[✓] Ollama available"
else
    echo "[ ] Ollama not installed"
fi

if [ -n "$OPENROUTER_API_KEY" ]; then
    echo "[✓] OpenRouter API key configured"
else
    echo "[ ] OpenRouter API key not set"
fi

# ------------------------------------------------------------------
# 4. Check for required Python environment
# ------------------------------------------------------------------
if [ -d .venv ]; then
    echo "[✓] Python virtual environment exists"
else
    echo "[ ] No .venv — run 'uv sync' to create one"
fi

echo ""
echo "=== Intake complete ==="
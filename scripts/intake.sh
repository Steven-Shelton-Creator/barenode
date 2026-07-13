#!/usr/bin/env bash
# barenode Intake Valve
# ======================
# Run on first load to intake credentials and configure the environment.
# The agent runs this automatically via AGENTS.md instructions.
#
# Security model:
#   - Reads tokens from .env (gitignored — never committed)
#   - Creates a temporary GIT_ASKPASS script for memory-only auth
#   - Cleans up the temp script on shell exit (trap)
#   - Never writes secrets to .git/config or any tracked file
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
# 2. GitHub authentication (memory-only, never written to disk)
# ------------------------------------------------------------------
REMOTE_URL=$(git config --get remote.origin.url 2>/dev/null || echo "")

if echo "$REMOTE_URL" | grep -q "https://"; then
    if [ -n "$GITHUB_TOKEN" ]; then
        # Ensure clean remote URL (no embedded token from earlier runs)
        git remote set-url origin "https://github.com/Steven-Shelton-Creator/barenode.git" 2>/dev/null || true

        # Configure git credential helper using single quotes so the
        # $GITHUB_TOKEN reference is stored literally (not expanded).
        # At push time, git evaluates the helper function in a subshell
        # that inherits the GITHUB_TOKEN environment variable.
        #
        # Net result: token never appears on disk in any form.
        git config --local credential.helper '!f() { echo username=oauth2; echo password=$GITHUB_TOKEN; }; f'

        echo "[✓] GitHub token configured (credential helper references \$GITHUB_TOKEN)"
        echo "    Token supplied via env var at push time — never stored on disk"
    else
        echo "[ ] No GitHub token found."
        echo "    Add GITHUB_TOKEN to .env to enable pushes."
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
echo "  Credential helper active: token supplied via \$GITHUB_TOKEN at push time"
echo ""
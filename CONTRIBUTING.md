# Contributing

## Development Workflow

Every phase follows the same pattern:

1. **Read** the documentation (`ARCHITECTURE.md`, `BUILD_PLAN.md`, current phase doc)
2. **Create** a feature branch from `develop`:
   ```bash
   git checkout develop
   git checkout -b feature/CHXX-description
   ```
3. **Implement** only that phase — no unrelated refactoring
4. **Run tests**:
   ```bash
   uv run verify
   ```
5. **Update** documentation if architecture changed
6. **Commit** with a focused message:
   ```bash
   git commit -m "CHXX: implement <primitive>"
   ```
7. **Merge** into `develop`:
   ```bash
   git checkout develop
   git merge feature/CHXX-description
   ```

## Commit Style

Each commit represents one meaningful unit of work:

```
CH01: add bare model call with REPL
CH02: implement conversation history
CH03: add system instruction loader
CH04: implement context injection
CH05: add tool registry
...
```

## Branch Strategy

```
main             — stable, released
develop          — integration branch
feature/CHXX-*   — one per primitive
```

## Prerequisites

- Python 3.11+
- [uv](https://docs.astral.sh/uv/) — `curl -LsSf https://astral.sh/uv/install.sh | sh`

## Getting Started

```bash
git clone <repo-url> barenode
cd barenode
uv sync
uv run agent
```
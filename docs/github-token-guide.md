# Fine-Grained GitHub Personal Access Token Guide

Use this when you need to give an AI agent or automated tool access to **a single specific repository** without risking your entire GitHub account.

---

## Step 1: Navigate to Developer Settings

1. Click your profile picture in the top-right corner of GitHub.
2. Click **Settings**.
3. Scroll all the way down the left sidebar and click **Developer settings**.

## Step 2: Open Fine-grained Tokens

1. In the left sidebar, expand **Personal access tokens**.
2. Click **Fine-grained tokens**.
3. Click **Generate new token**.

## Step 3: Configure Repository Isolation

- **Token name**: Give it a clear name (e.g., `coding-agent-token`).
- **Expiration**: Select a reasonable window (e.g., 30 or 90 days). Avoid "No expiration."
- **Repository access**: Change from "All repositories" to **Only selected repositories**.
- **Select repositories**: Use the dropdown to choose the exact repository your agent needs.

## Step 4: Grant Permissions (Least Privilege)

Under **Repository permissions**, grant only what's strictly required:

| Permission       | Setting        | Why                                      |
|------------------|----------------|------------------------------------------|
| **Contents**     | Read and write | View files, pull code, push commits      |
| **Pull requests**| Read and write | Open PRs for review                      |
| **Metadata**     | Read-only      | Required — auto-set, always on           |

## Step 5: Save the Token

1. Scroll to the bottom and click **Generate token**.
2. **Copy the token immediately** — you will not be able to see it again.
3. Paste it into your agent's configuration file or environment variables.

> **Safety note:** Treat this token like a password. Never commit it to a repository or share it.
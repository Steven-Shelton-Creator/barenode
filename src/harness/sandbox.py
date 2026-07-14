"""Sandbox — Docker isolation / scrubbed local subprocess (CH08).

All command execution runs through the sandbox.  The harness controls
one chokepoint for all external execution.

Design
------
- **Docker mode** (preferred): Isolated container with no network,
  non-root user, read-only rootfs, memory/process caps.
- **Local fallback**: Scrub the environment and run in a subprocess
  if Docker is not available.
"""

import os
import shutil
import subprocess
import sys
import time
from dataclasses import dataclass, field


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

# Docker image to use for the sandbox container
SANDBOX_IMAGE = "alpine:latest"

# Resource limits (Docker mode)
SANDBOX_MEMORY = "256m"
SANDBOX_PIDS_LIMIT = 50
SANDBOX_USER = "1000:1000"

# Timeout for a single command (seconds)
SANDBOX_TIMEOUT = 30

# Fallback environment for local subprocess mode
_FALLBACK_ENV = {
    "PATH": "/usr/local/bin:/usr/bin:/bin",
    "HOME": "/tmp",
    "SHELL": "/bin/sh",
    "USER": "nobody",
}


# ---------------------------------------------------------------------------
# Result type
# ---------------------------------------------------------------------------

@dataclass
class SandboxResult:
    """Result of a sandboxed command execution.

    Attributes
    ----------
    stdout : str
        Standard output from the command.
    stderr : str
        Standard error from the command.
    exit_code : int
        Exit code of the command.
    duration : float
        Execution time in seconds.
    method : str
        Which execution method was used (``"docker"`` or ``"local"``).
    """

    stdout: str = ""
    stderr: str = ""
    exit_code: int = 0
    duration: float = 0.0
    method: str = "unknown"


# ---------------------------------------------------------------------------
# Sandbox
# ---------------------------------------------------------------------------

class Sandbox:
    """Sandboxed command execution provider.

    The sandbox tries Docker first and falls back to a scrubbed local
    subprocess if Docker is unavailable.
    """

    def __init__(self, workspace: str | None = None) -> None:
        self.workspace = workspace or os.getcwd()
        self._docker_available: bool | None = None

    def check(self) -> bool:
        """Check whether Docker is available.

        Returns
        -------
        bool
            ``True`` if Docker is installed and the sandbox image exists.
        """
        if self._docker_available is not None:
            return self._docker_available

        # Check Docker binary
        if not shutil.which("docker"):
            self._docker_available = False
            return False

        # Check if we can run Docker
        try:
            result = subprocess.run(
                ["docker", "info", "--format", "{{.ServerVersion}}"],
                capture_output=True,
                text=True,
                timeout=10,
            )
            if result.returncode != 0:
                self._docker_available = False
                return False
        except (subprocess.TimeoutExpired, FileNotFoundError, OSError):
            self._docker_available = False
            return False

        # Check the sandbox image exists
        try:
            img_result = subprocess.run(
                ["docker", "image", "ls", "--format", "{{.Repository}}:{{.Tag}}", SANDBOX_IMAGE],
                capture_output=True,
                text=True,
                timeout=10,
            )
            self._docker_available = SANDBOX_IMAGE in img_result.stdout
        except (subprocess.TimeoutExpired, OSError):
            self._docker_available = False

        return self._docker_available

    def run(self, command: str, workdir: str | None = None) -> SandboxResult:
        """Run a command inside the sandbox.

        Parameters
        ----------
        command : str
            The shell command to execute.
        workdir : str or None
            Working directory inside the sandbox.  Defaults to the
            workspace directory.

        Returns
        -------
        SandboxResult
            The result of the execution.
        """
        if workdir is None:
            workdir = self.workspace

        start = time.time()

        if self.check():
            result = self._run_docker(command, workdir)
        else:
            result = self._run_local(command, workdir)

        result.duration = time.time() - start
        return result

    def _run_docker(self, command: str, workdir: str) -> SandboxResult:
        """Run a command inside a Docker container."""
        # Build the command to run inside the container
        # We cd to the workdir first, then run the user's command
        inner_cmd = f"cd /workspace && {{ {command}; }}"

        cmd = [
            "docker", "run", "--rm", "-i",
            "--network", "none",
            "--read-only",
            "--tmpfs", "/tmp:noexec,nosuid,size=64m",
            "--user", SANDBOX_USER,
            "--memory", SANDBOX_MEMORY,
            "--pids-limit", str(SANDBOX_PIDS_LIMIT),
            "-v", f"{workdir}:/workspace:rw",
            SANDBOX_IMAGE,
            "sh", "-c", inner_cmd,
        ]

        try:
            proc = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=SANDBOX_TIMEOUT,
            )
            return SandboxResult(
                stdout=proc.stdout,
                stderr=proc.stderr,
                exit_code=proc.returncode,
                method="docker",
            )
        except subprocess.TimeoutExpired:
            return SandboxResult(
                stdout="",
                stderr=f"[sandbox] Command timed out after {SANDBOX_TIMEOUT}s.",
                exit_code=-1,
                method="docker",
            )
        except OSError as exc:
            return SandboxResult(
                stdout="",
                stderr=f"[sandbox] Execution error: {exc}",
                exit_code=-1,
                method="docker",
            )

    def _run_local(self, command: str, workdir: str) -> SandboxResult:
        """Run a command in a scrubbed local subprocess (fallback)."""
        try:
            proc = subprocess.run(
                command,
                shell=True,
                cwd=workdir,
                env=_FALLBACK_ENV,
                capture_output=True,
                text=True,
                timeout=SANDBOX_TIMEOUT,
            )
            return SandboxResult(
                stdout=proc.stdout,
                stderr=proc.stderr,
                exit_code=proc.returncode,
                method="local",
            )
        except subprocess.TimeoutExpired:
            return SandboxResult(
                stdout="",
                stderr=f"[sandbox] Command timed out after {SANDBOX_TIMEOUT}s.",
                exit_code=-1,
                method="local",
            )
        except OSError as exc:
            return SandboxResult(
                stdout="",
                stderr=f"[sandbox] Execution error: {exc}",
                exit_code=-1,
                method="local",
            )

    def __repr__(self) -> str:
        docker_status = "available" if self._docker_available else "unavailable"
        return f"Sandbox(workspace={self.workspace!r}, docker={docker_status})"
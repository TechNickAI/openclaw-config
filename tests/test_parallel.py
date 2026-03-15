"""Tests for Parallel.ai skill wrapper.

The parallel skill is a thin bash wrapper around the official parallel-cli.
These tests verify the wrapper behavior (auto-install logic, passthrough).
Integration tests require both parallel-cli installed and PARALLEL_API_KEY set.
"""

import os
import subprocess
from pathlib import Path

import pytest

SKILL_PATH = str(Path(__file__).parent / ".." / "skills" / "parallel" / "parallel")

try:
    HAS_CLI = (
        subprocess.run(
            ["parallel-cli", "--version"],
            capture_output=True,
            check=False,
        ).returncode
        == 0
    )
except FileNotFoundError:
    HAS_CLI = False

HAS_API_KEY = bool(os.getenv("PARALLEL_API_KEY"))

requires_cli = pytest.mark.skipif(
    not HAS_CLI,
    reason="parallel-cli not installed",
)

requires_api_key = pytest.mark.skipif(
    not HAS_API_KEY,
    reason="PARALLEL_API_KEY not set - skipping integration tests",
)


def run_skill(*args: str, env: dict | None = None) -> subprocess.CompletedProcess:
    """Run the parallel skill wrapper with given arguments."""
    cmd = ["bash", SKILL_PATH, *args]
    run_env = os.environ.copy()
    if env:
        run_env.update(env)
    return subprocess.run(
        cmd,
        check=False,
        capture_output=True,
        text=True,
        env=run_env,
    )


class TestWrapper:
    """Tests for the bash wrapper itself."""

    def test_skill_is_executable(self):
        """Skill script exists and is executable."""
        path = Path(SKILL_PATH)
        assert path.exists()
        assert os.access(path, os.X_OK)

    def test_skill_is_bash(self):
        """Skill script is a bash script, not Python."""
        with Path(SKILL_PATH).open() as f:
            first_line = f.readline()
        assert "bash" in first_line


@requires_cli
class TestPassthrough:
    """Tests that verify the wrapper passes through to parallel-cli."""

    def test_help_passthrough(self):
        """Wrapper passes help/version commands through."""
        result = run_skill("--version")
        assert result.returncode == 0

    def test_search_without_key_fails_fast(self):
        """Wrapper catches missing API key before hitting CLI (prevents interactive hang)."""
        result = run_skill("search", "test query", env={"PARALLEL_API_KEY": ""})
        assert result.returncode != 0
        assert "PARALLEL_API_KEY" in result.stderr


@requires_cli
@requires_api_key
class TestSearchIntegration:
    """Integration tests for search via the wrapper."""

    def test_search_returns_results(self):
        """Basic search returns output."""
        result = run_skill("search", "python programming", "--max-results", "2")
        assert result.returncode == 0
        assert result.stdout.strip()

    def test_search_json_output(self):
        """Search with --json returns structured output."""
        result = run_skill(
            "search", "python programming", "--max-results", "1", "--json"
        )
        assert result.returncode == 0
        assert "{" in result.stdout


@requires_cli
@requires_api_key
class TestExtractIntegration:
    """Integration tests for extract via the wrapper."""

    def test_extract_basic_url(self):
        """Extract content from a simple URL."""
        result = run_skill("extract", "https://example.com")
        assert result.returncode == 0
        assert result.stdout.strip()

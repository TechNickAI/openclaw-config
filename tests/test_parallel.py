"""Tests for Parallel.ai skill.

Integration tests require PARALLEL_API_KEY environment variable.
Tests auto-skip if the key is not available.
"""

import os
import subprocess
from pathlib import Path

import pytest

# Path to the skill script
SKILL_PATH = str(Path(__file__).parent / ".." / "skills" / "parallel" / "parallel")

# Skip integration tests if no API key
HAS_API_KEY = bool(os.getenv("PARALLEL_API_KEY"))
requires_api_key = pytest.mark.skipif(
    not HAS_API_KEY,
    reason="PARALLEL_API_KEY not set - skipping integration tests",
)


def run_skill(*args: str, env: dict | None = None) -> subprocess.CompletedProcess:
    """Run the parallel skill with given arguments."""
    cmd = ["uv", "run", SKILL_PATH, *args]
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


class TestHelp:
    """Tests for help command - no API key required."""

    def test_help_shows_usage(self):
        """Help command shows usage information."""
        # Run without API key to test help works standalone
        result = run_skill("help", env={"PARALLEL_API_KEY": ""})

        # Help should work even without API key
        assert result.returncode == 0
        assert "Parallel.ai" in result.stdout
        assert "search" in result.stdout
        assert "extract" in result.stdout

    def test_no_args_shows_help(self):
        """Running with no arguments shows help."""
        result = run_skill(env={"PARALLEL_API_KEY": ""})

        assert result.returncode == 0
        assert "Commands:" in result.stdout


class TestValidation:
    """Tests for input validation - no API key required."""

    def test_search_requires_query(self):
        """Search without query shows error."""
        result = run_skill("search", env={"PARALLEL_API_KEY": "fake-key"})

        assert result.returncode != 0
        assert (
            "query required" in result.stderr.lower()
            or "query required" in result.stdout.lower()
        )

    def test_extract_requires_url(self):
        """Extract without URL shows error."""
        result = run_skill("extract", env={"PARALLEL_API_KEY": "fake-key"})

        assert result.returncode != 0
        assert (
            "url required" in result.stderr.lower()
            or "url required" in result.stdout.lower()
        )

    def test_extract_validates_url_format(self):
        """Extract rejects invalid URLs."""
        result = run_skill("extract", "not-a-url", env={"PARALLEL_API_KEY": "fake-key"})

        assert result.returncode != 0
        assert "http" in result.stderr.lower() or "url" in result.stderr.lower()

    def test_limit_must_be_numeric(self):
        """--limit flag requires a number."""
        result = run_skill(
            "search", "test", "--limit", "abc", env={"PARALLEL_API_KEY": "fake-key"}
        )

        assert result.returncode != 0
        assert "limit" in result.stderr.lower() or "number" in result.stderr.lower()

    def test_missing_api_key_shows_error(self):
        """Missing API key shows helpful error."""
        result = run_skill("search", "test", env={"PARALLEL_API_KEY": ""})

        assert result.returncode != 0
        assert "PARALLEL_API_KEY" in result.stderr

    def test_limit_must_be_positive(self):
        """--limit rejects zero and negative values."""
        result = run_skill(
            "search", "test", "--limit", "0", env={"PARALLEL_API_KEY": "fake-key"}
        )
        assert result.returncode != 0
        assert "positive" in result.stderr.lower()

        result = run_skill(
            "search", "test", "--limit", "-5", env={"PARALLEL_API_KEY": "fake-key"}
        )
        assert result.returncode != 0

    def test_limit_requires_value(self):
        """--limit at end of args without value shows error."""
        result = run_skill(
            "search", "test", "--limit", env={"PARALLEL_API_KEY": "fake-key"}
        )
        assert result.returncode != 0
        assert "limit" in result.stderr.lower()

    def test_unknown_command_shows_error(self):
        """Unknown command shows error, not help."""
        result = run_skill("typo", env={"PARALLEL_API_KEY": "fake-key"})
        assert result.returncode != 0
        assert "unknown command" in result.stderr.lower()

    def test_raw_invalid_json(self):
        """Raw command rejects invalid JSON."""
        result = run_skill(
            "raw", "/search", "not-json", env={"PARALLEL_API_KEY": "fake-key"}
        )
        assert result.returncode != 0
        assert "json" in result.stderr.lower()


@requires_api_key
class TestSearchIntegration:
    """Integration tests for search - require API key."""

    def test_search_returns_results(self):
        """Basic search returns formatted results."""
        result = run_skill("search", "python programming", "--limit", "2")

        assert result.returncode == 0
        # Should have markdown formatted output
        assert "##" in result.stdout or "URL:" in result.stdout

    def test_search_with_limit(self):
        """Search respects --limit flag."""
        result = run_skill("search", "artificial intelligence", "--limit", "1")

        assert result.returncode == 0
        # Should return at least one result
        assert result.stdout.strip()


@requires_api_key
class TestExtractIntegration:
    """Integration tests for extract - require API key."""

    def test_extract_basic_url(self):
        """Extract content from a simple URL."""
        result = run_skill("extract", "https://example.com")

        assert result.returncode == 0
        # Should have some content
        assert result.stdout.strip()

    def test_extract_with_full_flag(self):
        """Extract with --full returns more content."""
        result = run_skill("extract", "https://example.com", "--full")

        assert result.returncode == 0
        assert result.stdout.strip()


@requires_api_key
class TestRawIntegration:
    """Integration tests for raw API calls - require API key."""

    def test_raw_search_endpoint(self):
        """Raw API call to search endpoint."""
        payload = '{"search_queries": ["test"], "max_results": 1}'
        result = run_skill("raw", "/search", payload)

        assert result.returncode == 0
        # Should return JSON
        assert "{" in result.stdout

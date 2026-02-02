"""Tests for Limitless skill.

Integration tests require LIMITLESS_API_KEY environment variable.
Tests auto-skip if the key is not available.
"""

import os
import subprocess

import pytest

# Path to the skill script
SKILL_PATH = os.path.join(
    os.path.dirname(__file__), "..", "skills", "limitless", "limitless"
)

# Skip integration tests if no API key
HAS_API_KEY = bool(os.getenv("LIMITLESS_API_KEY"))
requires_api_key = pytest.mark.skipif(
    not HAS_API_KEY,
    reason="LIMITLESS_API_KEY not set - skipping integration tests",
)


def run_skill(*args: str, env: dict | None = None) -> subprocess.CompletedProcess:
    """Run the limitless skill with given arguments."""
    cmd = ["uv", "run", SKILL_PATH, *args]
    run_env = os.environ.copy()
    if env:
        run_env.update(env)
    return subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        env=run_env,
    )


class TestHelp:
    """Tests for help command - no API key required."""

    def test_help_shows_usage(self):
        """Help command shows usage information."""
        result = run_skill("help", env={"LIMITLESS_API_KEY": ""})

        assert result.returncode == 0
        assert "Limitless" in result.stdout
        assert "recent" in result.stdout
        assert "search" in result.stdout

    def test_no_args_shows_help(self):
        """Running with no arguments shows help."""
        result = run_skill(env={"LIMITLESS_API_KEY": ""})

        assert result.returncode == 0
        assert "Commands:" in result.stdout


class TestValidation:
    """Tests for input validation - no API key required."""

    def test_missing_api_key_shows_error(self):
        """Missing API key shows helpful error."""
        result = run_skill("recent", env={"LIMITLESS_API_KEY": ""})

        assert result.returncode != 0
        assert "LIMITLESS_API_KEY" in result.stderr

    def test_search_requires_query(self):
        """Search without query shows error."""
        result = run_skill("search", env={"LIMITLESS_API_KEY": "fake-key"})

        assert result.returncode != 0
        assert "query" in result.stderr.lower()

    def test_date_requires_argument(self):
        """Date command without date shows error."""
        result = run_skill("date", env={"LIMITLESS_API_KEY": "fake-key"})

        assert result.returncode != 0
        assert "date" in result.stderr.lower()

    def test_date_validates_format(self):
        """Date command rejects invalid date format."""
        result = run_skill("date", "not-a-date", env={"LIMITLESS_API_KEY": "fake-key"})

        assert result.returncode != 0
        assert "YYYY-MM-DD" in result.stderr

    def test_get_requires_id(self):
        """Get command without ID shows error."""
        result = run_skill("get", env={"LIMITLESS_API_KEY": "fake-key"})

        assert result.returncode != 0
        assert "id" in result.stderr.lower()

    def test_unknown_command_shows_error(self):
        """Unknown command shows error."""
        result = run_skill("typo", env={"LIMITLESS_API_KEY": "fake-key"})

        assert result.returncode != 0
        assert "unknown command" in result.stderr.lower()

    def test_recent_limit_must_be_positive(self):
        """Recent with invalid limit shows error."""
        result = run_skill("recent", "0", env={"LIMITLESS_API_KEY": "fake-key"})

        assert result.returncode != 0
        assert "positive" in result.stderr.lower() or "1-10" in result.stderr.lower()

    def test_recent_limit_capped_at_10(self):
        """Recent with limit > 10 shows error (API max is 10)."""
        result = run_skill("recent", "20", env={"LIMITLESS_API_KEY": "fake-key"})

        assert result.returncode != 0
        assert "10" in result.stderr

    def test_audio_requires_start_and_end(self):
        """Audio command requires both start and end timestamps."""
        result = run_skill("audio", env={"LIMITLESS_API_KEY": "fake-key"})

        assert result.returncode != 0
        assert "start" in result.stderr.lower() or "usage" in result.stderr.lower()

    def test_audio_rejects_negative_timestamps(self):
        """Audio command rejects negative timestamps."""
        result = run_skill("audio", "-1000", "5000", env={"LIMITLESS_API_KEY": "fake-key"})

        assert result.returncode != 0
        assert "non-negative" in result.stderr.lower()

    def test_audio_duration_limit_enforced(self):
        """Audio command enforces 2-hour maximum."""
        result = run_skill("audio", "0", "10800000", env={"LIMITLESS_API_KEY": "fake-key"})

        assert result.returncode != 0
        assert "2-hour" in result.stderr.lower() or "maximum" in result.stderr.lower()

    def test_date_rejects_invalid_date(self):
        """Date command rejects semantically invalid dates."""
        result = run_skill("date", "2026-13-45", env={"LIMITLESS_API_KEY": "fake-key"})

        assert result.returncode != 0

    def test_chats_limit_must_be_positive(self):
        """Chats with limit 0 shows error."""
        result = run_skill("chats", "0", env={"LIMITLESS_API_KEY": "fake-key"})

        assert result.returncode != 0


@requires_api_key
class TestRecentIntegration:
    """Integration tests for recent - require API key."""

    def test_recent_returns_results(self):
        """Recent command returns formatted lifelogs."""
        result = run_skill("recent", "1")

        assert result.returncode == 0
        assert result.stdout.strip()

    def test_recent_default_limit(self):
        """Recent without limit uses default."""
        result = run_skill("recent")

        assert result.returncode == 0


@requires_api_key
class TestSearchIntegration:
    """Integration tests for search - require API key."""

    def test_search_returns_results(self):
        """Search command returns formatted results."""
        result = run_skill("search", "meeting")

        assert result.returncode == 0
        # May or may not have results depending on data

    def test_today_returns_results(self):
        """Today command runs successfully."""
        result = run_skill("today")

        assert result.returncode == 0


@requires_api_key
class TestChatsIntegration:
    """Integration tests for chats - require API key."""

    def test_chats_returns_results(self):
        """Chats command returns formatted results."""
        result = run_skill("chats")

        assert result.returncode == 0

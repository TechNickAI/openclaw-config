"""Tests for Follow Up Boss skill.

Integration tests require FUB_API_KEY environment variable.
Tests auto-skip if the key is not available.
"""

import os
import subprocess
from pathlib import Path

import pytest

SKILL_PATH = str(Path(__file__).parent / ".." / "skills" / "followupboss" / "followupboss")

HAS_API_KEY = bool(os.getenv("FUB_API_KEY"))
requires_api_key = pytest.mark.skipif(
    not HAS_API_KEY,
    reason="FUB_API_KEY not set - skipping integration tests",
)


def run_skill(*args: str, env: dict | None = None) -> subprocess.CompletedProcess:
    """Run the followupboss skill with given arguments."""
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
    """Tests that don't require an API key."""

    def test_help_shows_usage(self):
        result = run_skill("help")
        assert result.returncode == 0
        assert "Follow Up Boss CLI" in result.stdout
        assert "search" in result.stdout
        assert "get" in result.stdout
        assert "notes" in result.stdout
        assert "deals" in result.stdout

    def test_no_args_shows_help(self):
        result = run_skill()
        assert result.returncode == 0
        assert "Follow Up Boss CLI" in result.stdout


class TestValidation:
    """Input validation tests — no real API calls."""

    def test_missing_api_key_shows_error(self):
        result = run_skill("recent", env={"FUB_API_KEY": ""})
        assert result.returncode == 1
        assert "FUB_API_KEY" in result.stderr

    def test_search_requires_query(self):
        result = run_skill("search", env={"FUB_API_KEY": "fake-key"})
        assert result.returncode == 1
        assert "query required" in result.stderr.lower()

    def test_get_requires_id(self):
        result = run_skill("get", env={"FUB_API_KEY": "fake-key"})
        assert result.returncode == 1
        assert "Person ID required" in result.stderr

    def test_get_validates_id_is_number(self):
        result = run_skill("get", "abc", env={"FUB_API_KEY": "fake-key"})
        assert result.returncode == 1
        assert "must be a number" in result.stderr

    def test_notes_requires_person_id(self):
        result = run_skill("notes", env={"FUB_API_KEY": "fake-key"})
        assert result.returncode == 1
        assert "Person ID required" in result.stderr

    def test_add_note_requires_body(self):
        result = run_skill("add-note", "123", env={"FUB_API_KEY": "fake-key"})
        assert result.returncode == 1
        assert "body required" in result.stderr.lower()

    def test_add_task_requires_name(self):
        result = run_skill("add-task", "123", env={"FUB_API_KEY": "fake-key"})
        assert result.returncode == 1
        assert "task name required" in result.stderr.lower()

    def test_add_task_validates_date(self):
        result = run_skill("add-task", "123", "Call back", "not-a-date", env={"FUB_API_KEY": "fake-key"})
        assert result.returncode == 1
        assert "Invalid date" in result.stderr

    def test_recent_validates_limit(self):
        result = run_skill("recent", "999", env={"FUB_API_KEY": "fake-key"})
        assert result.returncode == 1
        assert "100" in result.stderr

    def test_unknown_command_shows_error(self):
        result = run_skill("bogus")
        assert result.returncode == 1
        assert "Unknown command" in result.stderr


@requires_api_key
class TestSearchIntegration:
    """Integration tests for search — requires FUB_API_KEY."""

    def test_search_by_name(self):
        result = run_skill("search", "test")
        assert result.returncode == 0
        # Should return markdown output (either contacts or "No contacts found")
        assert "contacts" in result.stdout.lower() or "no contacts" in result.stdout.lower()

    def test_recent_contacts(self):
        result = run_skill("recent", "3")
        assert result.returncode == 0


@requires_api_key
class TestResourcesIntegration:
    """Integration tests for read-only resources — requires FUB_API_KEY."""

    def test_users(self):
        result = run_skill("users")
        assert result.returncode == 0

    def test_stages(self):
        result = run_skill("stages")
        assert result.returncode == 0

    def test_deals(self):
        result = run_skill("deals", "3")
        assert result.returncode == 0

    def test_tasks(self):
        result = run_skill("tasks")
        assert result.returncode == 0

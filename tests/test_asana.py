"""Tests for Asana skill.

Integration tests require ASANA_ACCESS_TOKEN environment variable.
Tests auto-skip if the key is not available.
"""

import os
import subprocess
from pathlib import Path

import pytest

# Path to the skill script
SKILL_PATH = str(Path(__file__).parent / ".." / "skills" / "asana" / "asana")

# Skip integration tests if no API key
HAS_API_KEY = bool(os.getenv("ASANA_ACCESS_TOKEN"))
requires_api_key = pytest.mark.skipif(
    not HAS_API_KEY,
    reason="ASANA_ACCESS_TOKEN not set - skipping integration tests",
)


def run_skill(*args: str, env: dict | None = None) -> subprocess.CompletedProcess:
    """Run the asana skill with given arguments."""
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
        result = run_skill("help", env={"ASANA_ACCESS_TOKEN": ""})

        assert result.returncode == 0
        assert "Asana" in result.stdout
        assert "tasks" in result.stdout
        assert "comment" in result.stdout

    def test_no_args_shows_help(self):
        """Running with no arguments shows help."""
        result = run_skill(env={"ASANA_ACCESS_TOKEN": ""})

        assert result.returncode == 0
        assert "Commands:" in result.stdout


class TestValidation:
    """Tests for input validation - no API key required."""

    def test_missing_api_key_shows_error(self):
        """Missing API key shows helpful error."""
        result = run_skill("tasks", "123", env={"ASANA_ACCESS_TOKEN": ""})

        assert result.returncode != 0
        assert "ASANA_ACCESS_TOKEN" in result.stderr

    def test_tasks_requires_project_gid(self):
        """Tasks without project GID shows error."""
        result = run_skill("tasks", env={"ASANA_ACCESS_TOKEN": "fake-key"})

        assert result.returncode != 0
        assert "project" in result.stderr.lower()

    def test_tasks_in_section_requires_section_gid(self):
        """Tasks-in-section without section GID shows error."""
        result = run_skill("tasks-in-section", env={"ASANA_ACCESS_TOKEN": "fake-key"})

        assert result.returncode != 0
        assert "section" in result.stderr.lower()

    def test_move_requires_both_gids(self):
        """Move without both GIDs shows error."""
        result = run_skill("move", "123", env={"ASANA_ACCESS_TOKEN": "fake-key"})

        assert result.returncode != 0
        assert "section" in result.stderr.lower()

    def test_tag_requires_both_gids(self):
        """Tag without both GIDs shows error."""
        result = run_skill("tag", "123", env={"ASANA_ACCESS_TOKEN": "fake-key"})

        assert result.returncode != 0
        assert "tag" in result.stderr.lower()

    def test_untag_requires_both_gids(self):
        """Untag without both GIDs shows error."""
        result = run_skill("untag", "123", env={"ASANA_ACCESS_TOKEN": "fake-key"})

        assert result.returncode != 0
        assert "tag" in result.stderr.lower()

    def test_comment_requires_task_gid(self):
        """Comment without task GID shows error."""
        result = run_skill("comment", env={"ASANA_ACCESS_TOKEN": "fake-key"})

        assert result.returncode != 0
        assert "task" in result.stderr.lower()

    def test_comment_requires_text(self):
        """Comment without text shows error."""
        result = run_skill("comment", "123", env={"ASANA_ACCESS_TOKEN": "fake-key"})

        assert result.returncode != 0
        assert "text" in result.stderr.lower()

    def test_complete_requires_task_gid(self):
        """Complete without task GID shows error."""
        result = run_skill("complete", env={"ASANA_ACCESS_TOKEN": "fake-key"})

        assert result.returncode != 0
        assert "task" in result.stderr.lower()

    def test_sections_requires_project_gid(self):
        """Sections without project GID shows error."""
        result = run_skill("sections", env={"ASANA_ACCESS_TOKEN": "fake-key"})

        assert result.returncode != 0
        assert "project" in result.stderr.lower()

    def test_tags_requires_workspace_gid(self):
        """Tags without workspace GID shows error."""
        result = run_skill("tags", env={"ASANA_ACCESS_TOKEN": "fake-key"})

        assert result.returncode != 0
        assert "workspace" in result.stderr.lower()

    def test_create_requires_project_gid(self):
        """Create without project GID shows error."""
        result = run_skill("create", env={"ASANA_ACCESS_TOKEN": "fake-key"})

        assert result.returncode != 0
        assert "project" in result.stderr.lower()

    def test_create_requires_name(self):
        """Create without name shows error."""
        result = run_skill("create", "123", env={"ASANA_ACCESS_TOKEN": "fake-key"})

        assert result.returncode != 0
        assert "name" in result.stderr.lower()

    def test_unknown_command_shows_error(self):
        """Unknown command shows error."""
        result = run_skill("typo", env={"ASANA_ACCESS_TOKEN": "fake-key"})

        assert result.returncode != 0
        assert "unknown command" in result.stderr.lower()

    def test_gid_must_be_numeric(self):
        """Non-numeric GIDs are rejected."""
        result = run_skill(
            "tasks", "not-a-number", env={"ASANA_ACCESS_TOKEN": "fake-key"}
        )

        assert result.returncode != 0
        assert "numeric" in result.stderr.lower()

    def test_gid_rejects_path_traversal(self):
        """GIDs with path traversal characters are rejected."""
        result = run_skill("tasks", "../../etc", env={"ASANA_ACCESS_TOKEN": "fake-key"})

        assert result.returncode != 0
        assert "numeric" in result.stderr.lower()

    def test_move_validates_both_gids(self):
        """Move validates both task and section GIDs."""
        result = run_skill("move", "abc", "123", env={"ASANA_ACCESS_TOKEN": "fake-key"})

        assert result.returncode != 0
        assert "numeric" in result.stderr.lower()

        result = run_skill("move", "123", "abc", env={"ASANA_ACCESS_TOKEN": "fake-key"})

        assert result.returncode != 0
        assert "numeric" in result.stderr.lower()


# Use "100x Nick" project and "Carmenta Collective" workspace for integration tests
WORKSPACE_GID = "1195259077882228"
PROJECT_GID = "1211197449253083"


@requires_api_key
class TestTasksIntegration:
    """Integration tests for read-only task listing."""

    def test_tasks_returns_output(self):
        """Tasks command returns tab-separated output."""
        result = run_skill("tasks", PROJECT_GID)

        assert result.returncode == 0
        assert result.stdout.strip()

    def test_sections_returns_output(self):
        """Sections command lists project sections."""
        result = run_skill("sections", PROJECT_GID)

        assert result.returncode == 0
        assert result.stdout.strip()
        # Should have tab-separated GID and name
        assert "\t" in result.stdout

    def test_tags_returns_output(self):
        """Tags command lists workspace tags."""
        result = run_skill("tags", WORKSPACE_GID)

        assert result.returncode == 0
        assert result.stdout.strip()

    def test_invalid_project_gid_shows_api_error(self):
        """Invalid project GID returns a clear API error, not empty output."""
        result = run_skill("tasks", "999999999999999")

        assert result.returncode != 0
        assert "error" in result.stderr.lower()


@requires_api_key
class TestCreateCommentCompleteIntegration:
    """Integration tests for the create → comment → complete lifecycle."""

    def test_full_task_lifecycle(self):
        """Create a task, comment on it, and complete it."""
        # Create
        result = run_skill(
            "create", PROJECT_GID, "Integration test task — safe to delete"
        )
        assert result.returncode == 0
        assert "Created:" in result.stdout

        # Extract task GID from output
        task_gid = result.stdout.split("Created:")[1].strip().split(" ")[0]
        assert task_gid.isdigit()

        # Comment
        result = run_skill("comment", task_gid, "Automated test comment")
        assert result.returncode == 0
        assert "Comment added" in result.stdout

        # Complete
        result = run_skill("complete", task_gid)
        assert result.returncode == 0
        assert "Task completed" in result.stdout

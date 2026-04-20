"""Tests for HubSpot skill.

Integration tests require HUBSPOT_API_KEY environment variable.
Tests auto-skip if the key is not available.
"""

import os
import re
import subprocess
from pathlib import Path

import pytest

SKILL_PATH = str(Path(__file__).parent / ".." / "skills" / "hubspot" / "hubspot")

HAS_API_KEY = bool(os.getenv("HUBSPOT_API_KEY"))
requires_api_key = pytest.mark.skipif(
    not HAS_API_KEY,
    reason="HUBSPOT_API_KEY not set - skipping integration tests",
)


def run_skill(*args: str, env: dict | None = None) -> subprocess.CompletedProcess:
    """Run the hubspot skill with given arguments."""
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
    """Help output requires no API key."""

    def test_help_shows_commands(self):
        result = run_skill("help", env={"HUBSPOT_API_KEY": ""})
        assert result.returncode == 0
        assert "contacts" in result.stdout
        assert "deals" in result.stdout
        assert "stages" in result.stdout

    def test_no_args_shows_help(self):
        result = run_skill(env={"HUBSPOT_API_KEY": ""})
        assert result.returncode == 0
        assert "Commands:" in result.stdout

    def test_help_long_flag(self):
        result = run_skill("--help", env={"HUBSPOT_API_KEY": ""})
        assert result.returncode == 0
        assert "Commands:" in result.stdout

    def test_help_short_flag(self):
        result = run_skill("-h", env={"HUBSPOT_API_KEY": ""})
        assert result.returncode == 0
        assert "Commands:" in result.stdout

    def test_help_mentions_api_key_env(self):
        result = run_skill("help", env={"HUBSPOT_API_KEY": ""})
        assert "HUBSPOT_API_KEY" in result.stdout


class TestValidation:
    """Input validation — no API calls needed."""

    def test_missing_api_key_errors(self):
        result = run_skill("contacts", env={"HUBSPOT_API_KEY": ""})
        assert result.returncode != 0
        assert "HUBSPOT_API_KEY" in result.stderr

    def test_contact_requires_id(self):
        result = run_skill("contact", env={"HUBSPOT_API_KEY": "fake"})
        assert result.returncode != 0
        assert "ID" in result.stderr or "id" in result.stderr.lower()

    def test_deal_requires_id(self):
        result = run_skill("deal", env={"HUBSPOT_API_KEY": "fake"})
        assert result.returncode != 0
        assert "ID" in result.stderr or "id" in result.stderr.lower()

    def test_unknown_command_errors(self):
        result = run_skill("nope", env={"HUBSPOT_API_KEY": "fake"})
        assert result.returncode != 0
        assert "unknown command" in result.stderr.lower()

    def test_limit_must_be_numeric(self):
        result = run_skill(
            "contacts", "--limit", "abc", env={"HUBSPOT_API_KEY": "fake"}
        )
        assert result.returncode != 0
        assert "numeric" in result.stderr.lower()

    def test_limit_min_enforced(self):
        result = run_skill("contacts", "--limit", "0", env={"HUBSPOT_API_KEY": "fake"})
        assert result.returncode != 0
        assert "1" in result.stderr

    def test_limit_max_enforced(self):
        result = run_skill(
            "contacts", "--limit", "200", env={"HUBSPOT_API_KEY": "fake"}
        )
        assert result.returncode != 0
        assert "100" in result.stderr

    def test_limit_requires_value(self):
        result = run_skill("contacts", "--limit", env={"HUBSPOT_API_KEY": "fake"})
        assert result.returncode != 0

    def test_stages_rejects_extra_args(self):
        result = run_skill("stages", "unexpected", env={"HUBSPOT_API_KEY": "fake"})
        assert result.returncode != 0


@requires_api_key
class TestContactsIntegration:
    """Live HubSpot contacts — require API key."""

    def test_contacts_list(self):
        result = run_skill("contacts")
        assert result.returncode == 0
        assert result.stdout.strip()

    def test_contacts_with_limit(self):
        result = run_skill("contacts", "--limit", "3")
        assert result.returncode == 0
        assert result.stdout.strip()

    def test_contacts_search(self):
        result = run_skill("contacts", "a")
        assert result.returncode == 0

    def test_contact_by_id(self):
        search = run_skill("contacts", "--limit", "1")
        assert search.returncode == 0
        match = re.search(r"ID: (\d+)", search.stdout)
        if not match:
            pytest.skip("HubSpot portal has no contacts to exercise by-ID lookup")
        result = run_skill("contact", match.group(1))
        assert result.returncode == 0
        assert match.group(1) in result.stdout


@requires_api_key
class TestDealsIntegration:
    """Live HubSpot deals — require API key."""

    def test_deals_list(self):
        result = run_skill("deals")
        assert result.returncode == 0
        assert result.stdout.strip()

    def test_deals_with_limit(self):
        result = run_skill("deals", "--limit", "3")
        assert result.returncode == 0

    def test_deal_by_id(self):
        search = run_skill("deals", "--limit", "1")
        assert search.returncode == 0
        match = re.search(r"ID: (\d+)", search.stdout)
        if not match:
            pytest.skip("HubSpot portal has no deals to exercise by-ID lookup")
        result = run_skill("deal", match.group(1))
        assert result.returncode == 0
        assert match.group(1) in result.stdout


@requires_api_key
class TestStagesIntegration:
    """Live HubSpot pipelines and stages — require API key."""

    def test_stages_returns_results(self):
        result = run_skill("stages")
        assert result.returncode == 0
        assert result.stdout.strip()

    def test_stages_output_format(self):
        result = run_skill("stages")
        assert result.returncode == 0
        assert "##" in result.stdout

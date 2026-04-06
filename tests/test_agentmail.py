"""Tests for AgentMail skill.

Integration tests require AGENTMAIL_API_KEY environment variable.
Tests auto-skip if the key is not available.
"""

import json
import os
import subprocess
from pathlib import Path

import pytest

SKILL_PATH = str(Path(__file__).parent / ".." / "skills" / "agentmail" / "agentmail")

HAS_API_KEY = bool(os.getenv("AGENTMAIL_API_KEY"))
requires_api_key = pytest.mark.skipif(
    not HAS_API_KEY,
    reason="AGENTMAIL_API_KEY not set - skipping integration tests",
)


def run_skill(*args: str, env: dict | None = None) -> subprocess.CompletedProcess:
    """Run the agentmail skill with given arguments."""
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
        result = run_skill("help", env={"AGENTMAIL_API_KEY": ""})

        assert result.returncode == 0
        assert "AgentMail" in result.stdout
        assert "inboxes" in result.stdout
        assert "send" in result.stdout

    def test_no_args_shows_help(self):
        result = run_skill(env={"AGENTMAIL_API_KEY": ""})

        assert result.returncode == 0
        assert "Commands:" in result.stdout


class TestValidation:
    """Tests for input validation - no API key required."""

    def test_missing_api_key_shows_error(self):
        result = run_skill("inboxes", env={"AGENTMAIL_API_KEY": ""})

        assert result.returncode != 0
        assert "AGENTMAIL_API_KEY" in result.stderr

    def test_create_inbox_no_key(self):
        result = run_skill("create", env={"AGENTMAIL_API_KEY": ""})

        assert result.returncode != 0
        assert "AGENTMAIL_API_KEY" in result.stderr

    def test_send_requires_inbox_id(self):
        result = run_skill("send", env={"AGENTMAIL_API_KEY": "fake-key"})

        assert result.returncode != 0
        assert "inbox" in result.stderr.lower()

    def test_send_requires_to_address(self):
        result = run_skill("send", "inbox-123", env={"AGENTMAIL_API_KEY": "fake-key"})

        assert result.returncode != 0
        assert "to" in result.stderr.lower() or "recipient" in result.stderr.lower()

    def test_send_requires_subject(self):
        result = run_skill(
            "send",
            "inbox-123",
            "user@example.com",
            env={"AGENTMAIL_API_KEY": "fake-key"},
        )

        assert result.returncode != 0
        assert "subject" in result.stderr.lower()

    def test_send_requires_body(self):
        result = run_skill(
            "send",
            "inbox-123",
            "user@example.com",
            "Hello",
            env={"AGENTMAIL_API_KEY": "fake-key"},
        )

        assert result.returncode != 0
        assert "body" in result.stderr.lower()

    def test_messages_requires_inbox_id(self):
        result = run_skill("messages", env={"AGENTMAIL_API_KEY": "fake-key"})

        assert result.returncode != 0
        assert "inbox" in result.stderr.lower()

    def test_get_requires_inbox_and_message_id(self):
        result = run_skill("get", env={"AGENTMAIL_API_KEY": "fake-key"})

        assert result.returncode != 0

    def test_get_requires_message_id(self):
        result = run_skill("get", "inbox-123", env={"AGENTMAIL_API_KEY": "fake-key"})

        assert result.returncode != 0
        assert "message" in result.stderr.lower()

    def test_threads_requires_inbox_id(self):
        result = run_skill("threads", env={"AGENTMAIL_API_KEY": "fake-key"})

        assert result.returncode != 0
        assert "inbox" in result.stderr.lower()

    def test_thread_requires_inbox_and_thread_id(self):
        result = run_skill("thread", "inbox-123", env={"AGENTMAIL_API_KEY": "fake-key"})

        assert result.returncode != 0
        assert "thread" in result.stderr.lower()

    def test_delete_requires_inbox_id(self):
        result = run_skill("delete", env={"AGENTMAIL_API_KEY": "fake-key"})

        assert result.returncode != 0
        assert "inbox" in result.stderr.lower()

    def test_webhook_create_requires_url(self):
        result = run_skill("webhook-create", env={"AGENTMAIL_API_KEY": "fake-key"})

        assert result.returncode != 0
        assert "url" in result.stderr.lower()

    def test_webhook_create_requires_events(self):
        result = run_skill(
            "webhook-create",
            "https://example.com/hook",
            env={"AGENTMAIL_API_KEY": "fake-key"},
        )

        assert result.returncode != 0
        assert "event" in result.stderr.lower()

    def test_webhook_create_validates_event_types(self):
        result = run_skill(
            "webhook-create",
            "https://example.com/hook",
            "bogus.event",
            env={"AGENTMAIL_API_KEY": "fake-key"},
        )

        assert result.returncode != 0
        assert "unknown event type" in result.stderr.lower()

    def test_webhook_create_accepts_valid_events(self):
        """Valid event types pass validation (will fail at API without real key)."""
        result = run_skill(
            "webhook-create",
            "https://example.com/hook",
            "message.received",
            env={"AGENTMAIL_API_KEY": "fake-key"},
        )

        # Should get past validation and fail at API call, not at event validation
        assert "unknown event type" not in result.stderr.lower()

    def test_webhook_get_requires_id(self):
        result = run_skill("webhook-get", env={"AGENTMAIL_API_KEY": "fake-key"})

        assert result.returncode != 0
        assert "webhook id" in result.stderr.lower()

    def test_webhook_delete_requires_id(self):
        result = run_skill("webhook-delete", env={"AGENTMAIL_API_KEY": "fake-key"})

        assert result.returncode != 0
        assert "webhook id" in result.stderr.lower()

    def test_unknown_command_shows_error(self):
        result = run_skill("typo", env={"AGENTMAIL_API_KEY": "fake-key"})

        assert result.returncode != 0
        assert "unknown command" in result.stderr.lower()

    def test_messages_limit_must_be_positive(self):
        result = run_skill(
            "messages",
            "inbox-123",
            "--limit",
            "0",
            env={"AGENTMAIL_API_KEY": "fake-key"},
        )

        assert result.returncode != 0

    def test_messages_limit_must_be_numeric(self):
        result = run_skill(
            "messages",
            "inbox-123",
            "--limit",
            "abc",
            env={"AGENTMAIL_API_KEY": "fake-key"},
        )

        assert result.returncode != 0
        assert "number" in result.stderr.lower()


@requires_api_key
class TestReadIntegration:
    """Integration tests for read operations - work with inbox-scoped keys."""

    def test_list_inboxes(self):
        result = run_skill("inboxes")

        assert result.returncode == 0
        assert "ID:" in result.stdout or "No inboxes" in result.stdout

    def test_list_inboxes_with_limit(self):
        result = run_skill("inboxes", "--limit", "1")

        assert result.returncode == 0

    def test_inbox_details(self):
        """Get details for first available inbox."""
        list_result = run_skill("raw", "GET", "/inboxes")
        assert list_result.returncode == 0

        data = json.loads(list_result.stdout)
        inboxes = data.get("inboxes") or []
        if not inboxes:
            pytest.skip("No inboxes available")

        inbox_id = inboxes[0].get("inbox_id") or inboxes[0].get("id")
        result = run_skill("inbox", inbox_id)

        assert result.returncode == 0
        assert inbox_id in result.stdout

    def test_list_messages(self):
        """List messages for first available inbox."""
        list_result = run_skill("raw", "GET", "/inboxes")
        assert list_result.returncode == 0

        data = json.loads(list_result.stdout)
        inboxes = data.get("inboxes") or []
        if not inboxes:
            pytest.skip("No inboxes available")

        inbox_id = inboxes[0].get("inbox_id") or inboxes[0].get("id")
        result = run_skill("messages", inbox_id)

        assert result.returncode == 0

    def test_list_threads(self):
        """List threads for first available inbox."""
        list_result = run_skill("raw", "GET", "/inboxes")
        assert list_result.returncode == 0

        data = json.loads(list_result.stdout)
        inboxes = data.get("inboxes") or []
        if not inboxes:
            pytest.skip("No inboxes available")

        inbox_id = inboxes[0].get("inbox_id") or inboxes[0].get("id")
        result = run_skill("threads", inbox_id)

        assert result.returncode == 0

    def test_raw_api_call(self):
        result = run_skill("raw", "GET", "/inboxes")

        assert result.returncode == 0
        assert "inboxes" in result.stdout


# Write operations need an org-level key (am_..._org_...), not inbox-scoped
HAS_ORG_KEY = HAS_API_KEY and not os.getenv("AGENTMAIL_API_KEY", "").startswith(
    "am_us_inbox_"
)
requires_org_key = pytest.mark.skipif(
    not HAS_ORG_KEY,
    reason="AGENTMAIL_API_KEY is inbox-scoped or not set - skipping write tests",
)


@requires_org_key
class TestWriteIntegration:
    """Integration tests for write operations - require org-level API key."""

    def test_list_webhooks(self):
        result = run_skill("webhooks")

        assert result.returncode == 0

    def test_create_and_delete_inbox(self):
        """Create an inbox, verify it exists, then delete it."""
        # Use raw JSON to get a clean inbox_id without parsing markdown artifacts
        create_result = run_skill("raw", "POST", "/inboxes")
        assert create_result.returncode == 0

        data = json.loads(create_result.stdout)
        inbox_id = data.get("inbox_id") or data.get("id")
        assert inbox_id, f"No inbox_id in response: {create_result.stdout}"

        delete_result = run_skill("delete", inbox_id)
        assert delete_result.returncode == 0

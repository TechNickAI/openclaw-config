"""Tests for Quo (OpenPhone) skill.

Integration tests require QUO_API_KEY environment variable.
Tests auto-skip if the key is not available.
"""

import os
import subprocess
from pathlib import Path

import pytest

# Path to the skill script
SKILL_PATH = str(Path(__file__).parent / ".." / "skills" / "quo" / "quo")

# Skip integration tests if no API key
HAS_API_KEY = bool(os.getenv("QUO_API_KEY"))
requires_api_key = pytest.mark.skipif(
    not HAS_API_KEY,
    reason="QUO_API_KEY not set - skipping integration tests",
)


def run_skill(*args: str, env: dict | None = None) -> subprocess.CompletedProcess:
    """Run the quo skill with given arguments."""
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
        result = run_skill("help", env={"QUO_API_KEY": ""})

        assert result.returncode == 0
        assert "Quo" in result.stdout or "OpenPhone" in result.stdout
        assert "numbers" in result.stdout
        assert "conversations" in result.stdout

    def test_no_args_shows_help(self):
        """Running with no arguments shows help."""
        result = run_skill(env={"QUO_API_KEY": ""})

        assert result.returncode == 0
        assert "Commands:" in result.stdout


class TestValidation:
    """Tests for input validation - no API key required."""

    def test_missing_api_key_shows_error(self):
        """Missing API key shows helpful error."""
        result = run_skill("numbers", env={"QUO_API_KEY": ""})

        assert result.returncode != 0
        assert "QUO_API_KEY" in result.stderr

    def test_summary_requires_call_id(self):
        """Summary without callId shows error."""
        result = run_skill("summary", env={"QUO_API_KEY": "fake-key"})

        assert result.returncode != 0
        assert "callid" in result.stderr.lower() or "call" in result.stderr.lower()

    def test_transcript_requires_call_id(self):
        """Transcript without callId shows error."""
        result = run_skill("transcript", env={"QUO_API_KEY": "fake-key"})

        assert result.returncode != 0
        assert "callid" in result.stderr.lower() or "call" in result.stderr.lower()

    def test_recordings_requires_call_id(self):
        """Recordings without callId shows error."""
        result = run_skill("recordings", env={"QUO_API_KEY": "fake-key"})

        assert result.returncode != 0
        assert "callid" in result.stderr.lower() or "call" in result.stderr.lower()

    def test_voicemails_requires_call_id(self):
        """Voicemails without callId shows error."""
        result = run_skill("voicemails", env={"QUO_API_KEY": "fake-key"})

        assert result.returncode != 0
        assert "callid" in result.stderr.lower() or "call" in result.stderr.lower()

    def test_send_requires_from_and_to(self):
        """Send without --from and --to shows error."""
        result = run_skill("send", "Hello", env={"QUO_API_KEY": "fake-key"})

        assert result.returncode != 0
        # Should mention missing required args
        assert "from" in result.stderr.lower() or "to" in result.stderr.lower()

    def test_send_requires_message(self):
        """Send without message content shows error."""
        result = run_skill(
            "send",
            "--from",
            "+15551234567",
            "--to",
            "+15559876543",
            env={"QUO_API_KEY": "fake-key"},
        )

        assert result.returncode != 0
        assert "message" in result.stderr.lower() or "content" in result.stderr.lower()

    def test_send_validates_phone_format(self):
        """Send validates E.164 phone number format."""
        result = run_skill(
            "send",
            "--from",
            "5551234567",
            "--to",
            "+15559876543",
            "Hello",
            env={"QUO_API_KEY": "fake-key"},
        )

        assert result.returncode != 0
        assert "e.164" in result.stderr.lower() or "format" in result.stderr.lower()

    def test_messages_requires_phone_number_id(self):
        """Messages command requires phoneNumberId."""
        result = run_skill("messages", env={"QUO_API_KEY": "fake-key"})

        assert result.returncode != 0
        assert (
            "phonenumberid" in result.stderr.lower()
            or "number" in result.stderr.lower()
        )

    def test_messages_requires_participant(self):
        """Messages command requires participant phone number."""
        result = run_skill(
            "messages", "--number-id", "PN123", env={"QUO_API_KEY": "fake-key"}
        )

        assert result.returncode != 0
        assert "participant" in result.stderr.lower()

    def test_calls_requires_phone_number_id(self):
        """Calls command requires phoneNumberId."""
        result = run_skill("calls", env={"QUO_API_KEY": "fake-key"})

        assert result.returncode != 0
        assert (
            "phonenumberid" in result.stderr.lower()
            or "number" in result.stderr.lower()
        )

    def test_calls_requires_participant(self):
        """Calls command requires participant phone number."""
        result = run_skill(
            "calls", "--number-id", "PN123", env={"QUO_API_KEY": "fake-key"}
        )

        assert result.returncode != 0
        assert "participant" in result.stderr.lower()

    def test_unknown_command_shows_error(self):
        """Unknown command shows error, not help."""
        result = run_skill("typo", env={"QUO_API_KEY": "fake-key"})

        assert result.returncode != 0
        assert "unknown command" in result.stderr.lower()

    def test_raw_requires_endpoint(self):
        """Raw command requires endpoint."""
        result = run_skill("raw", env={"QUO_API_KEY": "fake-key"})

        assert result.returncode != 0
        assert "endpoint" in result.stderr.lower()

    def test_limit_must_be_positive(self):
        """--limit rejects zero and negative values."""
        result = run_skill(
            "conversations", "--limit", "0", env={"QUO_API_KEY": "fake-key"}
        )
        assert result.returncode != 0
        assert "positive" in result.stderr.lower() or "limit" in result.stderr.lower()

        result = run_skill(
            "conversations", "--limit", "-5", env={"QUO_API_KEY": "fake-key"}
        )
        assert result.returncode != 0

    def test_limit_must_be_numeric(self):
        """--limit flag requires a number."""
        result = run_skill(
            "conversations", "--limit", "abc", env={"QUO_API_KEY": "fake-key"}
        )

        assert result.returncode != 0
        assert "limit" in result.stderr.lower() or "number" in result.stderr.lower()


class TestCommandAliases:
    """Tests for command aliases - no API key required for help output."""

    def test_nums_is_alias_for_numbers(self):
        """'nums' is an alias for 'numbers'."""
        result = run_skill("help", env={"QUO_API_KEY": ""})
        # Help should mention the alias
        assert "nums" in result.stdout.lower() or "numbers" in result.stdout

    def test_convos_is_alias_for_conversations(self):
        """'convos' is an alias for 'conversations'."""
        result = run_skill("help", env={"QUO_API_KEY": ""})
        assert "convos" in result.stdout.lower() or "conversations" in result.stdout

    def test_recs_is_alias_for_recordings(self):
        """'recs' is an alias for 'recordings'."""
        result = run_skill("help", env={"QUO_API_KEY": ""})
        assert "recs" in result.stdout.lower() or "recordings" in result.stdout

    def test_vm_is_alias_for_voicemails(self):
        """'vm' is an alias for 'voicemails'."""
        result = run_skill("help", env={"QUO_API_KEY": ""})
        assert "vm" in result.stdout.lower() or "voicemails" in result.stdout


@requires_api_key
class TestNumbersIntegration:
    """Integration tests for numbers command - require API key."""

    def test_numbers_returns_results(self):
        """Numbers command returns formatted results."""
        result = run_skill("numbers")

        assert result.returncode == 0
        # Should have markdown formatted output or empty data message
        assert (
            "##" in result.stdout
            or "Number" in result.stdout
            or "No phone numbers" in result.stdout
        )

    def test_nums_alias_works(self):
        """Nums alias works same as numbers."""
        result = run_skill("nums")

        assert result.returncode == 0


@requires_api_key
class TestConversationsIntegration:
    """Integration tests for conversations command - require API key."""

    def test_conversations_returns_results(self):
        """Conversations command returns formatted results."""
        result = run_skill("conversations")

        assert result.returncode == 0
        # Should have some output
        assert result.stdout.strip()

    def test_conversations_with_limit(self):
        """Conversations respects --limit flag."""
        result = run_skill("conversations", "--limit", "5")

        assert result.returncode == 0

    def test_convos_alias_works(self):
        """Convos alias works same as conversations."""
        result = run_skill("convos", "--limit", "5")

        assert result.returncode == 0


@requires_api_key
class TestContactsIntegration:
    """Integration tests for contacts command - require API key."""

    def test_contacts_returns_results(self):
        """Contacts command returns formatted results."""
        result = run_skill("contacts")

        assert result.returncode == 0
        assert result.stdout.strip()

    def test_contacts_with_limit(self):
        """Contacts respects --limit flag."""
        result = run_skill("contacts", "--limit", "10")

        assert result.returncode == 0


@requires_api_key
class TestUsersIntegration:
    """Integration tests for users command - require API key."""

    def test_users_returns_results(self):
        """Users command returns formatted results."""
        result = run_skill("users")

        assert result.returncode == 0
        # Should have markdown formatted output
        assert result.stdout.strip()


@requires_api_key
class TestRawIntegration:
    """Integration tests for raw API calls - require API key."""

    def test_raw_get_phone_numbers(self):
        """Raw GET request to phone-numbers endpoint."""
        result = run_skill("raw", "GET", "/phone-numbers")

        assert result.returncode == 0
        # Should return JSON
        assert "{" in result.stdout

    def test_raw_defaults_to_get(self):
        """Raw command defaults to GET method."""
        result = run_skill("raw", "/phone-numbers")

        assert result.returncode == 0
        assert "{" in result.stdout

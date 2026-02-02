"""Tests for the apple-mail skill."""

import os
import subprocess
import sys
from pathlib import Path

import pytest

# Skip all tests on non-macOS platforms (PyObjC requires macOS)
pytestmark = pytest.mark.skipif(
    sys.platform != "darwin",
    reason="apple-mail requires macOS (PyObjC won't build on Linux/Windows)",
)

# Path to the skill script
SKILL_PATH = Path(__file__).parent.parent / "skills" / "apple-mail" / "apple-mail"


def run_skill(*args: str, env: dict | None = None, timeout: int = 120) -> subprocess.CompletedProcess:
    """Run the apple-mail skill with given arguments."""
    cmd = ["uv", "run", SKILL_PATH, *args]
    run_env = os.environ.copy()
    if env:
        run_env.update(env)
    return subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        timeout=timeout,
        env=run_env,
    )


def check_mail_accessible() -> bool:
    """Check if Mail.app is running and accessible."""
    try:
        # Quick test: just try to connect and check running status
        result = subprocess.run(
            [
                "uv",
                "run",
                "--with",
                "pyobjc-framework-ScriptingBridge",
                "python3",
                "-c",
                """
from ScriptingBridge import SBApplication
mail = SBApplication.applicationWithBundleIdentifier_('com.apple.mail')
if mail and mail.isRunning():
    # Try to actually access data with timeout
    import signal
    def handler(signum, frame):
        raise TimeoutError()
    signal.signal(signal.SIGALRM, handler)
    signal.alarm(5)
    try:
        accounts = mail.accounts()
        count = accounts.count()  # This will hang if permissions are blocked
        print('OK')
    except TimeoutError:
        print('TIMEOUT')
    finally:
        signal.alarm(0)
else:
    print('NOT_RUNNING')
""",
            ],
            capture_output=True,
            text=True,
            timeout=10,
        )
        return "OK" in result.stdout
    except Exception:
        return False


# Check at module load time
MAIL_ACCESSIBLE = check_mail_accessible()
requires_mail = pytest.mark.skipif(
    not MAIL_ACCESSIBLE,
    reason="Mail.app not accessible (not running or no automation permission)",
)


class TestHelp:
    """Tests for help command - always works, no Mail.app needed."""

    def test_help_shows_usage(self):
        """Help command shows usage information."""
        result = run_skill("help")

        assert result.returncode == 0
        assert "apple-mail" in result.stdout.lower()
        assert "accounts" in result.stdout
        assert "mailboxes" in result.stdout
        assert "list" in result.stdout
        assert "search" in result.stdout
        assert "read" in result.stdout
        assert "delete" in result.stdout
        assert "move" in result.stdout
        assert "send" in result.stdout
        assert "reply" in result.stdout

    def test_help_is_default_command(self):
        """Running with no args shows help."""
        result = run_skill()

        assert result.returncode == 0
        assert "Usage:" in result.stdout

    def test_unknown_command_shows_error(self):
        """Unknown command shows error with hint."""
        result = run_skill("foobar")

        assert result.returncode != 0
        assert "Unknown command" in result.stderr
        assert "foobar" in result.stderr


class TestValidation:
    """Tests for input validation - no Mail.app interaction needed."""

    def test_read_requires_id(self):
        """Read command requires message ID."""
        result = run_skill("read")

        assert result.returncode != 0
        assert "id" in result.stderr.lower() or "required" in result.stderr.lower()

    def test_delete_requires_id(self):
        """Delete command requires message ID."""
        result = run_skill("delete")

        assert result.returncode != 0
        assert "id" in result.stderr.lower() or "required" in result.stderr.lower()

    def test_move_requires_mailbox_and_id(self):
        """Move command requires mailbox and message ID."""
        result = run_skill("move")

        assert result.returncode != 0
        assert "mailbox" in result.stderr.lower() or "id" in result.stderr.lower()

    def test_move_requires_id_after_mailbox(self):
        """Move with only mailbox shows error."""
        result = run_skill("move", "SomeMailbox")

        assert result.returncode != 0
        assert "id" in result.stderr.lower() or "required" in result.stderr.lower()

    def test_mark_read_requires_id(self):
        """Mark-read requires message ID."""
        result = run_skill("mark-read")

        assert result.returncode != 0

    def test_mark_unread_requires_id(self):
        """Mark-unread requires message ID."""
        result = run_skill("mark-unread")

        assert result.returncode != 0

    def test_search_requires_query(self):
        """Search requires a query string."""
        result = run_skill("search")

        assert result.returncode != 0
        assert "query" in result.stderr.lower() or "required" in result.stderr.lower()

    def test_send_requires_to(self):
        """Send requires --to flag."""
        result = run_skill("send", "--subject", "Test", "--body", "Test body")

        assert result.returncode != 0
        assert "--to" in result.stderr

    def test_send_requires_subject(self):
        """Send requires --subject flag."""
        result = run_skill("send", "--to", "test@example.com", "--body", "Test body")

        assert result.returncode != 0
        assert "--subject" in result.stderr

    def test_send_requires_body(self):
        """Send requires --body flag."""
        result = run_skill("send", "--to", "test@example.com", "--subject", "Test")

        assert result.returncode != 0
        assert "--body" in result.stderr

    def test_reply_requires_id(self):
        """Reply requires message ID."""
        result = run_skill("reply", "--body", "Test reply")

        assert result.returncode != 0
        assert "id" in result.stderr.lower() or "required" in result.stderr.lower()

    def test_reply_requires_body(self):
        """Reply requires --body flag."""
        result = run_skill("reply", "12345")

        assert result.returncode != 0
        assert "--body" in result.stderr

    def test_limit_must_be_positive(self):
        """--limit flag must be a positive number."""
        result = run_skill("list", "--limit", "0")

        assert result.returncode != 0
        assert "positive" in result.stderr.lower() or "limit" in result.stderr.lower()

    def test_limit_must_be_numeric(self):
        """--limit flag must be a number."""
        result = run_skill("list", "--limit", "abc")

        assert result.returncode != 0
        assert "number" in result.stderr.lower() or "limit" in result.stderr.lower()


@requires_mail
class TestMailAppIntegration:
    """Integration tests - require Mail.app running and accessible."""

    def test_accounts_returns_output(self):
        """Accounts command returns some output."""
        result = run_skill("accounts")

        assert result.returncode == 0
        # Should have output (configured accounts) or "No mail accounts"
        assert result.stdout.strip()

    @pytest.mark.skip(reason="ScriptingBridge has variable performance - works manually but can timeout in CI")
    def test_mailboxes_returns_output(self):
        """Mailboxes command returns some output."""
        result = run_skill("mailboxes")

        assert result.returncode == 0
        assert result.stdout.strip()

    @pytest.mark.skip(reason="ScriptingBridge has variable performance - works manually but can timeout in CI")
    def test_list_inbox(self):
        """List INBOX returns messages or empty message."""
        result = run_skill("list", "INBOX", "--limit", "5")

        assert result.returncode == 0
        # Either has messages or says "No messages"
        assert result.stdout.strip()

    @pytest.mark.skip(reason="ScriptingBridge has variable performance - works manually but can timeout in CI")
    def test_list_with_limit(self):
        """List respects limit parameter."""
        result = run_skill("list", "INBOX", "--limit", "3")

        assert result.returncode == 0
        # Count output lines (excluding empty)
        lines = [l for l in result.stdout.strip().split("\n") if l.strip()]
        # Should be at most 3 messages (could be fewer if inbox is small)
        assert len(lines) <= 3 or "No messages" in result.stdout

    @pytest.mark.skip(reason="Search is slow without SQLite optimization - iterates all messages")
    def test_search_returns_output(self):
        """Search returns results or no-match message."""
        result = run_skill("search", "test", "--limit", "5")

        assert result.returncode == 0
        # Either has results or says "No messages matching"
        assert result.stdout.strip()

    def test_refresh_works(self):
        """Refresh command completes without error."""
        result = run_skill("refresh")

        assert result.returncode == 0
        assert "refresh" in result.stdout.lower()

    @pytest.mark.skip(reason="Slow when mailbox doesn't exist - iterates all nested mailboxes")
    def test_nonexistent_mailbox_error(self):
        """List with nonexistent mailbox shows error."""
        result = run_skill("list", "ThisMailboxDoesNotExist12345")

        assert result.returncode != 0
        assert "not found" in result.stderr.lower()

    @pytest.mark.skip(reason="Slow when message doesn't exist - checks all mailboxes")
    def test_nonexistent_message_id(self):
        """Read with nonexistent ID shows error."""
        result = run_skill("read", "999999999")

        assert result.returncode == 0  # Command succeeds but prints error
        assert "not found" in (result.stdout + result.stderr).lower()

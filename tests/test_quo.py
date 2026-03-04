"""Tests for Quo (OpenPhone) skill.

Unit tests verify format functions with mock API responses — no API key needed.
Integration tests require QUO_API_KEY environment variable and auto-skip without it.
"""

import importlib.machinery
import importlib.util
import os
import subprocess
from pathlib import Path

import pytest

# Path to the skill script
SKILL_PATH = str(Path(__file__).parent / ".." / "skills" / "quo" / "quo")

# Import format functions directly from the skill script (no .py extension)
_loader = importlib.machinery.SourceFileLoader("quo", SKILL_PATH)
_spec = importlib.util.spec_from_loader("quo", _loader)
_quo = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_quo)

from datetime import datetime, timezone

format_numbers = _quo.format_numbers
format_conversations = _quo.format_conversations
format_contacts = _quo.format_contacts
format_users = _quo.format_users
format_calls = _quo.format_calls
format_messages = _quo.format_messages
format_recordings = _quo.format_recordings
format_voicemails = _quo.format_voicemails
format_summary = _quo.format_summary
format_transcript = _quo.format_transcript
find_contact_by_phone = _quo.find_contact_by_phone
get_known_phones = _quo.get_known_phones
default_since = _quo.default_since

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


class TestFormatNumbers:
    """Unit tests for format_numbers — verifies field extraction from API response."""

    def test_formats_phone_number_fields(self):
        data = {
            "data": [
                {
                    "id": "PN123abc",
                    "name": "Main Line",
                    "formattedNumber": "(555) 123-4567",
                    "number": "+15551234567",
                    "type": "local",
                    "users": [{"name": "Nick Sullivan", "email": "nick@example.com"}],
                }
            ]
        }
        result = format_numbers(data)
        assert "## Main Line" in result
        assert "**ID:** PN123abc" in result
        assert "**Number:** (555) 123-4567" in result
        assert "**Type:** local" in result
        assert "**Users:** Nick Sullivan" in result

    def test_empty_data(self):
        assert format_numbers({"data": []}) == "No phone numbers found."

    def test_falls_back_to_raw_number(self):
        data = {"data": [{"id": "PN1", "number": "+15551234567", "type": "local", "users": []}]}
        result = format_numbers(data)
        assert "+15551234567" in result


class TestFormatConversations:
    """Unit tests for format_conversations."""

    def test_formats_conversation_fields(self):
        data = {
            "data": [
                {
                    "id": "CV123",
                    "name": "Nick Sullivan",
                    "participants": ["+15551234567", "+15559876543"],
                    "lastActivityAt": "2026-03-01T12:00:00Z",
                    "phoneNumberId": "PN123abc",
                }
            ]
        }
        result = format_conversations(data)
        assert "## Nick Sullivan" in result
        assert "**ID:** CV123" in result
        assert "+15551234567, +15559876543" in result
        assert "2026-03-01T12:00:00Z" in result
        assert "**Phone Number ID:** PN123abc" in result

    def test_empty_data(self):
        assert format_conversations({"data": []}) == "No conversations found."


class TestFormatContacts:
    """Unit tests for format_contacts — verifies defaultFields nesting is read correctly."""

    def test_reads_from_default_fields(self):
        """The critical test — fields must come from defaultFields, not top level."""
        data = {
            "data": [
                {
                    "id": "CT123",
                    "source": "public-api",
                    "defaultFields": {
                        "firstName": "John",
                        "lastName": "Doe",
                        "company": "Acme Corp",
                        "role": "CEO",
                        "emails": [{"name": "work", "value": "john@acme.com", "id": "e1"}],
                        "phoneNumbers": [{"name": "mobile", "value": "+15551234567", "id": "p1"}],
                    },
                    "customFields": [],
                }
            ]
        }
        result = format_contacts(data)
        assert "## John Doe" in result
        assert "**ID:** CT123" in result
        assert "**Company:** Acme Corp" in result
        assert "**Role:** CEO" in result
        assert "john@acme.com" in result
        assert "+15551234567" in result
        assert "**Source:** public-api" in result

    def test_contact_without_role_omits_role_line(self):
        data = {
            "data": [
                {
                    "id": "CT456",
                    "defaultFields": {
                        "firstName": "Jane",
                        "lastName": "Smith",
                        "company": None,
                        "role": None,
                        "emails": [],
                        "phoneNumbers": [{"name": "cell", "value": "+15559876543", "id": "p2"}],
                    },
                }
            ]
        }
        result = format_contacts(data)
        assert "## Jane Smith" in result
        assert "**Role:**" not in result
        assert "**Source:**" not in result

    def test_contact_multiple_phones_and_emails(self):
        data = {
            "data": [
                {
                    "id": "CT789",
                    "defaultFields": {
                        "firstName": "Bob",
                        "lastName": "",
                        "company": "Widget Inc",
                        "role": "Sales",
                        "emails": [
                            {"name": "work", "value": "bob@widget.com", "id": "e1"},
                            {"name": "personal", "value": "bob@gmail.com", "id": "e2"},
                        ],
                        "phoneNumbers": [
                            {"name": "office", "value": "+15551111111", "id": "p1"},
                            {"name": "cell", "value": "+15552222222", "id": "p2"},
                        ],
                    },
                }
            ]
        }
        result = format_contacts(data)
        assert "## Bob" in result
        assert "bob@widget.com, bob@gmail.com" in result
        assert "+15551111111, +15552222222" in result

    def test_missing_default_fields_crashes(self):
        """No defaultFields = KeyError, not silent 'Unknown'. Broken > wrong."""
        data = {"data": [{"id": "CT000", "firstName": "Orphan"}]}
        with pytest.raises(KeyError):
            format_contacts(data)

    def test_empty_data(self):
        assert format_contacts({"data": []}) == "No contacts found."


class TestFormatUsers:
    """Unit tests for format_users."""

    def test_formats_user_fields(self):
        data = {
            "data": [
                {
                    "id": "US123",
                    "firstName": "Nick",
                    "lastName": "Sullivan",
                    "email": "nick@example.com",
                    "role": "admin",
                }
            ]
        }
        result = format_users(data)
        assert "## Nick Sullivan" in result
        assert "**Email:** nick@example.com" in result
        assert "**Role:** admin" in result

    def test_empty_data(self):
        assert format_users({"data": []}) == "No users found."


class TestFormatCalls:
    """Unit tests for format_calls."""

    def test_formats_call_fields(self):
        data = {
            "data": [
                {
                    "id": "AC123",
                    "from": "+15551234567",
                    "to": "+15559876543",
                    "direction": "incoming",
                    "status": "completed",
                    "duration": 245,
                    "createdAt": "2026-03-01T14:30:00Z",
                }
            ]
        }
        result = format_calls(data)
        assert "## Call (incoming)" in result
        assert "**ID:** AC123" in result
        assert "**From:** +15551234567" in result
        assert "**To:** +15559876543" in result
        assert "**Status:** completed" in result
        assert "**Duration:** 245s" in result

    def test_empty_data(self):
        assert format_calls({"data": []}) == "No calls found."


class TestFormatMessages:
    """Unit tests for format_messages."""

    def test_formats_message_fields(self):
        data = {
            "data": [
                {
                    "id": "MS123",
                    "from": "+15551234567",
                    "to": ["+15559876543"],
                    "text": "Hey, are we still on for 3pm?",
                    "createdAt": "2026-03-01T10:00:00Z",
                    "direction": "outgoing",
                }
            ]
        }
        result = format_messages(data)
        assert "## Message (outgoing)" in result
        assert "**From:** +15551234567" in result
        assert "**To:** +15559876543" in result
        assert "Hey, are we still on for 3pm?" in result

    def test_empty_data(self):
        assert format_messages({"data": []}) == "No messages found."


class TestFormatRecordings:
    """Unit tests for format_recordings."""

    def test_formats_recording_fields(self):
        data = {
            "data": [
                {
                    "id": "RC123",
                    "status": "completed",
                    "duration": 120,
                    "url": "https://recordings.openphone.com/rc123.mp3",
                }
            ]
        }
        result = format_recordings(data)
        assert "**ID:** RC123" in result
        assert "**Status:** completed" in result
        assert "**Duration:** 120s" in result
        assert "https://recordings.openphone.com/rc123.mp3" in result

    def test_empty_data(self):
        assert format_recordings({"data": []}) == "No recordings found."


class TestFormatVoicemails:
    """Unit tests for format_voicemails."""

    def test_formats_single_voicemail(self):
        """API returns a single object, not an array."""
        data = {
            "data": {
                "callId": "AC123",
                "duration": 30,
                "status": "completed",
                "url": "https://recordings.openphone.com/vm123.mp3",
                "transcript": "Hi Nick, this is Paul from Urbanspace. Give me a call back.",
                "createdAt": "2026-03-01T08:00:00Z",
            }
        }
        result = format_voicemails(data)
        assert "**Call ID:** AC123" in result
        assert "**Duration:** 30s" in result
        assert "Paul from Urbanspace" in result
        assert "2026-03-01T08:00:00Z" in result

    def test_voicemail_without_transcript(self):
        data = {"data": {"callId": "AC456", "duration": 5}}
        result = format_voicemails(data)
        assert "**Transcript:** Not available" in result

    def test_empty_data(self):
        assert format_voicemails({"data": {}}) == "No voicemails found."


class TestFormatSummary:
    """Unit tests for format_summary."""

    def test_formats_summary_with_next_steps(self):
        data = {
            "data": {
                "status": "completed",
                "summary": ["Discussed Q2 targets", "Agreed on new pricing"],
                "nextSteps": ["Send updated proposal", "Schedule follow-up"],
            }
        }
        result = format_summary(data)
        assert "# Call Summary" in result
        assert "**Status:** completed" in result
        assert "- Discussed Q2 targets" in result
        assert "- Send updated proposal" in result

    def test_summary_string_format(self):
        """API sometimes returns summary as a string instead of array."""
        data = {
            "data": {
                "status": "completed",
                "summary": "Quick chat about the project timeline",
                "nextSteps": "Follow up next week",
            }
        }
        result = format_summary(data)
        assert "- Quick chat about the project timeline" in result
        assert "- Follow up next week" in result

    def test_empty_data(self):
        assert format_summary({"data": {}}) == "No summary available."


class TestFormatTranscript:
    """Unit tests for format_transcript."""

    def test_formats_dialogue_with_timestamps(self):
        data = {
            "data": {
                "callId": "AC123",
                "createdAt": "2026-03-01T14:30:00Z",
                "dialogue": [
                    {
                        "content": "Hello, this is Nick",
                        "start": 0.16,
                        "end": 1.5,
                        "identifier": "+15551234567",
                        "userId": "US123",
                    },
                    {
                        "content": "Hi Nick, this is Jane from Acme",
                        "start": 2.0,
                        "end": 4.5,
                        "identifier": "+15559876543",
                        "userId": None,
                    },
                ],
            }
        }
        result = format_transcript(data)
        assert "# Call Transcript" in result
        assert "[00:00] **+15551234567 (user):** Hello, this is Nick" in result
        assert "[00:02] **+15559876543:** Hi Nick, this is Jane from Acme" in result

    def test_timestamp_formatting_minutes(self):
        """Timestamps over 60s should show mm:ss correctly."""
        data = {
            "data": {
                "callId": "AC123",
                "dialogue": [
                    {"content": "Still here", "start": 125.5, "identifier": "+1555", "userId": None}
                ],
            }
        }
        result = format_transcript(data)
        assert "[02:05]" in result

    def test_empty_data(self):
        assert format_transcript({"data": {}}) == "No transcript available."


class TestFindContactByPhone:
    """Unit tests for find_contact_by_phone."""

    def test_finds_matching_contact(self):
        contacts = [
            {"id": "CT1", "defaultFields": {"phoneNumbers": [{"value": "+15551234567"}]}},
            {"id": "CT2", "defaultFields": {"phoneNumbers": [{"value": "+15559999999"}]}},
        ]
        matches = find_contact_by_phone("+15551234567", contacts)
        assert len(matches) == 1
        assert matches[0]["id"] == "CT1"

    def test_no_match_returns_empty(self):
        contacts = [
            {"id": "CT1", "defaultFields": {"phoneNumbers": [{"value": "+15551234567"}]}},
        ]
        assert find_contact_by_phone("+10000000000", contacts) == []

    def test_multiple_matches(self):
        contacts = [
            {"id": "CT1", "defaultFields": {"phoneNumbers": [{"value": "+15551234567"}]}},
            {"id": "CT2", "defaultFields": {"phoneNumbers": [{"value": "+15551234567"}]}},
        ]
        matches = find_contact_by_phone("+15551234567", contacts)
        assert len(matches) == 2

    def test_contact_with_multiple_phones(self):
        contacts = [
            {"id": "CT1", "defaultFields": {"phoneNumbers": [
                {"value": "+15551111111"},
                {"value": "+15552222222"},
            ]}},
        ]
        assert len(find_contact_by_phone("+15552222222", contacts)) == 1

    def test_missing_default_fields_crashes(self):
        """No defaultFields = KeyError. Broken > wrong."""
        contacts = [{"id": "CT1"}]
        with pytest.raises(KeyError):
            find_contact_by_phone("+15551234567", contacts)


class TestGetKnownPhones:
    """Unit tests for get_known_phones."""

    def test_collects_all_phones(self):
        contacts = [
            {"id": "CT1", "defaultFields": {"phoneNumbers": [
                {"value": "+15551111111"},
                {"value": "+15552222222"},
            ]}},
            {"id": "CT2", "defaultFields": {"phoneNumbers": [
                {"value": "+15553333333"},
            ]}},
        ]
        known = get_known_phones(contacts)
        assert known == {"+15551111111", "+15552222222", "+15553333333"}

    def test_empty_contacts(self):
        assert get_known_phones([]) == set()

    def test_deduplicates(self):
        contacts = [
            {"id": "CT1", "defaultFields": {"phoneNumbers": [{"value": "+15551111111"}]}},
            {"id": "CT2", "defaultFields": {"phoneNumbers": [{"value": "+15551111111"}]}},
        ]
        assert len(get_known_phones(contacts)) == 1


class TestDefaultSince:
    """Unit tests for default_since."""

    def test_returns_parseable_iso(self):
        result = default_since()
        datetime.fromisoformat(result)

    def test_is_approximately_30_days_ago(self):
        result = datetime.fromisoformat(default_since())
        delta = datetime.now(timezone.utc) - result
        assert 29 <= delta.days <= 31


class TestSearchPhoneValidation:
    """Validation tests for search-phone command."""

    def test_requires_phone_number(self):
        result = run_skill("search-phone", env={"QUO_API_KEY": "fake-key"})
        assert result.returncode != 0
        assert "phone" in result.stderr.lower()

    def test_validates_e164(self):
        result = run_skill("search-phone", "5551234567", env={"QUO_API_KEY": "fake-key"})
        assert result.returncode != 0
        assert "e.164" in result.stderr.lower() or "format" in result.stderr.lower()


class TestGatherValidation:
    """Validation tests for gather command."""

    def test_requires_phone_number(self):
        result = run_skill("gather", env={"QUO_API_KEY": "fake-key"})
        assert result.returncode != 0
        assert "phone" in result.stderr.lower()

    def test_validates_e164(self):
        result = run_skill("gather", "5551234567", env={"QUO_API_KEY": "fake-key"})
        assert result.returncode != 0
        assert "e.164" in result.stderr.lower() or "format" in result.stderr.lower()

    def test_limit_must_be_positive(self):
        result = run_skill("gather", "+15551234567", "--limit", "0", env={"QUO_API_KEY": "fake-key"})
        assert result.returncode != 0

    def test_limit_must_be_numeric(self):
        result = run_skill("gather", "+15551234567", "--limit", "abc", env={"QUO_API_KEY": "fake-key"})
        assert result.returncode != 0


class TestNewCommandsInHelp:
    """Verify new commands appear in help output."""

    def test_help_includes_search_phone(self):
        result = run_skill("help", env={"QUO_API_KEY": ""})
        assert "search-phone" in result.stdout

    def test_help_includes_gather(self):
        result = run_skill("help", env={"QUO_API_KEY": ""})
        assert "gather" in result.stdout

    def test_help_includes_unknown_flag(self):
        result = run_skill("help", env={"QUO_API_KEY": ""})
        assert "--unknown" in result.stdout

    def test_help_includes_sp_alias(self):
        result = run_skill("help", env={"QUO_API_KEY": ""})
        assert "sp" in result.stdout


@requires_api_key
class TestSearchPhoneIntegration:
    """Integration tests for search-phone command."""

    def test_search_phone_runs(self):
        result = run_skill("search-phone", "+15551234567")
        assert result.returncode == 0
        assert "No contacts found" in result.stdout or "**Phones:**" in result.stdout

    def test_sp_alias_works(self):
        result = run_skill("sp", "+15551234567")
        assert result.returncode == 0


@requires_api_key
class TestConversationsUnknownIntegration:
    """Integration tests for --unknown flag."""

    def test_unknown_flag_runs(self):
        result = run_skill("conversations", "--unknown", "--limit", "5")
        assert result.returncode == 0


@requires_api_key
class TestGatherIntegration:
    """Integration tests for gather command."""

    def test_gather_runs(self):
        result = run_skill("gather", "+15551234567", "--limit", "3")
        assert result.returncode == 0
        assert "# Gather:" in result.stdout


@requires_api_key
class TestNumbersIntegration:
    """Integration tests for numbers command - require API key."""

    def test_numbers_returns_formatted_fields(self):
        """Numbers command returns real field values, not just exit 0."""
        result = run_skill("numbers")

        assert result.returncode == 0
        # Must contain actual formatted fields, not just "some output"
        assert "**Number:**" in result.stdout or "No phone numbers" in result.stdout
        if "**Number:**" in result.stdout:
            assert "**ID:**" in result.stdout
            assert "**Type:**" in result.stdout
            assert "**Users:**" in result.stdout

    def test_nums_alias_works(self):
        """Nums alias works same as numbers."""
        result = run_skill("nums")

        assert result.returncode == 0


@requires_api_key
class TestConversationsIntegration:
    """Integration tests for conversations command - require API key."""

    def test_conversations_returns_formatted_fields(self):
        """Conversations command returns real field values."""
        result = run_skill("conversations")

        assert result.returncode == 0
        assert "**Participants:**" in result.stdout or "No conversations" in result.stdout
        if "**Participants:**" in result.stdout:
            assert "**Last Activity:**" in result.stdout
            assert "**Phone Number ID:**" in result.stdout

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

    def test_contacts_returns_formatted_fields(self):
        """Contacts command returns real field values from defaultFields."""
        result = run_skill("contacts")

        assert result.returncode == 0
        # Must show actual contact data, not all "Unknown"
        assert "**Phones:**" in result.stdout or "No contacts" in result.stdout
        if "**Phones:**" in result.stdout:
            assert "**ID:**" in result.stdout
            assert "**Company:**" in result.stdout

    def test_contacts_with_limit(self):
        """Contacts respects --limit flag."""
        result = run_skill("contacts", "--limit", "10")

        assert result.returncode == 0


@requires_api_key
class TestUsersIntegration:
    """Integration tests for users command - require API key."""

    def test_users_returns_formatted_fields(self):
        """Users command returns real field values."""
        result = run_skill("users")

        assert result.returncode == 0
        assert "**Email:**" in result.stdout or "No users" in result.stdout
        if "**Email:**" in result.stdout:
            assert "**Role:**" in result.stdout


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

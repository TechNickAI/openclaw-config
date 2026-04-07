"""Tests for daily-report workflow AGENT.md structure.

Validates that the workflow file has correct frontmatter and required sections.
No API key or external service required.
"""

from pathlib import Path

import pytest
import yaml

WORKFLOW_PATH = Path(__file__).parent.parent / "workflows" / "daily-report" / "AGENT.md"


def parse_frontmatter(content: str) -> tuple[dict, str]:
    """Extract YAML frontmatter and body from a markdown file."""
    if not content.startswith("---"):
        return {}, content
    end = content.index("---", 3)
    frontmatter_text = content[3:end].strip()
    body = content[end + 3 :].strip()
    return yaml.safe_load(frontmatter_text), body


class TestAgentMdExists:
    def test_file_exists(self):
        """AGENT.md exists at the expected path."""
        assert WORKFLOW_PATH.exists(), f"Missing: {WORKFLOW_PATH}"

    def test_file_is_not_empty(self):
        """AGENT.md has content."""
        assert WORKFLOW_PATH.stat().st_size > 0


class TestFrontmatter:
    @pytest.fixture(scope="class")
    def frontmatter(self):
        content = WORKFLOW_PATH.read_text()
        fm, _ = parse_frontmatter(content)
        return fm

    def test_has_name(self, frontmatter):
        """Frontmatter includes a name field."""
        assert "name" in frontmatter
        assert frontmatter["name"] == "daily-report"

    def test_has_version(self, frontmatter):
        """Frontmatter includes a version field."""
        assert "version" in frontmatter
        assert isinstance(frontmatter["version"], str)

    def test_has_description(self, frontmatter):
        """Frontmatter includes a description field."""
        assert "description" in frontmatter
        assert len(frontmatter["description"]) > 10


class TestRequiredSections:
    @pytest.fixture(scope="class")
    def body(self):
        content = WORKFLOW_PATH.read_text()
        _, body = parse_frontmatter(content)
        return body

    def test_has_h1_title(self, body):
        """Document has an H1 title."""
        assert any(line.startswith("# ") for line in body.splitlines())

    def test_has_gathering_section(self, body):
        """Describes how to gather cost data."""
        body_lower = body.lower()
        assert "gather" in body_lower or "sessions" in body_lower

    def test_references_openclaw_sessions(self, body):
        """References the openclaw sessions command."""
        assert "openclaw sessions" in body

    def test_references_cron_runs(self, body):
        """References the openclaw cron runs command."""
        assert "openclaw cron runs" in body

    def test_has_output_format_section(self, body):
        """Describes the output format."""
        body_lower = body.lower()
        assert "output" in body_lower or "format" in body_lower

    def test_output_under_15_lines(self, body):
        """Output section mentions the 15-line limit."""
        assert "15 line" in body.lower() or "15-line" in body.lower()

    def test_has_delivery_section(self, body):
        """Describes how to deliver the report."""
        assert "deliver" in body.lower() or "telegram" in body.lower()

    def test_has_cron_setup_section(self, body):
        """Includes cron setup configuration."""
        assert "Cron Setup" in body or "cron setup" in body.lower()

    def test_cron_config_has_schedule(self, body):
        """Cron config includes a schedule expression."""
        assert "0 17 * * *" in body or "0 18 * * *" in body

    def test_cron_config_has_timeout(self, body):
        """Cron config includes a timeout."""
        assert "timeoutSeconds" in body or "timeout" in body.lower()

    def test_has_empathy_pass(self, body):
        """Includes the empathy review pass."""
        assert "empathy" in body.lower() or "Empathy" in body

    def test_has_budget_section(self, body):
        """Describes the expected budget / turn count."""
        assert "budget" in body.lower() or "Budget" in body

    def test_telegram_delivery_target(self, body):
        """References telegram as the delivery channel."""
        assert "telegram" in body.lower()

    def test_has_deployment_note(self, body):
        """Mentions deployment / update behavior."""
        assert "deployment" in body.lower() or "Deployment" in body

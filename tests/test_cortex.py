"""Tests for the Cortex knowledge compiler skill.

Tests the mechanical operations: hashing, lock management, ingest state
tracking, file enumeration, index rebuilding. All tests use a temporary
directory — no cloud storage required.
"""

import os
import subprocess
import time
from pathlib import Path

import pytest

SKILL_PATH = str(Path(__file__).parent / ".." / "skills" / "cortex" / "cortex")


def run_cortex(
    *args: str, env: dict | None = None, cwd: str | None = None
) -> subprocess.CompletedProcess:
    """Run the cortex skill with given arguments."""
    cmd = [SKILL_PATH, *args]
    run_env = os.environ.copy()
    if env:
        run_env.update(env)
    return subprocess.run(
        cmd,
        check=False,
        capture_output=True,
        text=True,
        env=run_env,
        cwd=cwd,
    )


@pytest.fixture
def cortex_store(tmp_path):
    """Create a minimal cortex store structure for testing."""
    store = tmp_path / "cortex"
    knowledge = store / "knowledge"
    raw = store / "raw"

    # Create directory structure
    for d in [
        raw / "documents",
        raw / "notes",
        knowledge / "entities",
        knowledge / "concepts",
        knowledge / "summaries",
        knowledge / "synthesis",
        knowledge / "decisions",
        knowledge / "how-to",
    ]:
        d.mkdir(parents=True)

    # Create initial files
    (knowledge / "index.md").write_text(
        "# Cortex Index\n\nLast updated: 2026-04-11\n"
        "Total pages: 0 | Sources ingested: 0\n\n"
        "## Categories\n\n"
        "| Category | Pages | Sub-index |\n"
        "|----------|-------|-----------|\n"
        "| Entities | 0 | [entities/_index.md](entities/_index.md) |\n\n"
        "## Recent Activity\n\n_No activity yet._\n"
    )
    (knowledge / "log.md").write_text("# Operation Log\n\n_No operations yet._\n")
    (knowledge / ".ingest-state.md").write_text(
        "# Ingest State\n\n"
        "| Path | Hash | Status | Timestamp |\n"
        "|------|------|--------|-----------|\n"
    )

    # Sub-indexes
    for cat in [
        "entities",
        "concepts",
        "summaries",
        "synthesis",
        "decisions",
        "how-to",
    ]:
        (knowledge / cat / "_index.md").write_text(
            f"# {cat.title()}\n\n_No entries yet._\n"
        )

    # Schema
    (store / "schema.md").write_text("# Cortex Schema\n\nTest schema.\n")

    # Config
    config_dir = tmp_path / "config"
    config_dir.mkdir()
    config_file = config_dir / "config"
    config_file.write_text(
        f"CORTEX_STORE_PATH={store}\n"
        f"CORTEX_RAW_PATH={raw}\n"
        f"CORTEX_KNOWLEDGE_PATH={knowledge}\n"
        f"CORTEX_SCHEMA_PATH={store / 'schema.md'}\n"
        f"CLOUD_PROVIDER=test\n"
        f"WRITER_MACHINE=true\n"
    )

    return store, knowledge, raw, config_file


@pytest.fixture
def cortex_env(cortex_store):
    """Return env dict that points cortex at the test store."""
    store, knowledge, raw, config_file = cortex_store
    # Override config dir via XDG or monkey-patching
    # Since the script uses Path.home() / ".config" / "cortex", we need to
    # override HOME to redirect config lookup
    fake_home = config_file.parent.parent
    config_cortex = fake_home / ".config" / "cortex"
    config_cortex.mkdir(parents=True, exist_ok=True)
    # Move config file to expected location
    real_config = config_cortex / "config"
    real_config.write_text(config_file.read_text())
    return {"HOME": str(fake_home)}


class TestScript:
    """Basic script tests."""

    def test_is_executable(self):
        """Skill script exists and is executable."""
        path = Path(SKILL_PATH)
        assert path.exists(), f"Script not found: {SKILL_PATH}"
        assert os.access(path, os.X_OK), "Script is not executable"

    def test_help(self):
        """Help text displays correctly."""
        result = run_cortex("help")
        assert result.returncode == 0
        assert "cortex <command>" in result.stdout
        assert "setup" in result.stdout
        assert "status" in result.stdout
        assert "lock" in result.stdout

    def test_unknown_command(self):
        """Unknown command produces error."""
        result = run_cortex("nonexistent")
        assert result.returncode == 1
        assert "Unknown command" in result.stderr


class TestHash:
    """Content hash tests."""

    def test_hash_file(self, tmp_path, cortex_env):
        """Hash produces consistent output for same content."""
        f = tmp_path / "test.md"
        f.write_text("Hello, world!")
        result = run_cortex("hash", str(f), env=cortex_env)
        assert result.returncode == 0
        hash1 = result.stdout.strip()
        assert len(hash1) == 16  # truncated SHA-256

        # Same content, same hash
        result2 = run_cortex("hash", str(f), env=cortex_env)
        assert result2.stdout.strip() == hash1

    def test_hash_different_content(self, tmp_path, cortex_env):
        """Different content produces different hashes."""
        f1 = tmp_path / "a.md"
        f2 = tmp_path / "b.md"
        f1.write_text("Content A")
        f2.write_text("Content B")

        r1 = run_cortex("hash", str(f1), env=cortex_env)
        r2 = run_cortex("hash", str(f2), env=cortex_env)
        assert r1.stdout.strip() != r2.stdout.strip()

    def test_hash_missing_file(self, cortex_env):
        """Hash of nonexistent file errors."""
        result = run_cortex("hash", "/nonexistent/file.md", env=cortex_env)
        assert result.returncode == 1
        assert "not found" in result.stderr.lower()


class TestLock:
    """Write lock management tests."""

    def test_lock_acquire_release(self, cortex_store, cortex_env):
        """Lock can be acquired and released."""
        _, knowledge, _, _ = cortex_store

        result = run_cortex("lock", env=cortex_env)
        assert result.returncode == 0
        assert "acquired" in result.stdout.lower()
        assert (knowledge / ".lock").exists()

        result = run_cortex("unlock", env=cortex_env)
        assert result.returncode == 0
        assert not (knowledge / ".lock").exists()

    def test_lock_blocks_second_acquire(self, cortex_store, cortex_env):
        """Second lock attempt fails while first is held."""
        _, knowledge, _, _ = cortex_store

        run_cortex("lock", env=cortex_env)
        result = run_cortex("lock", env=cortex_env)
        assert result.returncode == 1
        assert (
            "lock held" in result.stderr.lower()
            or "write lock" in result.stderr.lower()
        )

        # Cleanup
        run_cortex("unlock", env=cortex_env)

    def test_expired_lock_overridden(self, cortex_store, cortex_env):
        """Expired lock gets overridden."""
        _, knowledge, _, _ = cortex_store

        # Write a lock with old timestamp
        lock_file = knowledge / ".lock"
        old_time = time.time() - (31 * 60)  # 31 minutes ago
        lock_file.write_text(f"old-machine | {old_time}")

        result = run_cortex("lock", env=cortex_env)
        assert result.returncode == 0
        assert "overrid" in result.stdout.lower() or "acquired" in result.stdout.lower()

        run_cortex("unlock", env=cortex_env)

    def test_unlock_force(self, cortex_store, cortex_env):
        """Force unlock removes any lock."""
        _, knowledge, _, _ = cortex_store

        lock_file = knowledge / ".lock"
        lock_file.write_text(f"other-machine | {time.time()}")

        result = run_cortex("unlock", "--force", env=cortex_env)
        assert result.returncode == 0
        assert not lock_file.exists()

    def test_unlock_no_lock(self, cortex_store, cortex_env):
        """Unlocking when no lock exists is a no-op."""
        result = run_cortex("unlock", env=cortex_env)
        assert result.returncode == 0


class TestIngestState:
    """Ingest state tracking tests."""

    def test_check_new_file(self, cortex_store, cortex_env):
        """New file reports as not ingested."""
        store, _, raw, _ = cortex_store
        f = raw / "documents" / "test.md"
        f.write_text("Test document content")

        result = run_cortex("check", str(f), env=cortex_env)
        assert result.returncode == 0
        assert "new" in result.stdout.lower()

    def test_mark_and_check(self, cortex_store, cortex_env):
        """File marked as ingested shows as already-ingested."""
        store, _, raw, _ = cortex_store
        f = raw / "documents" / "test.md"
        f.write_text("Test document content")

        run_cortex("mark-ingested", str(f), env=cortex_env)
        result = run_cortex("check", str(f), env=cortex_env)
        assert result.returncode == 0
        assert "already-ingested" in result.stdout.lower()

    def test_mark_pending(self, cortex_store, cortex_env):
        """File can be marked as pending."""
        store, _, raw, _ = cortex_store
        f = raw / "documents" / "test.md"
        f.write_text("Test document content")

        run_cortex("mark-pending", str(f), env=cortex_env)
        result = run_cortex("check", str(f), env=cortex_env)
        assert result.returncode == 0
        assert "pending" in result.stdout.lower()

    def test_changed_file_detected(self, cortex_store, cortex_env):
        """Modified file shows as changed."""
        store, _, raw, _ = cortex_store
        f = raw / "documents" / "test.md"
        f.write_text("Original content")
        run_cortex("mark-ingested", str(f), env=cortex_env)

        # Modify the file
        f.write_text("Updated content")
        result = run_cortex("check", str(f), env=cortex_env)
        assert result.returncode == 0
        assert "changed" in result.stdout.lower() or "new" in result.stdout.lower()


class TestEnumerate:
    """File enumeration tests."""

    def test_enumerate_files(self, cortex_store, cortex_env):
        """Enumerate lists eligible files."""
        _, _, raw, _ = cortex_store
        (raw / "documents" / "readme.md").write_text("# Readme")
        (raw / "documents" / "notes.txt").write_text("Some notes")
        (raw / "documents" / "data.json").write_text("{}")

        result = run_cortex("enumerate", str(raw / "documents"), env=cortex_env)
        assert result.returncode == 0
        assert "readme.md" in result.stdout
        assert "notes.txt" in result.stdout
        assert "data.json" in result.stdout
        assert "Total: 3 files" in result.stdout

    def test_enumerate_skips_sensitive(self, cortex_store, cortex_env):
        """Enumerate skips sensitive files."""
        _, _, raw, _ = cortex_store
        docs = raw / "documents"
        (docs / "readme.md").write_text("# Safe")
        (docs / ".env").write_text("SECRET=bad")
        (docs / "credentials.json").write_text("{}")
        (docs / "server.pem").write_text("cert")
        (docs / "secret-config.yaml").write_text("x: 1")

        result = run_cortex("enumerate", str(docs), env=cortex_env)
        assert "readme.md" in result.stdout
        assert ".env" not in result.stdout.split("Skipped")[0]
        assert "credentials" not in result.stdout.split("Skipped")[0]
        assert "server.pem" not in result.stdout.split("Skipped")[0]
        assert "secret-config" not in result.stdout.split("Skipped")[0]

    def test_enumerate_skips_unsupported(self, cortex_store, cortex_env):
        """Enumerate skips unsupported file types."""
        _, _, raw, _ = cortex_store
        docs = raw / "documents"
        (docs / "readme.md").write_text("# Good")
        (docs / "binary.exe").write_bytes(b"\x00\x01")
        (docs / "archive.zip").write_bytes(b"PK")

        result = run_cortex("enumerate", str(docs), env=cortex_env)
        assert "readme.md" in result.stdout
        assert "binary.exe" not in result.stdout.split("Skipped")[0]

    def test_enumerate_skips_already_ingested(self, cortex_store, cortex_env):
        """Enumerate skips files already ingested."""
        _, _, raw, _ = cortex_store
        docs = raw / "documents"
        f1 = docs / "old.md"
        f2 = docs / "new.md"
        f1.write_text("Already processed")
        f2.write_text("Fresh content")

        run_cortex("mark-ingested", str(f1), env=cortex_env)
        result = run_cortex("enumerate", str(docs), env=cortex_env)
        assert "new.md" in result.stdout
        assert "already ingested" in result.stdout.lower()

    def test_enumerate_estimate(self, cortex_store, cortex_env):
        """Estimate mode shows cost projection."""
        _, _, raw, _ = cortex_store
        docs = raw / "documents"
        (docs / "a.md").write_text("Content A")
        (docs / "b.md").write_text("Content B")

        result = run_cortex("enumerate", str(docs), "--estimate", env=cortex_env)
        assert result.returncode == 0
        assert "Eligible files: 2" in result.stdout
        assert "Estimated API cost" in result.stdout


class TestRebuildIndex:
    """Index rebuilding tests."""

    def test_rebuild_empty(self, cortex_store, cortex_env):
        """Rebuild with no pages creates empty indexes."""
        result = run_cortex("rebuild-index", env=cortex_env)
        assert result.returncode == 0
        assert "0 pages" in result.stdout

    def test_rebuild_with_pages(self, cortex_store, cortex_env):
        """Rebuild with pages populates indexes correctly."""
        _, knowledge, _, _ = cortex_store

        # Create some knowledge pages with frontmatter
        (knowledge / "entities" / "alpaca.md").write_text(
            "---\n"
            "title: Alpaca\n"
            "type: entity\n"
            "sources:\n  - raw/documents/trading.md\n"
            "related: []\n"
            "tags: [trading, api, broker]\n"
            "created: 2026-04-11\n"
            "last_compiled: 2026-04-11\n"
            "confidence: high\n"
            "---\n\n"
            "Alpaca is a trading API.\n"
        )
        (knowledge / "concepts" / "event-driven-architecture.md").write_text(
            "---\n"
            "title: Event-Driven Architecture\n"
            "type: concept\n"
            "sources:\n  - raw/documents/arch.pdf\n"
            "related:\n  - entities/alpaca.md\n"
            "tags: [architecture, patterns]\n"
            "created: 2026-04-11\n"
            "last_compiled: 2026-04-11\n"
            "confidence: medium\n"
            "---\n\n"
            "Async messaging patterns.\n"
        )

        result = run_cortex("rebuild-index", env=cortex_env)
        assert result.returncode == 0
        assert "2 pages" in result.stdout

        # Check sub-indexes
        entity_index = (knowledge / "entities" / "_index.md").read_text()
        assert "Alpaca" in entity_index
        assert "trading" in entity_index

        concept_index = (knowledge / "concepts" / "_index.md").read_text()
        assert "Event-Driven Architecture" in concept_index

        # Check root index
        root_index = (knowledge / "index.md").read_text()
        assert "Entities" in root_index
        assert "Concepts" in root_index

    def test_rebuild_warns_on_bad_frontmatter(self, cortex_store, cortex_env):
        """Rebuild warns about pages without valid frontmatter."""
        _, knowledge, _, _ = cortex_store

        (knowledge / "entities" / "broken.md").write_text(
            "No frontmatter here, just content.\n"
        )

        result = run_cortex("rebuild-index", env=cortex_env)
        assert result.returncode == 0
        assert "No frontmatter" in result.stdout


class TestStatus:
    """Status command tests."""

    def test_status_empty_store(self, cortex_store, cortex_env):
        """Status works on empty store."""
        result = run_cortex("status", env=cortex_env)
        assert result.returncode == 0
        assert "Cortex Status" in result.stdout
        assert "Total" in result.stdout

    def test_status_with_content(self, cortex_store, cortex_env):
        """Status reflects actual content."""
        _, knowledge, raw, _ = cortex_store

        # Add a raw file and a knowledge page
        (raw / "documents" / "test.md").write_text("Raw content")
        (knowledge / "entities" / "test-entity.md").write_text(
            "---\ntitle: Test\ntype: entity\n---\nContent\n"
        )

        result = run_cortex("status", env=cortex_env)
        assert result.returncode == 0
        assert "Raw Sources: 1" in result.stdout

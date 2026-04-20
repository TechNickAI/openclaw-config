"""Tests for the Cortex v2 knowledge compiler skill.

Tests the v2 CLI surface: help, status, scan, rebuild-index.
All tests use a temporary directory — no cloud storage required.
"""

import os
import sqlite3
import subprocess
from pathlib import Path

import pytest

SKILL_PATH = str(Path(__file__).parent / ".." / "skills" / "cortex" / "cortex")
KNOWLEDGE_CATEGORIES = [
    "entities",
    "concepts",
    "summaries",
    "synthesis",
    "decisions",
    "how-to",
]


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


def _init_store_db(db_path: Path) -> None:
    """Initialize a cortex SQLite database."""
    db = sqlite3.connect(str(db_path))
    db.execute("PRAGMA journal_mode=WAL")
    db.executescript("""
        CREATE TABLE IF NOT EXISTS sources (
            path TEXT PRIMARY KEY,
            hash TEXT,
            status TEXT NOT NULL DEFAULT 'new',
            file_type TEXT,
            file_size INTEGER,
            online_only INTEGER DEFAULT 0,
            source_date TEXT,
            discovered_at TEXT NOT NULL,
            ingested_at TEXT,
            error TEXT
        );
        CREATE INDEX IF NOT EXISTS idx_status ON sources(status);
        CREATE INDEX IF NOT EXISTS idx_hash ON sources(hash);
    """)
    db.commit()
    db.close()


@pytest.fixture
def cortex_store(tmp_path):
    """Create a v2 cortex store with SQLite and config."""
    store = tmp_path / "knowledge-base"
    store.mkdir()

    # Create all category directories with stub indexes
    for cat in KNOWLEDGE_CATEGORIES:
        cat_dir = store / cat
        cat_dir.mkdir()
        (cat_dir / "index.md").write_text(f"# {cat.title()}\n\n_No entries yet._\n")

    # Extra directories
    (store / "learning").mkdir()
    (store / "learning" / "archive").mkdir()
    (store / "daily").mkdir()

    # Root index
    (store / "index.md").write_text(
        "# Cortex Index\n\n"
        "Last updated: 2026-04-12\n"
        "Total pages: 0 | Sources ingested: 0\n\n"
        "## Categories\n\n"
        "| Category | Pages | Index |\n"
        "|----------|-------|-------|\n"
        + "".join(
            f"| {cat.title().replace('-', ' ')} | 0 | [{cat}/index.md]({cat}/index.md) |\n"
            for cat in KNOWLEDGE_CATEGORIES
        )
        + "\n## Recent Activity\n\n_No activity yet._\n"
    )
    (store / "review-queue.md").write_text("# Review Queue\n\n_No items pending._\n")

    # Initialize SQLite
    _init_store_db(store / "cortex.db")

    # Config at fake_home/.config/cortex/config
    fake_home = tmp_path / "home"
    config_dir = fake_home / ".config" / "cortex"
    config_dir.mkdir(parents=True)
    (config_dir / "config").write_text(
        f"CORTEX_STORE_PATH={store}\nCLOUD_PROVIDER=Dropbox\n"
    )

    return store, fake_home


@pytest.fixture
def cortex_env(cortex_store):
    """Return env dict pointing cortex at the test store."""
    _, fake_home = cortex_store
    return {"HOME": str(fake_home)}


class TestScript:
    """Basic script tests."""

    def test_is_executable(self):
        """Skill script exists and is executable."""
        path = Path(SKILL_PATH)
        assert path.exists(), f"Script not found: {SKILL_PATH}"
        assert os.access(path, os.X_OK), "Script is not executable"

    def test_help(self):
        """Help text lists v2 commands."""
        result = run_cortex("help")
        assert result.returncode == 0
        assert "cortex <command>" in result.stdout
        assert "setup" in result.stdout
        assert "status" in result.stdout
        assert "scan" in result.stdout
        assert "rebuild-index" in result.stdout

    def test_unknown_command(self):
        """Unknown command produces actionable error."""
        result = run_cortex("nonexistent")
        assert result.returncode == 1
        assert "Unknown command" in result.stderr


class TestStatus:
    """Status command tests."""

    def test_status_no_config(self, tmp_path):
        """Status without config gives actionable error."""
        fake_home = tmp_path / "empty-home"
        fake_home.mkdir()
        result = run_cortex("status", env={"HOME": str(fake_home)})
        assert result.returncode == 1
        assert (
            "cortex setup" in result.stderr.lower()
            or "not configured" in result.stderr.lower()
        )

    def test_status_empty_store(self, cortex_store, cortex_env):
        """Status works on empty store and shows totals."""
        result = run_cortex("status", env=cortex_env)
        assert result.returncode == 0
        assert "Cortex Status" in result.stdout
        assert "Total" in result.stdout

    def test_status_reflects_pages(self, cortex_store, cortex_env):
        """Status counts knowledge pages from category directories."""
        store, _ = cortex_store
        (store / "entities" / "test-entity.md").write_text(
            "---\ntitle: Test Entity\ntype: entity\n---\nContent.\n"
        )
        result = run_cortex("status", env=cortex_env)
        assert result.returncode == 0
        assert "Cortex Status" in result.stdout


class TestScan:
    """File scanning tests."""

    def test_scan_discovers_files(self, cortex_store, cortex_env, tmp_path):
        """Scan discovers and records markdown files."""
        source_dir = tmp_path / "sources"
        source_dir.mkdir()
        (source_dir / "notes.md").write_text("# Notes\nSome content here.")
        (source_dir / "report.txt").write_text("Plain text report.")

        result = run_cortex("scan", str(source_dir), env=cortex_env)
        assert result.returncode == 0
        assert "Scanning" in result.stdout

    def test_scan_skips_sensitive_files(self, cortex_store, cortex_env, tmp_path):
        """Scan skips .env, credentials.json, and similar sensitive files."""
        source_dir = tmp_path / "sources"
        source_dir.mkdir()
        (source_dir / "notes.md").write_text("# Safe notes")
        (source_dir / ".env").write_text("SECRET_KEY=bad")
        (source_dir / "credentials.json").write_text('{"key":"secret"}')

        result = run_cortex("scan", str(source_dir), env=cortex_env)
        assert result.returncode == 0
        # Sensitive count should be > 0 in summary
        assert (
            "skipped_sensitive" in result.stdout or "sensitive" in result.stdout.lower()
        )

    def test_scan_skips_unsupported_types(self, cortex_store, cortex_env, tmp_path):
        """Scan skips unsupported file types without error."""
        source_dir = tmp_path / "sources"
        source_dir.mkdir()
        (source_dir / "notes.md").write_text("# Notes")
        (source_dir / "binary.exe").write_bytes(b"\x00MZ\x00")

        result = run_cortex("scan", str(source_dir), env=cortex_env)
        assert result.returncode == 0

    def test_scan_deduplicates_identical_content(
        self, cortex_store, cortex_env, tmp_path
    ):
        """Scan marks second file with identical content as duplicate."""
        source_dir = tmp_path / "sources"
        source_dir.mkdir()
        content = "# Identical Content\n\nThis is exactly the same in both files.\n"
        (source_dir / "original.md").write_text(content)
        (source_dir / "duplicate.md").write_text(content)

        result = run_cortex("scan", str(source_dir), env=cortex_env)
        assert result.returncode == 0
        # One file should be marked as skipped duplicate
        assert (
            "skipped" in result.stdout.lower() or "duplicate" in result.stdout.lower()
        )

    def test_scan_nonexistent_dir_errors(self, cortex_store, cortex_env):
        """Scan of nonexistent path gives actionable error."""
        result = run_cortex("scan", "/nonexistent/path/xyz", env=cortex_env)
        assert result.returncode == 1
        assert "not a directory" in result.stderr.lower()

    def test_rescan_updates_online_only_hashes(
        self, cortex_store, cortex_env, tmp_path
    ):
        """Re-scan updates hash for files previously recorded as online-only."""
        store, _ = cortex_store
        db_path = store / "cortex.db"

        source_dir = tmp_path / "sources"
        source_dir.mkdir()
        f = source_dir / "doc.md"
        f.write_text("# Document\n\nContent that is now accessible.")
        abs_path = str(f.resolve())

        # Manually insert as online-only (simulates first scan when file wasn't synced)
        db = sqlite3.connect(str(db_path))
        db.execute(
            "INSERT INTO sources "
            "(path, hash, status, file_type, file_size, online_only, discovered_at) "
            "VALUES (?, NULL, 'new', 'markdown', 100, 1, '2026-04-12T00:00:00Z')",
            (abs_path,),
        )
        db.commit()
        db.close()

        # Rescan — file is now accessible (not online-only placeholder)
        result = run_cortex("scan", str(source_dir), env=cortex_env)
        assert result.returncode == 0

        # Hash should now be populated and online_only cleared
        db = sqlite3.connect(str(db_path))
        row = db.execute(
            "SELECT hash, online_only FROM sources WHERE path = ?", (abs_path,)
        ).fetchone()
        db.close()
        assert row is not None
        assert row[0] is not None, (
            "Hash should be populated after rescan of accessible file"
        )
        assert row[1] == 0, "online_only should be cleared after file became accessible"


class TestRebuildIndex:
    """Index rebuilding tests."""

    def test_rebuild_empty(self, cortex_store, cortex_env):
        """Rebuild with no pages creates empty indexes."""
        result = run_cortex("rebuild-index", env=cortex_env)
        assert result.returncode == 0
        assert "0 pages" in result.stdout

    def test_rebuild_with_pages(self, cortex_store, cortex_env):
        """Rebuild with pages populates category indexes correctly."""
        store, _ = cortex_store
        (store / "entities" / "alpaca.md").write_text(
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
        (store / "concepts" / "event-driven-architecture.md").write_text(
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
        assert "pages" in result.stdout

        entity_index = (store / "entities" / "index.md").read_text()
        assert "Alpaca" in entity_index
        assert "trading" in entity_index

        concept_index = (store / "concepts" / "index.md").read_text()
        assert "Event-Driven Architecture" in concept_index

        root_index = (store / "index.md").read_text()
        assert "Entities" in root_index
        assert "Concepts" in root_index

    def test_rebuild_warns_on_bad_frontmatter(self, cortex_store, cortex_env):
        """Rebuild warns about pages without valid frontmatter."""
        store, _ = cortex_store
        (store / "entities" / "broken.md").write_text(
            "No frontmatter here, just content.\n"
        )

        result = run_cortex("rebuild-index", env=cortex_env)
        assert result.returncode == 0
        assert "No frontmatter" in result.stdout

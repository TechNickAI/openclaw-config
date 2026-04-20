"""Tests for Apple Photos skill.

Unit tests mock osxphotos to verify CLI logic without a Photos library.
Integration tests require macOS with Photos.app and osxphotos installed.
"""

import datetime as dt
import importlib.machinery
import importlib.util
import json
import subprocess
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

SKILL_PATH = Path(__file__).parent / ".." / "skills" / "apple-photos" / "apple-photos"

# Check real package availability BEFORE injecting the mock — find_spec doesn't import.
HAS_OSXPHOTOS = importlib.util.find_spec("osxphotos") is not None
HAS_PHOTOS_LIBRARY = HAS_OSXPHOTOS and sys.platform == "darwin"

# Pre-register a mock so the skill script can be imported on non-macOS/CI.
# setdefault preserves the real package if it's already been imported.
_mock_osxphotos = MagicMock()
_mock_osxphotos.QueryOptions = MagicMock
sys.modules.setdefault("osxphotos", _mock_osxphotos)

# Dynamically load the skill script as a module (no .py extension)
_loader = importlib.machinery.SourceFileLoader("apple_photos", str(SKILL_PATH))
spec = importlib.util.spec_from_loader("apple_photos", _loader)
apple_photos = importlib.util.module_from_spec(spec)
spec.loader.exec_module(apple_photos)

requires_osxphotos = pytest.mark.skipif(
    not HAS_OSXPHOTOS,
    reason="osxphotos not installed",
)

requires_photos_library = pytest.mark.skipif(
    not HAS_PHOTOS_LIBRARY,
    reason="No macOS Photos library available",
)


# -- Fixtures ------------------------------------------------------------------


def make_mock_photo(
    uuid="ABC-123",
    filename="IMG_1234.HEIC",
    original_filename="IMG_1234.HEIC",
    date=None,
    path="/photos/IMG_1234.HEIC",
    path_edited=None,
    persons=None,
    albums=None,
    favorite=False,
    hasadjustments=False,
    ismissing=False,
):
    """Create a mock PhotoInfo object."""
    photo = MagicMock()
    photo.uuid = uuid
    photo.filename = filename
    photo.original_filename = original_filename
    photo.date = date or dt.datetime(2026, 3, 15, 10, 30, 0)  # noqa: DTZ001
    photo.path = path
    photo.path_edited = path_edited
    photo.persons = persons or []
    photo.albums = albums or []
    photo.favorite = favorite
    photo.hasadjustments = hasadjustments
    photo.ismissing = ismissing
    return photo


# -- Unit tests: pure functions ------------------------------------------------


class TestParseDate:
    """Tests for date parsing."""

    def test_none_returns_none(self):
        assert apple_photos.parse_date(None) is None

    def test_empty_string_returns_none(self):
        assert apple_photos.parse_date("") is None

    def test_date_only(self):
        result = apple_photos.parse_date("2026-03-15")
        assert result == dt.datetime(2026, 3, 15)  # noqa: DTZ001

    def test_full_iso(self):
        result = apple_photos.parse_date("2026-03-15T10:30:00")
        assert result == dt.datetime(2026, 3, 15, 10, 30, 0)  # noqa: DTZ001

    def test_invalid_date_raises(self):
        with pytest.raises(ValueError):
            apple_photos.parse_date("not-a-date")


class TestSanitizeFilename:
    """Tests for filename sanitization."""

    def test_simple_name_unchanged(self):
        assert apple_photos.sanitize_filename("IMG_1234.HEIC") == "IMG_1234.HEIC"

    def test_preserves_safe_chars(self):
        assert (
            apple_photos.sanitize_filename("2026-03-15_photo (1).jpg")
            == "2026-03-15_photo (1).jpg"
        )

    def test_replaces_slashes(self):
        result = apple_photos.sanitize_filename("path/to/file.jpg")
        assert "/" not in result

    def test_replaces_special_chars(self):
        result = apple_photos.sanitize_filename("photo@#$%!.jpg")
        assert "@" not in result
        assert "#" not in result

    def test_strips_whitespace(self):
        result = apple_photos.sanitize_filename("  photo.jpg  ")
        assert result == "photo.jpg"


class TestPhotoToDict:
    """Tests for photo-to-dict conversion."""

    def test_basic_conversion(self):
        photo = make_mock_photo(
            uuid="ABC-123",
            filename="IMG_1234.HEIC",
            persons=["Alice", "Bob"],
            albums=["Vacation"],
        )
        result = apple_photos.photo_to_dict(photo)
        assert result["uuid"] == "ABC-123"
        assert result["filename"] == "IMG_1234.HEIC"
        assert result["persons"] == ["Alice", "Bob"]
        assert result["albums"] == ["Vacation"]
        assert result["date"] == "2026-03-15T10:30:00"

    def test_both_paths_present(self):
        photo = make_mock_photo(
            path="/photos/original.heic",
            path_edited="/photos/edited.heic",
        )
        result = apple_photos.photo_to_dict(photo)
        assert result["original_path"] == "/photos/original.heic"
        assert result["edited_path"] == "/photos/edited.heic"

    def test_no_edited_path(self):
        photo = make_mock_photo(path="/photos/original.heic", path_edited=None)
        result = apple_photos.photo_to_dict(photo)
        assert result["original_path"] == "/photos/original.heic"
        assert result["edited_path"] is None

    def test_none_date(self):
        photo = make_mock_photo()
        photo.date = None
        result = apple_photos.photo_to_dict(photo)
        assert result["date"] is None

    def test_deduplicates_persons(self):
        photo = make_mock_photo(persons=["Alice", "Alice", "Bob"])
        result = apple_photos.photo_to_dict(photo)
        assert result["persons"] == ["Alice", "Bob"]

    def test_sorts_albums(self):
        photo = make_mock_photo(albums=["Zebra", "Alpha"])
        result = apple_photos.photo_to_dict(photo)
        assert result["albums"] == ["Alpha", "Zebra"]


class TestUniquePath:
    """Tests for collision-safe path generation."""

    def test_no_collision(self, tmp_path):
        result = apple_photos.unique_path(tmp_path, "photo.jpg")
        assert result == tmp_path / "photo.jpg"

    def test_collision_appends_counter(self, tmp_path):
        (tmp_path / "photo.jpg").write_text("existing")
        result = apple_photos.unique_path(tmp_path, "photo.jpg")
        assert result == tmp_path / "photo_1.jpg"

    def test_multiple_collisions(self, tmp_path):
        (tmp_path / "photo.jpg").write_text("existing")
        (tmp_path / "photo_1.jpg").write_text("existing")
        result = apple_photos.unique_path(tmp_path, "photo.jpg")
        assert result == tmp_path / "photo_2.jpg"


# -- Unit tests: argparser -----------------------------------------------------


class TestParser:
    """Tests for argument parser construction."""

    def test_parser_builds(self):
        parser = apple_photos.build_parser()
        assert parser is not None

    def test_people_subcommand(self):
        parser = apple_photos.build_parser()
        args = parser.parse_args(["people", "--limit", "10"])
        assert args.command == "people"
        assert args.limit == 10

    def test_query_subcommand(self):
        parser = apple_photos.build_parser()
        args = parser.parse_args(
            [
                "query",
                "--person",
                "Alice",
                "--after",
                "2026-01-01",
                "--json",
            ]
        )
        assert args.command == "query"
        assert args.person == ["Alice"]
        assert args.after == "2026-01-01"
        assert args.json is True

    def test_query_multiple_persons(self):
        parser = apple_photos.build_parser()
        args = parser.parse_args(
            [
                "query",
                "--person",
                "Alice",
                "--person",
                "Bob",
            ]
        )
        assert args.person == ["Alice", "Bob"]

    def test_export_subcommand(self):
        parser = apple_photos.build_parser()
        args = parser.parse_args(
            [
                "export",
                "/Users/test/out",
                "--person",
                "Alice",
                "--dry-run",
            ]
        )
        assert args.command == "export"
        assert args.dest == "/Users/test/out"
        assert args.dry_run is True

    def test_no_subcommand_exits(self):
        parser = apple_photos.build_parser()
        args = parser.parse_args([])
        assert args.command is None


# -- Unit tests: subcommand logic with mocked DB ------------------------------


class TestCmdPeople:
    """Tests for the people subcommand with mocked PhotosDB."""

    def test_lists_people_sorted_by_count(self, capsys):
        mock_db = MagicMock()
        mock_db.persons = ["Alice", "Bob", "_UNKNOWN_"]
        mock_db.persons_as_dict = {
            "Alice": ["p1", "p2", "p3"],
            "Bob": ["p1"],
            "_UNKNOWN_": ["p1", "p2"],
        }

        parser = apple_photos.build_parser()
        args = parser.parse_args(["people", "--limit", "10"])

        with patch.object(apple_photos, "get_db", return_value=mock_db):
            apple_photos.cmd_people(args)

        output = capsys.readouterr().out
        lines = output.strip().split("\n")
        assert len(lines) == 2  # _UNKNOWN_ excluded
        assert lines[0].startswith("3\t")
        assert "Alice" in lines[0]
        assert lines[1].startswith("1\t")
        assert "Bob" in lines[1]

    def test_includes_unknown_when_flagged(self, capsys):
        mock_db = MagicMock()
        mock_db.persons = ["Alice", "_UNKNOWN_"]
        mock_db.persons_as_dict = {
            "Alice": ["p1"],
            "_UNKNOWN_": ["p1", "p2"],
        }

        parser = apple_photos.build_parser()
        args = parser.parse_args(["people", "--include-unknown"])

        with patch.object(apple_photos, "get_db", return_value=mock_db):
            apple_photos.cmd_people(args)

        output = capsys.readouterr().out
        assert "_UNKNOWN_" in output


class TestCmdQuery:
    """Tests for the query subcommand with mocked PhotosDB."""

    def test_json_output(self, capsys):
        mock_db = MagicMock()
        mock_db.query.return_value = [
            make_mock_photo(uuid="1", filename="a.jpg"),
            make_mock_photo(uuid="2", filename="b.jpg"),
        ]

        parser = apple_photos.build_parser()
        args = parser.parse_args(["query", "--json", "--limit", "10"])

        with patch.object(apple_photos, "get_db", return_value=mock_db):
            apple_photos.cmd_query(args)

        output = capsys.readouterr().out
        data = json.loads(output)
        assert len(data) == 2
        assert data[0]["uuid"] == "1"

    def test_text_output(self, capsys):
        mock_db = MagicMock()
        mock_db.query.return_value = [
            make_mock_photo(filename="photo.jpg", path="/photos/photo.jpg"),
        ]

        parser = apple_photos.build_parser()
        args = parser.parse_args(["query"])

        with patch.object(apple_photos, "get_db", return_value=mock_db):
            apple_photos.cmd_query(args)

        output = capsys.readouterr().out
        assert "photo.jpg" in output
        assert "\t" in output

    def test_limit_applied(self, capsys):
        mock_db = MagicMock()
        mock_db.query.return_value = [make_mock_photo(uuid=str(i)) for i in range(10)]

        parser = apple_photos.build_parser()
        args = parser.parse_args(["query", "--json", "--limit", "3"])

        with patch.object(apple_photos, "get_db", return_value=mock_db):
            apple_photos.cmd_query(args)

        data = json.loads(capsys.readouterr().out)
        assert len(data) == 3


class TestCmdExport:
    """Tests for the export subcommand with mocked PhotosDB."""

    def test_dry_run_no_copy(self, capsys, tmp_path):
        mock_photo = make_mock_photo(
            path=str(tmp_path / "source.jpg"),
            original_filename="source.jpg",
        )
        # Create the source file so the exists() check passes
        (tmp_path / "source.jpg").write_text("fake image data")

        mock_db = MagicMock()
        mock_db.query.return_value = [mock_photo]

        dest = tmp_path / "output"
        parser = apple_photos.build_parser()
        args = parser.parse_args(["export", str(dest), "--dry-run"])

        with patch.object(apple_photos, "get_db", return_value=mock_db):
            apple_photos.cmd_export(args)

        output = capsys.readouterr().out
        assert "DRYRUN" in output
        assert "Exported 1 item(s)" in output
        # Dest dir is created but no files copied
        assert dest.exists()
        assert not list(dest.glob("*"))

    def test_actual_copy(self, capsys, tmp_path):
        source_file = tmp_path / "source.jpg"
        source_file.write_text("fake image data")

        mock_photo = make_mock_photo(
            path=str(source_file),
            original_filename="source.jpg",
        )

        mock_db = MagicMock()
        mock_db.query.return_value = [mock_photo]

        dest = tmp_path / "output"
        parser = apple_photos.build_parser()
        args = parser.parse_args(["export", str(dest)])

        with patch.object(apple_photos, "get_db", return_value=mock_db):
            apple_photos.cmd_export(args)

        output = capsys.readouterr().out
        assert "COPIED" in output
        assert "Exported 1 item(s)" in output
        exported = list(dest.glob("*"))
        assert len(exported) == 1
        assert exported[0].read_text() == "fake image data"

    def test_skips_missing_source(self, capsys, tmp_path):
        mock_photo = make_mock_photo(
            path="/nonexistent/photo.jpg",
            original_filename="photo.jpg",
        )

        mock_db = MagicMock()
        mock_db.query.return_value = [mock_photo]

        dest = tmp_path / "output"
        parser = apple_photos.build_parser()
        args = parser.parse_args(["export", str(dest)])

        with patch.object(apple_photos, "get_db", return_value=mock_db):
            apple_photos.cmd_export(args)

        output = capsys.readouterr().out
        assert "Exported 0 item(s)" in output

    def test_filename_collision_appends_suffix(self, capsys, tmp_path):
        source1 = tmp_path / "source1.jpg"
        source2 = tmp_path / "source2.jpg"
        source1.write_text("first photo")
        source2.write_text("second photo")

        same_date = dt.datetime(2026, 3, 15, 10, 30, 0)  # noqa: DTZ001
        mock_photos = [
            make_mock_photo(
                path=str(source1), original_filename="IMG.jpg", date=same_date
            ),
            make_mock_photo(
                path=str(source2), original_filename="IMG.jpg", date=same_date
            ),
        ]

        mock_db = MagicMock()
        mock_db.query.return_value = mock_photos

        dest = tmp_path / "output"
        parser = apple_photos.build_parser()
        args = parser.parse_args(["export", str(dest)])

        with patch.object(apple_photos, "get_db", return_value=mock_db):
            apple_photos.cmd_export(args)

        exported = sorted(dest.glob("*"))
        assert len(exported) == 2
        contents = {f.read_text() for f in exported}
        assert contents == {"first photo", "second photo"}

    def test_prefers_edited_when_flagged(self, capsys, tmp_path):
        original = tmp_path / "original.jpg"
        edited = tmp_path / "edited.jpg"
        original.write_text("original")
        edited.write_text("edited version")

        mock_photo = make_mock_photo(
            path=str(original),
            path_edited=str(edited),
            original_filename="photo.jpg",
        )

        mock_db = MagicMock()
        mock_db.query.return_value = [mock_photo]

        dest = tmp_path / "output"
        parser = apple_photos.build_parser()
        args = parser.parse_args(["export", str(dest), "--edited"])

        with patch.object(apple_photos, "get_db", return_value=mock_db):
            apple_photos.cmd_export(args)

        exported = list(dest.glob("*"))
        assert len(exported) == 1
        assert exported[0].read_text() == "edited version"


# -- Integration tests ---------------------------------------------------------


@requires_photos_library
class TestIntegrationPeople:
    """Integration tests that run against a real Photos library."""

    def test_people_runs(self):
        result = subprocess.run(
            [sys.executable, str(SKILL_PATH), "people", "--limit", "5"],
            capture_output=True,
            text=True,
            check=False,
        )
        assert result.returncode == 0

    def test_people_output_has_tabs(self):
        result = subprocess.run(
            [sys.executable, str(SKILL_PATH), "people", "--limit", "3"],
            capture_output=True,
            text=True,
            check=False,
        )
        if result.stdout.strip():
            for line in result.stdout.strip().split("\n"):
                assert "\t" in line


@requires_photos_library
class TestIntegrationQuery:
    """Integration tests for query subcommand."""

    def test_query_json_is_valid(self):
        result = subprocess.run(
            [sys.executable, str(SKILL_PATH), "query", "--limit", "2", "--json"],
            capture_output=True,
            text=True,
            check=False,
        )
        assert result.returncode == 0
        if result.stdout.strip():
            data = json.loads(result.stdout)
            assert isinstance(data, list)

"""Unit tests for note.py."""

import io
import tempfile
import unittest
from argparse import Namespace
from datetime import date
from pathlib import Path
from unittest.mock import patch

from note import cmd_archive, cmd_new, cmd_temp, get_editor, get_notes_dir, get_temp_dir


class TestGetNotesDir(unittest.TestCase):
    """Tests for get_notes_dir()."""

    @patch.dict("os.environ", {"PERSONAL_NOTES_DIR": "/tmp/notes"})
    def test_returns_value_when_set(self):
        self.assertEqual(get_notes_dir(), "/tmp/notes")

    @patch.dict("os.environ", {}, clear=True)
    def test_exits_when_missing(self):
        with self.assertRaises(SystemExit) as ctx:
            get_notes_dir()
        self.assertEqual(ctx.exception.code, 1)

    @patch.dict("os.environ", {"PERSONAL_NOTES_DIR": ""})
    def test_exits_when_empty(self):
        with self.assertRaises(SystemExit) as ctx:
            get_notes_dir()
        self.assertEqual(ctx.exception.code, 1)

    @patch("sys.stderr", new_callable=io.StringIO)
    @patch.dict("os.environ", {}, clear=True)
    def test_prints_error_when_missing(self, mock_stderr):
        with self.assertRaises(SystemExit):
            get_notes_dir()
        self.assertIn("PERSONAL_NOTES_DIR", mock_stderr.getvalue())


class TestGetEditor(unittest.TestCase):
    """Tests for get_editor()."""

    @patch.dict("os.environ", {"PERSONAL_NOTES_EDITOR": "vim"})
    def test_returns_value_when_set(self):
        self.assertEqual(get_editor(), "vim")

    @patch.dict("os.environ", {}, clear=True)
    def test_exits_when_missing(self):
        with self.assertRaises(SystemExit) as ctx:
            get_editor()
        self.assertEqual(ctx.exception.code, 1)

    @patch.dict("os.environ", {"PERSONAL_NOTES_EDITOR": ""})
    def test_exits_when_empty(self):
        with self.assertRaises(SystemExit) as ctx:
            get_editor()
        self.assertEqual(ctx.exception.code, 1)

    @patch("sys.stderr", new_callable=io.StringIO)
    @patch.dict("os.environ", {}, clear=True)
    def test_prints_error_when_missing(self, mock_stderr):
        with self.assertRaises(SystemExit):
            get_editor()
        self.assertIn("PERSONAL_NOTES_EDITOR", mock_stderr.getvalue())


class TestGetTempDir(unittest.TestCase):
    """Tests for get_temp_dir()."""

    @patch.dict("os.environ", {"PERSONAL_NOTES_TEMP_DIR": "/tmp/temp"})
    def test_returns_value_when_set(self):
        self.assertEqual(get_temp_dir(), "/tmp/temp")

    @patch.dict("os.environ", {}, clear=True)
    def test_exits_when_missing(self):
        with self.assertRaises(SystemExit) as ctx:
            get_temp_dir()
        self.assertEqual(ctx.exception.code, 1)

    @patch.dict("os.environ", {"PERSONAL_NOTES_TEMP_DIR": ""})
    def test_exits_when_empty(self):
        with self.assertRaises(SystemExit) as ctx:
            get_temp_dir()
        self.assertEqual(ctx.exception.code, 1)

    @patch("sys.stderr", new_callable=io.StringIO)
    @patch.dict("os.environ", {}, clear=True)
    def test_prints_error_when_missing(self, mock_stderr):
        with self.assertRaises(SystemExit):
            get_temp_dir()
        self.assertIn("PERSONAL_NOTES_TEMP_DIR", mock_stderr.getvalue())


FAKE_DATE = date(2025, 7, 15)


class TestCmdNew(unittest.TestCase):
    """Tests for cmd_new()."""

    def setUp(self):
        self._tmpdir = tempfile.TemporaryDirectory()
        self.tmpdir = self._tmpdir.name

        self.env_patch = patch.dict(
            "os.environ",
            {
                "PERSONAL_NOTES_DIR": self.tmpdir,
                "PERSONAL_NOTES_EDITOR": "vim",
            },
        )
        self.env_patch.start()

        self.date_patch = patch("note.date")
        self.mock_date = self.date_patch.start()
        self.mock_date.today.return_value = FAKE_DATE
        self.mock_date.side_effect = lambda *a, **kw: date(*a, **kw)

        self.popen_patch = patch("note.subprocess.Popen")
        self.mock_popen = self.popen_patch.start()

    def tearDown(self):
        self.popen_patch.stop()
        self.date_patch.stop()
        self.env_patch.stop()
        self._tmpdir.cleanup()

    def _expected_dir(self):
        return Path(self.tmpdir) / "notes" / "2025"

    def _expected_file(self, slug):
        return self._expected_dir() / f"2025-07-15_{slug}.txt"

    def test_creates_directory_structure(self):
        cmd_new(Namespace(name=["My", "Note"]))
        self.assertTrue(self._expected_dir().is_dir())

    def test_creates_file(self):
        cmd_new(Namespace(name=["My", "Note"]))
        filepath = self._expected_file("my_note")
        self.assertTrue(filepath.exists())
        self.assertEqual(filepath.read_text(), "")

    def test_slug_is_lowercased(self):
        cmd_new(Namespace(name=["UPPER", "CASE"]))
        filepath = self._expected_file("upper_case")
        self.assertTrue(filepath.exists())

    def test_multi_word_name(self):
        cmd_new(Namespace(name=["One", "Two", "Three"]))
        filepath = self._expected_file("one_two_three")
        self.assertTrue(filepath.exists())

    def test_prints_created_message(self):
        with patch("sys.stdout", new_callable=io.StringIO) as mock_stdout:
            cmd_new(Namespace(name=["My", "Note"]))
        output = mock_stdout.getvalue()
        self.assertIn("Created file:", output)
        self.assertIn("2025-07-15_my_note.txt", output)

    def test_opens_editor(self):
        cmd_new(Namespace(name=["My", "Note"]))
        self.mock_popen.assert_called_once()
        call_args = self.mock_popen.call_args
        cmd_str = call_args[0][0]
        self.assertIn("vim", cmd_str)
        self.assertIn("2025-07-15_my_note.txt", cmd_str)
        self.assertTrue(call_args[1]["shell"])


class TestCmdTemp(unittest.TestCase):
    """Tests for cmd_temp()."""

    def setUp(self):
        self._tmpdir = tempfile.TemporaryDirectory()
        self.tmpdir = self._tmpdir.name

        self.env_patch = patch.dict(
            "os.environ",
            {
                "PERSONAL_NOTES_TEMP_DIR": self.tmpdir,
                "PERSONAL_NOTES_EDITOR": "vim",
            },
        )
        self.env_patch.start()

        self.date_patch = patch("note.date")
        self.mock_date = self.date_patch.start()
        self.mock_date.today.return_value = FAKE_DATE
        self.mock_date.side_effect = lambda *a, **kw: date(*a, **kw)

        self.popen_patch = patch("note.subprocess.Popen")
        self.mock_popen = self.popen_patch.start()

    def tearDown(self):
        self.popen_patch.stop()
        self.date_patch.stop()
        self.env_patch.stop()
        self._tmpdir.cleanup()

    def _expected_file(self, slug):
        return Path(self.tmpdir) / f"2025-07-15_{slug}.txt"

    def test_creates_file_with_name(self):
        cmd_temp(Namespace(name=["My", "Temp"]))
        filepath = self._expected_file("my_temp")
        self.assertTrue(filepath.exists())
        self.assertEqual(filepath.read_text(), "")

    @patch("note.os.urandom", return_value=b"\xab\xcd")
    def test_creates_file_without_name(self, _mock_urandom):
        cmd_temp(Namespace(name=[]))
        filepath = self._expected_file("abcd")
        self.assertTrue(filepath.exists())

    @patch("note.os.urandom", return_value=b"\xab\xcd")
    def test_random_slug_when_no_name(self, _mock_urandom):
        cmd_temp(Namespace(name=[]))
        files = list(Path(self.tmpdir).iterdir())
        self.assertEqual(len(files), 1)
        self.assertIn("abcd", files[0].name)

    def test_slug_is_lowercased(self):
        cmd_temp(Namespace(name=["UPPER"]))
        filepath = self._expected_file("upper")
        self.assertTrue(filepath.exists())

    def test_files_in_temp_dir_directly(self):
        cmd_temp(Namespace(name=["My", "Temp"]))
        filepath = self._expected_file("my_temp")
        self.assertEqual(filepath.parent, Path(self.tmpdir))

    def test_prints_created_temp_message(self):
        with patch("sys.stdout", new_callable=io.StringIO) as mock_stdout:
            cmd_temp(Namespace(name=["My", "Temp"]))
        output = mock_stdout.getvalue()
        self.assertIn("Created temp file:", output)
        self.assertIn("2025-07-15_my_temp.txt", output)

    def test_opens_editor(self):
        cmd_temp(Namespace(name=["My", "Temp"]))
        self.mock_popen.assert_called_once()
        call_args = self.mock_popen.call_args
        cmd_str = call_args[0][0]
        self.assertIn("vim", cmd_str)
        self.assertIn("2025-07-15_my_temp.txt", cmd_str)
        self.assertTrue(call_args[1]["shell"])


class TestCmdArchive(unittest.TestCase):
    """Tests for cmd_archive()."""

    def setUp(self):
        self._tmpdir = tempfile.TemporaryDirectory()
        self.notes_root = Path(self._tmpdir.name)
        self.archive_path = self.notes_root / ".archive"

        self.env_patch = patch.dict(
            "os.environ", {"PERSONAL_NOTES_DIR": str(self.notes_root)}
        )
        self.env_patch.start()

    def tearDown(self):
        self.env_patch.stop()
        self._tmpdir.cleanup()

    def _make_note(self, name, content=""):
        """Create a note file inside notes_root and return its path."""
        filepath = self.notes_root / name
        filepath.write_text(content)
        return filepath

    def test_creates_archive_directory(self):
        src = self._make_note("note.txt")
        cmd_archive(Namespace(files=[str(src)]))
        self.assertTrue(self.archive_path.is_dir())

    def test_moves_file_to_archive(self):
        src = self._make_note("note.txt", "hello")
        cmd_archive(Namespace(files=[str(src)]))
        dest = self.archive_path / "note.txt"
        self.assertFalse(src.exists())
        self.assertTrue(dest.exists())
        self.assertEqual(dest.read_text(), "hello")

    def test_archives_multiple_files(self):
        src1 = self._make_note("a.txt")
        src2 = self._make_note("b.txt")
        cmd_archive(Namespace(files=[str(src1), str(src2)]))
        self.assertTrue((self.archive_path / "a.txt").exists())
        self.assertTrue((self.archive_path / "b.txt").exists())
        self.assertFalse(src1.exists())
        self.assertFalse(src2.exists())

    def test_collision_renames_with_counter(self):
        src1 = self._make_note("note.txt", "first")
        cmd_archive(Namespace(files=[str(src1)]))
        src2 = self._make_note("note.txt", "second")
        cmd_archive(Namespace(files=[str(src2)]))
        self.assertTrue((self.archive_path / "note.txt").exists())
        self.assertTrue((self.archive_path / "note_1.txt").exists())
        self.assertEqual((self.archive_path / "note.txt").read_text(), "first")
        self.assertEqual((self.archive_path / "note_1.txt").read_text(), "second")

    def test_collision_counter_increments(self):
        for i in range(3):
            src = self._make_note("note.txt", str(i))
            cmd_archive(Namespace(files=[str(src)]))
        self.assertTrue((self.archive_path / "note.txt").exists())
        self.assertTrue((self.archive_path / "note_1.txt").exists())
        self.assertTrue((self.archive_path / "note_2.txt").exists())

    def test_error_if_not_a_file(self):
        with patch("sys.stderr", new_callable=io.StringIO) as mock_stderr:
            cmd_archive(Namespace(files=[str(self.notes_root / "nonexistent.txt")]))
        self.assertIn("is not a file", mock_stderr.getvalue())

    def test_error_if_outside_notes_dir(self):
        with tempfile.NamedTemporaryFile() as outside_file:
            with patch("sys.stderr", new_callable=io.StringIO) as mock_stderr:
                cmd_archive(Namespace(files=[outside_file.name]))
        self.assertIn("PERSONAL_NOTES_DIR", mock_stderr.getvalue())

    def test_skips_bad_file_continues_to_next(self):
        good = self._make_note("good.txt")
        cmd_archive(Namespace(files=["nonexistent.txt", str(good)]))
        self.assertTrue((self.archive_path / "good.txt").exists())

    def test_prints_archived_message(self):
        src = self._make_note("note.txt")
        with patch("sys.stdout", new_callable=io.StringIO) as mock_stdout:
            cmd_archive(Namespace(files=[str(src)]))
        output = mock_stdout.getvalue()
        self.assertIn("Archived:", output)
        self.assertIn("note.txt", output)


if __name__ == "__main__":
    unittest.main()

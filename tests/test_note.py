"""Unit tests for note.py."""

import io
import tempfile
import unittest
from argparse import Namespace
from datetime import date
from pathlib import Path
from unittest.mock import patch

from note import cmd_new, get_editor, get_notes_dir, get_temp_dir


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


if __name__ == "__main__":
    unittest.main()

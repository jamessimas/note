"""Unit tests for environment-variable getter functions in note.py."""

import io
import unittest
from unittest.mock import patch

from note import get_editor, get_notes_dir, get_temp_dir


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


if __name__ == "__main__":
    unittest.main()

#!/usr/bin/env python3
"""A simple CLI tool for creating notes."""

import argparse
import os
import subprocess
import sys
from datetime import date
from pathlib import Path


def get_notes_dir():
    """Return the $PERSONAL_NOTES directory or exit with an error."""
    notes_dir = os.environ.get("PERSONAL_NOTES")
    if not notes_dir:
        print(
            "Error: $PERSONAL_NOTES environment variable is not set.", file=sys.stderr
        )
        sys.exit(1)
    return notes_dir


def get_editor():
    """Return the $PERSONAL_NOTES_EDITOR value or exit with an error."""
    editor = os.environ.get("PERSONAL_NOTES_EDITOR")
    if not editor:
        print("Error: $PERSONAL_NOTES_EDITOR environment variable is not set.", file=sys.stderr)
        sys.exit(1)
    return editor


def get_temp_dir():
    """Return the $PERSONAL_NOTES_TEMP_DIR directory or exit with an error."""
    temp_dir = os.environ.get("PERSONAL_NOTES_TEMP_DIR")
    if not temp_dir:
        print(
            "Error: $PERSONAL_NOTES_TEMP_DIR environment variable is not set.",
            file=sys.stderr,
        )
        sys.exit(1)
    return temp_dir


def cmd_new(args):
    """Create a new note file and open it in $PERSONAL_NOTES_EDITOR."""
    notes_dir = get_notes_dir()
    editor = get_editor()

    today = date.today()
    year = today.strftime("%Y")
    date_prefix = today.strftime("%Y-%m-%d")
    slug = "-".join(word.lower() for word in args.name)

    folder = Path(notes_dir) / "notes" / year
    folder.mkdir(parents=True, exist_ok=True)

    filepath = folder / f"{date_prefix}_{slug}.txt"
    filepath.touch()

    print(f"Created file: {filepath}")

    subprocess.Popen(f"{editor} {filepath}", shell=True)


def cmd_temp(args):
    """Create a temporary note file and open it in $PERSONAL_NOTES_EDITOR."""
    temp_dir = get_temp_dir()
    editor = get_editor()

    date_prefix = date.today().strftime("%Y-%m-%d")

    if args.name:
        slug = "-".join(word.lower() for word in args.name)
    else:
        slug = os.urandom(2).hex()

    folder = Path(temp_dir)
    folder.mkdir(parents=True, exist_ok=True)

    filepath = folder / f"{date_prefix}_{slug}.txt"
    filepath.touch()

    print(f"Created temp file: {filepath}")

    subprocess.Popen(f"{editor} {filepath}", shell=True)


def cmd_recent(args):
    """Open the most recently edited note in $PERSONAL_NOTES_EDITOR."""
    notes_dir = get_notes_dir()
    editor = get_editor()

    notes_path = Path(notes_dir) / "notes"
    files = [f for f in notes_path.rglob("*") if f.is_file()]

    if not files:
        print("Error: No notes found.", file=sys.stderr)
        sys.exit(1)

    most_recent = max(files, key=lambda f: f.stat().st_mtime)
    subprocess.Popen(f"{editor} {most_recent}", shell=True)


def main():
    parser = argparse.ArgumentParser(
        description="A simple CLI tool for creating notes.",
    )
    subparsers = parser.add_subparsers(dest="command")

    new_parser = subparsers.add_parser("new", help="Create a new note")
    new_parser.add_argument(
        "name",
        nargs="+",
        help="The name of the note (e.g. My New Note)",
    )

    temp_parser = subparsers.add_parser("temp", help="Create a temporary note")
    temp_parser.add_argument(
        "name",
        nargs="*",
        help="Optional name of the note (random if omitted)",
    )

    subparsers.add_parser("recent", help="Open the most recently edited note")

    args = parser.parse_args()

    if args.command is None:
        parser.print_help()
        sys.exit(0)

    if args.command == "new":
        cmd_new(args)
    elif args.command == "temp":
        cmd_temp(args)
    elif args.command == "recent":
        cmd_recent(args)


if __name__ == "__main__":
    main()

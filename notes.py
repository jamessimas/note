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
    """Return the $EDITOR value or exit with an error."""
    editor = os.environ.get("EDITOR")
    if not editor:
        print("Error: $EDITOR environment variable is not set.", file=sys.stderr)
        sys.exit(1)
    return editor


def cmd_new(args):
    """Create a new note file and open it in $EDITOR."""
    notes_dir = get_notes_dir()
    editor = get_editor()

    editor = os.environ.get("EDITOR")
    if not editor:
        print("Error: $EDITOR environment variable is not set.", file=sys.stderr)
        sys.exit(1)

    today = date.today()
    year = today.strftime("%Y")
    date_prefix = today.strftime("%Y-%m-%d")
    slug = "-".join(word.lower() for word in args.name)

    folder = Path(notes_dir) / "notes" / year
    folder.mkdir(parents=True, exist_ok=True)

    filepath = folder / f"{date_prefix}_{slug}.txt"
    filepath.touch()

    subprocess.Popen(f"{editor} {filepath}", shell=True)


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

    args = parser.parse_args()

    if args.command is None:
        parser.print_help()
        sys.exit(0)

    if args.command == "new":
        cmd_new(args)


if __name__ == "__main__":
    main()

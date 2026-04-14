#!/usr/bin/env python3
"""A simple CLI tool for creating notes."""

import argparse
import os
import subprocess
import sys
from datetime import date
from pathlib import Path


DEFAULT_RECENT_COUNT = 5


def get_notes_dir():
    """Return the $PERSONAL_NOTES_DIR directory or exit with an error."""
    notes_dir = os.environ.get("PERSONAL_NOTES_DIR")
    if not notes_dir:
        print(
            "Error: $PERSONAL_NOTES_DIR environment variable is not set.",
            file=sys.stderr,
        )
        sys.exit(1)
    return notes_dir


def get_editor():
    """Return the $PERSONAL_NOTES_EDITOR value or exit with an error."""
    editor = os.environ.get("PERSONAL_NOTES_EDITOR")
    if not editor:
        print(
            "Error: $PERSONAL_NOTES_EDITOR environment variable is not set.",
            file=sys.stderr,
        )
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
    slug = "_".join(word.lower() for word in args.name)

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
        slug = "_".join(word.lower() for word in args.name)
    else:
        slug = os.urandom(2).hex()

    folder = Path(temp_dir)
    folder.mkdir(parents=True, exist_ok=True)

    filepath = folder / f"{date_prefix}_{slug}.txt"
    filepath.touch()

    print(f"Created temp file: {filepath}")

    subprocess.Popen(f"{editor} {filepath}", shell=True)


def cmd_recent(args):
    """Select from the 5 most recently edited notes via fzf."""
    notes_dir = get_notes_dir()
    editor = get_editor()

    notes_path = Path(notes_dir) / "notes"
    files = [f for f in notes_path.rglob("*") if f.is_file()]

    if not files:
        print("Error: No notes found.", file=sys.stderr)
        sys.exit(1)

    files.sort(key=lambda f: f.stat().st_mtime, reverse=True)
    recent = [str(f) for f in files[: args.count]]

    fzf_cmd = [
        "fzf",
        "--preview",
        "bat --color always {}",
        "--multi",
    ]

    result = subprocess.run(
        fzf_cmd,
        input="\n".join(recent),
        capture_output=True,
        text=True,
    )

    if result.returncode != 0:
        sys.exit(0)

    selected = [f for f in result.stdout.strip().splitlines() if f]
    for filepath in selected:
        subprocess.Popen(f"{editor} {filepath}", shell=True)


def cmd_find(args):
    """Interactively find and open notes with fzf."""
    notes_dir = get_notes_dir()
    editor = get_editor()

    notes_path = Path(notes_dir) / "notes"
    files = [str(f) for f in notes_path.rglob("*") if f.is_file()]

    if not files:
        print("Error: No notes found.", file=sys.stderr)
        sys.exit(1)

    query = " ".join(args.query) if args.query else ""

    fzf_cmd = [
        "fzf",
        "--preview",
        "bat --color always {}",
        "--multi",
        "--query",
        query,
    ]

    result = subprocess.run(
        fzf_cmd,
        input="\n".join(files),
        capture_output=True,
        text=True,
    )

    if result.returncode != 0:
        sys.exit(0)

    selected = [f for f in result.stdout.strip().splitlines() if f]
    for filepath in selected:
        subprocess.Popen(f"{editor} {filepath}", shell=True)


def cmd_sync(args):
    """Run `make sync` in $PERSONAL_NOTES_DIR."""
    notes_dir = get_notes_dir()
    result = subprocess.run(["make", "sync"], cwd=notes_dir)
    sys.exit(result.returncode)


def cmd_archive(args):
    """Move notes to the archive folder."""
    notes_dir = get_notes_dir()
    notes_root = Path(notes_dir).resolve()
    archive_path = notes_root / ".archive"
    archive_path.mkdir(parents=True, exist_ok=True)

    for filepath in args.files:
        src = Path(filepath).resolve()

        if not src.is_file():
            print(f"Error: {filepath} is not a file.", file=sys.stderr)
            continue

        if notes_root not in src.parents:
            print(
                f"Error: {filepath} is not inside $PERSONAL_NOTES_DIR.",
                file=sys.stderr,
            )
            continue

        dest = archive_path / src.name
        if dest.exists():
            stem = src.stem
            suffix = src.suffix
            counter = 1
            while dest.exists():
                dest = archive_path / f"{stem}_{counter}{suffix}"
                counter += 1

        src.rename(dest)
        print(f"Archived: {filepath} -> {dest}")


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

    find_parser = subparsers.add_parser("find", help="Find notes based on filename")
    find_parser.add_argument(
        "query",
        nargs="*",
        help="Optional initial search query for fzf",
    )

    recent_parser = subparsers.add_parser(
        "recent",
        help=f"Find recently edited notes (default: {DEFAULT_RECENT_COUNT})",
    )
    recent_parser.add_argument(
        "--count",
        type=int,
        default=DEFAULT_RECENT_COUNT,
        help=f"Number of recent notes to show (default: {DEFAULT_RECENT_COUNT})",
    )

    archive_parser = subparsers.add_parser("archive", help="Archive notes")
    archive_parser.add_argument(
        "files",
        nargs="+",
        help="File paths of notes to archive",
    )

    subparsers.add_parser("sync", help="Sync notes via make sync")

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
    elif args.command == "find":
        cmd_find(args)
    elif args.command == "archive":
        cmd_archive(args)
    elif args.command == "sync":
        cmd_sync(args)


if __name__ == "__main__":
    main()

# note

[![Tests](https://github.com/jamessimas/note/actions/workflows/test.yml/badge.svg?branch=main)](https://github.com/jamessimas/note/actions/workflows/test.yml)

A single-file Python 3 CLI for managing personal notes. No dependencies beyond the standard library.

Notes are plain text files stored as `YYYY-MM-DD_slug_name.txt` under `$PERSONAL_NOTES_DIR/notes/<YYYY>/<new note>`.

Temp notes go to `$PERSONAL_NOTES_TEMP_DIR`.

## Setup

1. Set these environment variables:

```sh
export PERSONAL_NOTES_DIR="$HOME/personal-notes"  # root for permanent notes
export PERSONAL_NOTES_EDITOR="subl -a"            # editor command for editing notes
export PERSONAL_NOTES_TEMP_DIR="$HOME/Downloads"  # directory for temporary notes
```

2. Copy `note.py` to `$HOME/bin/note.py`.

## Usage

```sh
$ note.py
usage: note.py [-h] {new,temp,find,recent,archive,sync} ...

A simple CLI tool for creating notes.

positional arguments:
  {new,temp,find,recent,archive,sync}
    new                 Create a new note
    temp                Create a temporary note
    find                Find notes based on filename
    recent              Find recently edited notes (default: 5)
    archive             Archive notes
    sync                Sync notes via make sync

options:
  -h, --help            show this help message and exit
```

## Testing

Run unit tests:

```sh
make test
```

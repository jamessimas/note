# note

A single-file Python CLI for managing personal notes. No dependencies beyond the standard library.

## Setup

Set these environment variables:

```sh
export PERSONAL_NOTES_DIR="$HOME/personal-notes"  # root for permanent notes
export PERSONAL_NOTES_EDITOR="subl -a"            # editor command for editing notes
export PERSONAL_NOTES_TEMP_DIR="$HOME/Downloads"  # directory for temporary notes
```

## Usage

```sh
$ python3 note.py
usage: note.py [-h] {new,temp,find,recent,archive} ...

A simple CLI tool for creating notes.

positional arguments:
  {new,temp,find,recent,archive}
    new                 Create a new note
    temp                Create a temporary note
    find                Find notes based on filename
    recent              Find recently edited notes (default: 5)
    archive             Archive notes

options:
  -h, --help            show this help message and exit
```

## Testing

Run unit tests:

```sh
make test
```

## Notes format

Notes are plain text files stored as `YYYY-MM-DD_slug_name.txt` under `$PERSONAL_NOTES_DIR/notes/<YYYY>/`.

Temp notes go to `$PERSONAL_NOTES_TEMP_DIR/`.

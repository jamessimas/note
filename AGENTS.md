# AGENTS.md

Single-file Python CLI tool (`note.py`) with zero dependencies (stdlib only). No packaging, no CI.

## Running

```sh
python3 note.py new My Note Name    # create permanent note
python3 note.py temp [Optional Name] # create temp note (random slug if no name)
python3 note.py recent              # open most recently modified note
```

## Required environment variables

All three must be set or the tool exits with an error:

- `PERSONAL_NOTES_DIR` — root for permanent notes (stored under `notes/<YYYY>/`)
- `PERSONAL_NOTES_EDITOR` — editor command used to open files
- `PERSONAL_NOTES_TEMP_DIR` — directory for temporary notes

## Linting

Ruff with default config (no `ruff.toml` or `pyproject.toml`). Run manually:

```sh
ruff check note.py
ruff format note.py
```

## Testing

Tests use the stdlib `unittest` module (no extra dependencies). Run them with:

```sh
python3 -m unittest discover -s tests
```

## Conventions

- Note filenames: `YYYY-MM-DD_slug_name.txt`
- Commit messages: short imperative sentences (e.g., "Add recent command")

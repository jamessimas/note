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

3. Create Makefile

```makefile
# Get today's date and year dynamically
TODAY := $(shell date +%F)
YEAR  := $(shell date +%Y)

# Help
## ==============================
help: ## Show this help
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z0-9_-]+:.*?## / {sub("\\\\n",sprintf("\n%22c"," "), $$2);printf "\033[36m%-25s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST)

.PHONY: daily
daily: ## Create/open daily note
	@mkdir -p "daily/$(YEAR)"
	@subl daily/$(YEAR)/$(TODAY).md

.PHONY: sync
sync:
	@git pull --autostash
	@git add -u
	@git add .archive/ || true
	@git add logbooks/ notes/
	@git diff --cached --quiet || git commit -m "Update note(s)"
	@git push
	@echo "Done syncing."
```

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

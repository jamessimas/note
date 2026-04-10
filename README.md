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
python3 note.py new My Note Name         # create a permanent note
python3 note.py temp [Optional Name]     # create a temp note (random slug if no name)
python3 note.py recent                   # open most recently modified note
python3 note.py find [optional query]    # fuzzy-find and open notes (requires fzf + bat)
```

## Notes format

Notes are plain text files stored as `YYYY-MM-DD_slug_name.txt` under `$PERSONAL_NOTES_DIR/notes/<YYYY>/`.

Temp notes go to `$PERSONAL_NOTES_TEMP_DIR/`.

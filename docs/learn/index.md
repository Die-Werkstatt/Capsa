# The index

`src/capsa/index.py`

## What it does

The scanner tells Capsa what is on your drives right now. The index remembers it. It is one file, a **database**, that lives in Capsa's own folder and never inside your library.

Searching looks in the index, not on the drives. That is the difference between flipping through a contact sheet and opening every folder.

## What is inside

Three tables. Think of each as a spreadsheet.

| Table | One row is | Columns |
|---|---|---|
| `roots` | a library root | its path |
| `files` | a file the scanner found | which root, path inside the root, size, date, kind, missing or not |
| `files_search` | the same file, prepared for searching | the path, cut into words |

## Keeping it current

`index.update(root, files)` takes a fresh scan and compares it with what the index knows:

- A file that is new gets a row. Counted as **added**.
- A file whose size or date differs gets its row updated. Counted as **changed**.
- A file the index knows but the scan did not find is marked **missing**. Its row stays.
- Everything else is left alone.

Why mark instead of delete? If a drive is unplugged, the scan finds nothing on it. Deleting those rows would also throw away every tag you gave those assets. When the drive is back, the next scan clears the mark.

All changes of one update are written together, in one **transaction**: either all of them land or none. A crash halfway cannot leave half an update behind, like a render that writes to a temp file and renames it when the frame is complete.

## Searching

`index.search("chair exr")` returns the files whose path contains a word starting with `chair` **and** a word starting with `exr`, best match first.

The search table cuts every path into words wherever there is something that is not a letter or a digit. `chair/tex/chair_basecolor.exr` becomes `chair`, `tex`, `chair`, `basecolor`, `exr`. So `base` finds it, and `color` does not, because no word starts with `color`.

This is SQLite's full-text search, called FTS5. It works like the index at the back of a book: it looks up the word and gets the pages, without reading the book.

## How data flows

```
scan(root).files ──► index.update ──► files + files_search (in index.sqlite)
                                              │
"chair exr" ──────► index.search ◄────────────┘ ──► list of IndexedFile
```

## Safety

- `add_root` refuses a root that contains the index file itself. Capsa's data must not end up in your library.
- The index has a version number. If a later Capsa changes the tables, an old Capsa opening that file stops with a clear message.

## Try it

```sh
uv run python -c "from pathlib import Path; from capsa.scanner import scan; from capsa.index import Index; root = Path(r'D:\Assets'); index = Index(Path.home() / 'capsa-test.sqlite'); index.add_root(root); print(index.update(root, scan(root).files)); print([f.path.name for f in index.search('wood')][:10])"
```

Replace `D:\Assets` and `wood`. It writes `capsa-test.sqlite` into your user folder; delete it afterwards.

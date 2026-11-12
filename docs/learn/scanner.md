# The scanner

`src/capsa/scanner.py`

## What it does

You give it a folder, a **library root**. It walks through that folder and every folder inside it and writes down, for each file: where it is, how big it is, when it was last changed, and what kind of thing it is.

It is the File Pattern node of Capsa: it finds files and reports them. It does not open a single one.

## How it knows the kind

By the end of the file name. `chair.usd` ends in `.usd`, so it is USD. `smoke.0001.bgeo.sc` ends in `.bgeo.sc`, so it is a cache. The list of endings is the `SUFFIXES` table at the top of the file. Upper and lower case do not matter: `SKY.HDR` is an HDRI.

A name that matches nothing is `other`. It is still listed, so nothing in your library is invisible.

One gap: an `.exr` can be a texture or an HDRI, and the name does not say which. The scanner calls every `.exr` a texture; the grouping into assets decides later ([assets.md](assets.md)).

## What comes back

`scan(root)` returns a `Scan` with two lists:

- `files`: one `FileRecord` per file, with `path`, `size_bytes`, `modified_time` and `kind`.
- `unreadable`: every folder or file the scanner could not look at, such as a drive that is unplugged or a link that points to a deleted file.

A problem with one folder never stops the scan. The folder goes on the `unreadable` list and the scan carries on, like a render that skips a missing texture and reports it.

## How data flows

```
library root ──► os.walk (folder by folder) ──► name, size, date ──► FileRecord ──► Scan.files
                        │
                        └─ could not read ──► Scan.unreadable
```

## Why it cannot change your files

The scanner only asks the file system two questions: "what is in this folder?" and "how big and how old is this file?". A test, `test_scanner_calls_nothing_that_writes`, reads the scanner's own code and fails if it ever calls anything else. A second test scans a folder and checks that every file has the same size and date afterwards.

## Try it

```sh
uv run python -c "from pathlib import Path; from capsa.scanner import scan; s = scan(Path(r'D:\Assets')); print(len(s.files), 'files', len(s.unreadable), 'unreadable')"
```

Replace `D:\Assets` with one of your asset folders.

# The index

`src/capsa/index.py`

## What it does

The scanner tells Capsa what is on your drives right now. The index remembers it. It is one file, a **database**, that lives in Capsa's own folder and never inside your library.

Searching looks in the index, not on the drives. That is the difference between flipping through a contact sheet and opening every folder.

## What is inside

Six tables. Think of each as a spreadsheet.

| Table | One row is | Columns |
|---|---|---|
| `roots` | a library root | its path |
| `assets` | an asset, as `assets.py` grouped it | which root, path, name, kind, cover, missing or not |
| `files` | a file that belongs to an asset | which asset, path, size, date, kind |
| `assets_search` | the same asset, prepared for searching | its path and its tags, cut into words |
| `favourites` | an asset you starred | which root, path |
| `tags` | one tag on one asset | which root, path, tag |

Paths are stored relative to the root, so `materials/metal/metal_053B`, not `D:\Work\Library\materials\...`.

## Keeping it current

`index.update(root, assets)` takes the assets of a fresh scan and compares them with what the index knows:

- An asset that is new gets a row. Counted as **added**.
- An asset whose files differ (one more, one fewer, another size or date) gets its files replaced. Counted as **changed**.
- An asset the index knows but the scan did not find is marked **missing**. Its row stays.
- Unless its files are still there and now belong to another asset: a folder that became a material, frames that became a sequence. Then the old row is deleted. Counted as **regrouped**.
- Everything else is left alone.

Why mark instead of delete? If a drive is unplugged, the scan finds nothing on it. Deleting those rows would also throw away every tag you gave those assets. When the drive is back, the next scan clears the mark. A regrouped asset is different: its files are on the drive, so nothing would ever clear its mark.

All changes of one update are written together, in one **transaction**: either all of them land or none. A crash halfway cannot leave half an update behind, like a render that writes to a temp file and renames it when the frame is complete.

## Searching

`index.search("metal 053")` returns the assets whose path contains a word starting with `metal` **and** a word starting with `053`, best match first. Each result carries its name, kind, cover, total size and the date of its newest file.

The search table cuts every path into words wherever there is something that is not a letter or a digit. `materials/metal/metal_053B` becomes `materials`, `metal`, `metal`, `053B`. So `mat` finds it, and so does the folder it sits in. `roughness` does not: search looks at assets, not at the files inside them.

This is SQLite's full-text search, called FTS5. It works like the index at the back of a book: it looks up the word and gets the pages, without reading the book.

## Favourites and tags

`set_favourite(path, True)` stars an asset, `add_tag(path, "wood")` and `remove_tag(path, "wood")` tag it. Tags are stored in lower case with single spaces, so `Dining  Room` becomes `dining room`.

These are the only things in the index you make by hand: a rescan can build everything else again, but not them. So `favourites` and `tags` are not tied to an asset's row. They name the root and the path. When a rescan forgets an asset, its star and tags stay, and they are back as soon as an asset with that path is.

A tag is also written into `assets_search` beside the path, so `search("wood")` finds assets tagged wood.

## How data flows

```
scan(root).files ──► group ──► index.update ──► assets + files + assets_search
                                                        │
"metal 053" ──────────────► index.search ◄──────────────┘ ──► list of IndexedAsset
```

## Safety

- `add_root` refuses a root that contains the index file itself. Capsa's data must not end up in your library.
- The index has a version number, now 3. A file of version 2 is upgraded when Capsa opens it: the two new tables are added and the search table is built again, because an FTS5 table cannot gain a column. Nothing is rescanned. Capsa refuses a file of any other version with a clear message.

## Try it

```sh
uv run python -c "from pathlib import Path; from capsa.scanner import scan; from capsa.assets import group; from capsa.index import Index; root = Path(r'D:\Work\Library'); index = Index(Path.home() / 'capsa-test.sqlite'); index.add_root(root); print(index.update(root, group(scan(root).files))); print([a.name for a in index.search('metal')][:10])"
```

It writes `capsa-test.sqlite` into your user folder; delete it afterwards. If you ran the earlier version of this command, delete the old file first.

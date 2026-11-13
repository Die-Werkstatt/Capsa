# Running Capsa on your library

`src/capsa/library.py`, `src/capsa/__main__.py`

## What it does

`library.py` runs the other parts in order. `__main__.py` lets you start that from a terminal. There is no window yet.

## Three commands

```sh
uv run capsa add D:\Work\Library
uv run capsa scan
uv run capsa search metal 053
```

- `add` remembers a folder as a library root. It reads nothing yet.
- `scan` walks every root, groups the files into assets, updates the index and makes a thumbnail of every cover. It prints how many assets are new, changed, missing or regrouped.
- `search` prints the assets whose path matches every word: kind, name, path.

Run `scan` twice. The second run reports `0 added, 0 changed` and is fast, because every thumbnail is already there.

## Where Capsa writes

Everything goes into one **data folder**, never into your library:

| | |
|---|---|
| Windows | `%LOCALAPPDATA%\Capsa`, usually `C:\Users\<you>\AppData\Local\Capsa` |
| Linux | `~/.local/share/capsa` |

Inside are `index.sqlite` and the `thumbnails` folder. Delete the folder and Capsa starts from nothing; your library is not affected.

## What `refresh` does for one root

```
scan(root) ──► group ──► index.update ──► make_thumbnail for every cover
```

It returns one result per root with the numbers `scan` prints. The window will call the same function.

## What to know

- The first `scan` makes every thumbnail. An 8k HDRI takes one to two seconds, and nothing is printed until a root is done.
- `covers unreadable` counts covers OpenImageIO could not open. The log line above it names each file.
- A root on an unplugged drive is scanned as empty: its assets are marked missing and come back with the next scan.

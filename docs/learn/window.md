# The window

`src/capsa/window.py`, `src/capsa/web/`

## What it does

`uv run capsa` with no command opens Capsa's window, the **catalogue**. It has a title bar with the search box and three columns:

- **Sidebar:** groups of assets with their counts. Library holds All, Models, Materials, Textures (sequences included), HDRIs and Caches. Needs attention holds Missing files, shown only when an asset is missing.
- **Grid:** the assets of the chosen group as tiles with thumbnail, name and kind. Above it: a slider for the tile size, a button that switches to a list (one row per asset, with its size) and back, and the sort order. Recent puts the newest file first, Name sorts by name with numbers in number order (`metal_2` before `metal_10`), Size puts the largest first.
- **Details:** the selected asset: preview, name with its star, type, size, date and path, its tags, then Copy path and Show in Explorer.

The gear in the title bar opens **Settings**, a sheet from the right. It lists the library folders with their asset counts. Add folder opens the system's folder dialog, adds the folder and scans. Rescan all scans every folder, as `uv run capsa scan` does. While a scan runs, a blue line travels along the bottom of the title bar. `Esc` closes the sheet.

Typing in the search box narrows the grid and the counts. `Ctrl K` jumps to the search box. Clicking a tile selects it; the selection is the blue bar above it. The star on a tile (shown on hover) or `F` adds the asset to Favourites. `+ tag` or `T` adds a tag; clicking a tag removes it. A missing asset shows its name in orange.

## Two halves

The window is a small web page shown by Windows' own browser engine, WebView2, the one Edge uses. **pywebview** puts that page into a window and connects it to Python.

| Half | Files | Job |
|---|---|---|
| Python | `window.py` | Opens the window. `Api` answers the page's questions. |
| Page | `web/index.html`, `style.css`, `app.js` | Draws the title bar, sidebar, grid and details. Asks `Api` for data. |

## The bridge

In `app.js`:

```js
const assets = await window.pywebview.api.search("metal");
```

That line runs `Api.search("metal")` in Python and waits for the answer: a list of plain values (name, kind, path, cover, size, modified, missing). pywebview turns the Python list into a JavaScript array.

These calls do not go over the network. pywebview does start a small web server on `127.0.0.1` to hand WebView2 the three page files; Capsa has no server of its own. The page cannot reach anything `Api` does not offer.

`Api` has twelve methods: `search`, `thumbnail`, `show_in_explorer`, `set_favourite`, `add_tag`, `remove_tag`, `folders`, `add_folder`, `rescan`, `minimize`, `toggle_maximize` and `close`.

pywebview runs every call in a thread of its own. A scan can take a while, and the window stays usable meanwhile: the page only waits for the answer of `rescan` to hide the scan line and fetch the assets again. Thumbnails that are still loading wait until the scan ends: both make thumbnails, and two threads writing the same file at once would clash. A lock (`threading.Lock`) lets one in at a time.

The sidebar needs no method of its own. `search("")` already gives every asset with its kind, and `app.js` sorts them into groups and counts them.

## Copy path and Show in Explorer

Copy path runs in the page: `navigator.clipboard.writeText(path)`, the browser's own clipboard call.

Show in Explorer asks Python, because a page cannot start programs. On Windows `show_in_explorer` runs `explorer /select,"<path>"`, which opens the folder with the file selected. On Linux it opens the folder with `xdg-open`. A sequence selects its first frame, since `name_####.jpg` is not a real file. The button is off for a missing asset.

## Thumbnails

The page draws the tiles first, then asks for one thumbnail after the other with `window.pywebview.api.thumbnail(cover)`. Python makes the thumbnail if the cache does not have it yet, and sends it back as a **data URL**: the JPEG written out as text. The grid appears at once and fills in.

## The title bar

The window is **frameless**: Windows draws no title bar, Capsa draws its own. Dragging the empty part of the bar moves the window. That part is a `div` with the class `pywebview-drag-region`, which pywebview watches for. It lies behind the search box and buttons, so clicking those does not move the window.

## What it does not do yet

- The scan line shows that a scan runs, not how far it is.
- Sort, tile size and list or grid are forgotten when the window closes.
- No collections.
- The font is a placeholder: IBM Plex if installed, otherwise Segoe UI (#12).
- Maximise is tracked by the button alone: double-clicking the title bar or snapping the window does not update it.

# The window

`src/capsa/window.py`, `src/capsa/web/`

## What it does

`uv run capsa` with no command opens Capsa's window: a title bar with the search box, and every asset in the index as a tile with its thumbnail, name and kind.

Typing in the search box narrows the grid. `Ctrl K` jumps to the search box. A missing asset shows its name in orange.

## Two halves

The window is a small web page shown by Windows' own browser engine, WebView2, the one Edge uses. **pywebview** puts that page into a window and connects it to Python.

| Half | Files | Job |
|---|---|---|
| Python | `window.py` | Opens the window. `Api` answers the page's questions. |
| Page | `web/index.html`, `style.css`, `app.js` | Draws the title bar and the grid. Asks `Api` for data. |

## The bridge

In `app.js`:

```js
const assets = await window.pywebview.api.search("metal");
```

That line runs `Api.search("metal")` in Python and waits for the answer: a list of plain values (name, kind, path, cover, missing). pywebview turns the Python list into a JavaScript array.

There is no web server of Capsa's own and no network port. The page cannot reach anything `Api` does not offer.

`Api` has five methods: `search`, `thumbnail`, `minimize`, `toggle_maximize` and `close`.

## Thumbnails

The page draws the tiles first, then asks for one thumbnail after the other with `window.pywebview.api.thumbnail(cover)`. Python makes the thumbnail if the cache does not have it yet, and sends it back as a **data URL**: the JPEG written out as text. The grid appears at once and fills in.

## The title bar

The window is **frameless**: Windows draws no title bar, Capsa draws its own. Dragging the empty part of the bar moves the window. That part is a `div` with the class `pywebview-drag-region`, which pywebview watches for. It lies behind the search box and buttons, so clicking those does not move the window.

## What it does not do yet

- No sidebar, no details panel, no scanning from the window. Scan with `uv run capsa scan` and reopen the window.
- The font is a placeholder: IBM Plex if installed, otherwise Segoe UI (#12).
- Maximise is tracked by the button alone. Unverified on Windows: whether `restore()` takes a maximised window back to its size.

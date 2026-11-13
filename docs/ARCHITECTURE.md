# Architecture

Draft. The scanner, asset detection, the index and thumbnails exist (`scanner.py`, `assets.py`, `index.py`, `thumbnails.py` in `src/capsa/`); the index stores the assets. `library.py` runs them in order and the `capsa` command (`__main__.py`) starts it. `window.py` and `web/` show the index in a window. The other parts are the plan for phase 1.

```
Library roots (read only)          Capsa's data folder
  models, USD, textures, HDRIs       index (SQLite), settings, thumbnail cache
        │                                    ▲
        ▼                                    │
   scanner ──► asset detection ──► index ──► bridge ──► window
                                     ▲
                                thumbnails
```

- **Scanner:** walks the library roots and lists files with size, date and type.
- **Asset detection:** groups files into assets, such as a model with its texture folder.
- **Index:** one SQLite file holding files, assets, tags and collections, with full-text search.
- **Thumbnails:** 512 px JPEG previews of images, made with OpenImageIO, kept in the cache.
- **Data folder:** `%LOCALAPPDATA%\Capsa` on Windows, `$XDG_DATA_HOME/capsa` (default `~/.local/share/capsa`) on Linux. Holds `index.sqlite` and `thumbnails/`.
- **Bridge:** pywebview passes calls from the page's JavaScript to `window.Api` in Python. No web server of Capsa's own.
- **Window:** frameless, plain HTML, CSS and JavaScript in `src/capsa/web/`. So far the title bar, search and the grid of the three views in `docs/design/`.

Capsa reads library roots and writes only to its own data folder.
It never uses a Houdini licence and contains no SideFX code.

# Architecture

Draft. The scanner, asset detection and the index exist (`scanner.py`, `assets.py`, `index.py` in `src/capsa/`); the index stores the assets. The other parts are the plan for phase 1.

```
Library roots (read only)          Capsa's data folder
  models, USD, textures, HDRIs       index (SQLite), settings, thumbnail cache
        │                                    ▲
        ▼                                    │
   scanner ──► asset detection ──► index ──► local server ──► interface
                                     ▲
                                thumbnails
```

- **Scanner:** walks the library roots and lists files with size, date and type.
- **Asset detection:** groups files into assets, such as a model with its texture folder.
- **Index:** one SQLite file holding files, assets, tags and collections, with full-text search.
- **Thumbnails:** small previews made with OpenImageIO, kept in the cache.
- **Local server:** answers the interface's questions from the index.
- **Interface:** the three views in `docs/design/`.

Capsa reads library roots and writes only to its own data folder.
It never uses a Houdini licence and contains no SideFX code.

# Decisions

One entry per non-obvious choice. Newest at the bottom.

```
## YYYY-MM-DD: Title
**Decision:** what we chose
**Why:** reason in plain language
**Alternatives:** what else was possible and why not
**Trade-off:** what we give up
```

## 2026-11-11: Interface layout
**Decision:** Three views (Catalogue, Search, Inspector) in one frameless window, with settings as a side sheet. Spec and clickable prototype in [`docs/design/`](design/README.md).
**Why:** Browsing, finding and inspecting are the three jobs in phases 1 and 2. Keeping them in one window with one selection colour keeps it calm.
**Alternatives:** A pro-tool layout with docked panels and a shortcut bar. Rejected as too busy for a personal library. Shortcuts went into the right-click menu instead.
**Trade-off:** Less on screen at once. Detail like paths of missing files goes to the log, not the window.

## 2026-11-12: Python 3.13, managed with uv
**Decision:** Capsa's core is a Python 3.13 package in `src/capsa/`. uv installs Python and the dependencies and keeps their exact versions in `uv.lock`.
**Why:** The libraries the brief names have Windows wheels for 3.13: usd-core 26.11 supports 3.11 to 3.14, OpenImageIO 3.2.2 supports 3.9 to 3.15 (PyPI, checked 2026-11-11). Python is also Houdini's scripting language. uv is one program for what otherwise takes three (a Python installer, venv, pip), and the same two commands work on Windows and Linux.
**Alternatives:** pip with `requirements.txt`, as in Kompass: no lockfile, and a virtual environment to manage by hand. Python 3.11, to match Houdini 20.5 and 21.0: not needed, a Houdini panel runs in Houdini's own Python and talks to Capsa from outside.
**Trade-off:** uv has to be installed once on every machine.

## 2026-11-12: The roadmap lives in `agent_docs/ROADMAP.md`
**Decision:** One roadmap, at the path the project template and `.claude/suite.json` use.
**Why:** The brief asked for it in `docs/`. Two roadmaps would drift apart.
**Alternatives:** `docs/ROADMAP.md` as in Laterna, with the template's file pointing to it.
**Trade-off:** Capsa and Laterna differ here.

## 2026-11-12: The window is a pywebview window
**Decision:** Capsa opens in its own frameless pywebview window, never as a browser app. The interface inside the window is a web page.
**Why:** The interface spec asks for one frameless window with its own title bar, which a browser tab cannot be. pywebview is one Python package: `frameless=True`, a drag region, and `minimize()` and `maximize()` (https://pywebview.flowrl.com/api/). On Windows it draws the page with Edge WebView2. Chosen by Sandro (2026-11-12, #7).
**Alternatives:** A browser tab only, as in Laterna: no title bar of its own. Tauri with the Python backend as a sidecar: also WebView2 on Windows, so a 3D preview renders the same, but it adds Rust, the C++ Build Tools and a PyInstaller build.
**Trade-off:** No installer comes with it. On Linux pywebview needs Qt or GTK, untested. A preview that matches Karma would need Hydra, which neither option provides.

## 2026-11-12: The scanner reads names, sizes and dates only
**Decision:** A scan lists every file under a library root with its size, modified time and a kind taken from the file name. It opens no file. An `.exr` counts as a texture and an `.hdr` as an HDRI.
**Why:** Names, sizes and dates come from the folder listing, which is fast and cannot damage a file. Telling an HDRI from a texture needs the image's size or its folder, which belongs to asset detection (#15).
**Alternatives:** Open each file during the scan to read its contents: slow on a large library, and one broken file could stop the scan.
**Trade-off:** HDRIs saved as `.exr` show up as textures until asset detection exists.

## 2026-11-12: One central index in SQLite
**Decision:** Everything Capsa knows is in one SQLite file in Capsa's own data folder. Search uses SQLite's FTS5. A file that disappears is marked missing, not removed.
**Why:** The brief forbids writing into library roots, which rules out sidecar files beside assets. SQLite is one file, needs no server and comes with Python, FTS5 included (CPython's Windows build sets `SQLITE_ENABLE_FTS5`; not yet run on Sandro's machine, #11). Marking keeps tags when a drive is unplugged.
**Alternatives:** Sidecar files next to each asset: they travel with the asset, but write into the library. A JSON file: simple, but every search would read all of it.
**Trade-off:** Tags live only in the index. Move an asset folder to another machine and its tags stay behind. Missing rows pile up until something cleans them, which nothing does yet.

## 2026-11-12: What the checks on Sandro's machine showed
**Decision:** Build for the library as it is: 516 files, 9.93 GB, one root on a fixed disk, mostly ambientCG materials and HDRIs. No Component Builder assets, no `.tx`, no Houdini-written USD. Full results: issue #11.
**Why:** usd-core 26.11, OpenImageIO 3.2.2.0 and FTS5 all work on Windows 11 (Python 3.14.5). A walk of the whole library takes 0.02 s. A 256 px thumbnail of an 8k `.exr` or `.hdr` takes 1.4 to 1.9 s. OpenImageIO cannot read `.rat`. A Houdini 21 Component Builder asset names its thumbnail in `assetInfo` (`previews.thumbnails.default.defaultImage`, here `./thumbnail.png`).
**Alternatives:** Build Component Builder detection first, as the interface spec proposes: nothing in the library would use it.
**Trade-off:** Rules fitted to one library. A different folder layout needs new rules.

## 2026-11-12: A texture-set folder is one asset
**Decision:** A folder holding two or more different texture maps is one material, named after the folder, with everything directly in it. Every other file is its own asset. A `.rat` copy joins the file it was made from. A lone `.exr` counts as an HDRI.
**Why:** It matches the library: a material is a folder of maps (`metal_053B/`), an HDRI is one file with an optional `.rat` beside it. No file is written into the library.
**Alternatives:** Every file an asset: 450 material files as 450 tiles. Every lowest folder an asset: `hdri/exterior/4k` would be one tile holding all its HDRIs. A sidecar file per asset: writes into the library.
**Trade-off:** Two sets in one folder merge into one material. Resolutions of one material in sibling folders show as separate materials. An `.exr` that is not an HDRI is mislabelled until the image's proportions are read.

## 2026-11-12: The index stores assets
**Decision:** The index keeps one row per asset and the asset's files beneath it. Search returns assets and looks at their paths, not at the names of the files inside. The schema version is 2; an index of version 1 is refused, not converted.
**Why:** The catalogue shows assets, and tags and favourites will belong to an asset. Searching file names would answer "roughness" with every material in the library.
**Alternatives:** Keep files as the unit and group them on every search: the grouping would run for each keystroke. Convert version 1 files: the only one in existence is a test file.
**Trade-off:** A map cannot be found by its own file name. If a folder turns into a material because maps were added, its former single assets go missing and a new asset appears.


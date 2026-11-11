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
**Trade-off:** uv has to be installed once on every machine. The window and the web stack are still open (#7).

## 2026-11-12: The roadmap lives in `agent_docs/ROADMAP.md`
**Decision:** One roadmap, at the path the project template and `.claude/suite.json` use.
**Why:** The brief asked for it in `docs/`. Two roadmaps would drift apart.
**Alternatives:** `docs/ROADMAP.md` as in Laterna, with the template's file pointing to it.
**Trade-off:** Capsa and Laterna differ here.

# Decisions

## 2026-11-11 — Interface layout
**Decision:** Three views (Catalogue, Search, Inspector) in one frameless window, with settings as a side sheet. Spec and clickable prototype in [`docs/design/`](design/README.md).
**Why:** Browsing, finding and inspecting are the three jobs in phases 1 and 2. Keeping them in one window with one selection colour keeps it calm.
**Alternatives:** A pro-tool layout with docked panels and a shortcut bar. Rejected as too busy for a personal library. Shortcuts went into the right-click menu instead.
**Trade-off:** Less on screen at once. Detail like paths of missing files goes to the log, not the window.

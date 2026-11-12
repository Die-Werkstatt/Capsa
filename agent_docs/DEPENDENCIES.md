# Capsa: dependency policy and inventory

A decision record, not a lockfile mirror. Every direct dependency gets one line
saying why it is here. Removed or rejected candidates go under "Removed" with
the reason, so the same discussion does not happen twice.

## Policy

- Prefer the standard library, then what is already in the tree.
- A new dependency needs a reason a reviewer can check: what it does that the
  tree cannot reasonably do itself, and what it gets access to.
- Dependabot opens update PRs weekly (`.github/dependabot.yml`).

## Current inventory

| Dependency | Kind | Why |
|---|---|---|
| pytest | dev | Runs the unit tests. |
| ruff | dev | Lint and format. Pinned to 0.16.7, the version aislop 0.16.0 runs. |
| uv_build | build | Builds the `capsa` package from `src/`; uv's own backend. |
| three.js r128 (cdnjs) | website, prototype | The 3D box on `docs/website` and the material sphere in `docs/design/prototype.html`. Loaded at runtime. |
| Google Fonts | website, prototype | Michroma, IBM Plex and JetBrains Mono, loaded at runtime. Placeholders until the font is chosen (#12). |

## Removed

| Dependency | Removed in | Why |
|---|---|---|

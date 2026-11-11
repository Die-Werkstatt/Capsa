# Conventions

## General

- Clear names over short names: `modified_time`, not `mt`.
- One module does one job. If one sentence cannot describe it, split it.
- Comments say why, not what. Long explanations go in `docs/learn/`.
- Capsa never writes into a library root.
- Runs on Windows and Linux. Paths go through `pathlib`; tests must not depend on one system.

## Python

- Python 3.13. The code lives in `src/capsa/`, the tests in `tests/`.
- uv manages the environment. `uv add <package>` adds a dependency and updates `uv.lock`; the lockfile is never edited by hand.
- Style: PEP 8, formatted by `ruff format`. `snake_case` for functions and variables, `PascalCase` for classes.
- Type hints on function signatures.
- Tests with pytest, using real files from `tests/fixtures/` where a file format is involved.

## Licences

- Capsa contains no SideFX code and never converts Houdini files.
- Keep the licence notices of every open-source library Capsa uses. They must ship with Capsa if it is ever shared.

## Git

- One pull request per piece of work. See `CONTRIBUTING.md`.

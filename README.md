# Capsa

Asset library for VFX/3D. A personal tool for a Houdini/Solaris workflow: it
indexes the asset folders you already have, without moving or changing
anything, and finds assets fast.

In development: Capsa scans a folder, groups the files into assets, makes
thumbnails and shows them in a window you can search. The plan is in
[`docs/BRIEF.md`](docs/BRIEF.md), the order of work in
[`agent_docs/ROADMAP.md`](agent_docs/ROADMAP.md).

## Try it

Needs [uv](https://docs.astral.sh/uv/getting-started/installation/).

```sh
uv run capsa add <folder>
uv run capsa scan
uv run capsa search <words>
uv run capsa
```

The last one opens the window.

## Run the tests

```sh
uv run pytest -q
```

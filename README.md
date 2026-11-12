# Capsa

Asset library for VFX/3D. A personal tool for a Houdini/Solaris workflow: it
indexes the asset folders you already have, without moving or changing
anything, and finds assets fast.

In development: Capsa scans a folder, groups the files into assets, makes
thumbnails and searches the assets by name, from a terminal. There is no
window yet. The plan is in
[`docs/BRIEF.md`](docs/BRIEF.md), the order of work in
[`agent_docs/ROADMAP.md`](agent_docs/ROADMAP.md).

## Try it

Needs [uv](https://docs.astral.sh/uv/getting-started/installation/).

```sh
uv run capsa add <folder>
uv run capsa scan
uv run capsa search <words>
```

## Run the tests

```sh
uv run pytest -q
```

# Assets

`src/capsa/assets.py`

## What it does

The scanner returns files. You do not think in files: `metal_053B` is one material to you, not twelve PNGs. `group(files)` takes the scanner's list and returns **assets**, the things the catalogue shows as one tile.

It is like the difference between a folder of frames and one image sequence: same files, counted the way you would count them.

## The rules

Capsa looks at one folder at a time.

**1. A folder with a texture set is one material.**
A texture set is two or more different maps side by side. Capsa recognises a map by a word in its file name: `Color`, `Roughness`, `NormalGL`, `Displacement`, `diff`, `rough`, `nor` and so on. The full list is `MAP_WORDS` at the top of the file.

If a folder has a set, everything directly in that folder belongs to the material: the maps, the `.usdc`, the `.mtlx`, the `.rat` copies. The material is named after the folder.

**2. Any other file is its own asset.**
An HDRI, a model, a logo. It is named after the file.

**3. A `.rat` copy joins its source.**
Houdini writes `goegap_4k.exr.rat` beside `goegap_4k.exr`. That is the same picture twice, so both are one asset. A `.rat` whose source is gone stands alone.

## The cover

Every asset can have a **cover**, the picture shown on its tile.

- Material: the picture in the folder that is not a map, such as the `Metal053B.png` preview that ambientCG ships. If there is none, the colour map.
- A texture or HDRI: the file itself.
- A model, or a lone `.rat`: none yet.

## An assumption to know about

A lone `.exr` is taken for an HDRI. That is true for your library today, where every `.exr` outside a material is one. A render saved as `.exr` would be mislabelled. The reliable test is the picture's shape (an HDRI is twice as wide as it is high), which needs the file opened. That comes with thumbnails.

## What it does not do yet

- Two texture sets in one folder become one material.
- `metalPlates_08_4K` and `metalPlates_08_2K` are two materials, not two resolutions of one.
- The assets are not stored in the index. `group` runs on a scan and returns a list.

## Try it

```sh
uv run python -c "from pathlib import Path; from collections import Counter; from capsa.scanner import scan; from capsa.assets import group; assets = group(scan(Path(r'D:\Work\Library')).files); print(len(assets), 'assets'); print(Counter(a.kind.value for a in assets))"
```

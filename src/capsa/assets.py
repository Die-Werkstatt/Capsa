"""Turn a list of files into a list of assets: what the catalogue shows as one tile."""

import re
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path

from capsa.scanner import FileRecord, Kind

# Words in a texture's file name that say which map it is.
COLOR_WORDS = {"color", "basecolor", "albedo", "diffuse", "diff", "col"}
MAP_WORDS = COLOR_WORDS | {
    "roughness",
    "rough",
    "metalness",
    "metallic",
    "normal",
    "normalgl",
    "normaldx",
    "nor",
    "displacement",
    "disp",
    "height",
    "ambientocclusion",
    "ao",
    "opacity",
    "emission",
    "specular",
}

# Houdini writes its own copy of a texture as "<file name>.rat" beside it.
COMPANION_SUFFIX = ".rat"


@dataclass(frozen=True)
class Asset:
    name: str
    kind: Kind
    path: Path  # the folder of a material, the file of anything else
    cover: Path | None  # the image to show for it, if one is on disk
    files: tuple[FileRecord, ...]


def map_word(record: FileRecord) -> str | None:
    """Which map a texture is ("roughness"), or None if its name does not say."""
    if record.kind != Kind.TEXTURE or is_companion(record):
        return None
    for word in re.split(r"[^a-z0-9]+", record.path.stem.lower()):
        if word in MAP_WORDS:
            return word
    return None


def is_companion(record: FileRecord) -> bool:
    return record.path.name.lower().endswith(COMPANION_SUFFIX)


def group(files: list[FileRecord]) -> list[Asset]:
    by_folder: dict[Path, list[FileRecord]] = defaultdict(list)
    for record in files:
        by_folder[record.path.parent].append(record)

    assets: list[Asset] = []
    for folder in sorted(by_folder):
        records = by_folder[folder]
        # Two different maps side by side make a texture set: one material.
        if len({map_word(record) for record in records} - {None}) >= 2:
            assets.append(material(folder, records))
        else:
            assets.extend(single_files(records))
    return assets


def material(folder: Path, records: list[FileRecord]) -> Asset:
    images = [r for r in records if r.kind == Kind.TEXTURE and not is_companion(r)]
    # A picture that is no map is the preview the download came with.
    previews = [r for r in images if map_word(r) is None]
    colors = [r for r in images if map_word(r) in COLOR_WORDS]
    candidates = previews or colors
    cover = candidates[0].path if candidates else None
    return Asset(folder.name, Kind.MATERIAL, folder, cover, tuple(records))


def single_files(records: list[FileRecord]) -> list[Asset]:
    by_name = {record.path.name: record for record in records}
    companions: dict[str, list[FileRecord]] = defaultdict(list)
    for record in records:
        source = record.path.name[: -len(COMPANION_SUFFIX)]
        if is_companion(record) and source in by_name:
            companions[source].append(record)
            del by_name[record.path.name]

    assets = []
    for name, record in by_name.items():
        # An .exr on its own is taken for an HDRI; inside a material it is a map.
        kind = Kind.HDRI if record.path.suffix.lower() == ".exr" else record.kind
        shows_itself = kind in (Kind.TEXTURE, Kind.HDRI) and not is_companion(record)
        assets.append(
            Asset(
                record.path.stem,
                kind,
                record.path,
                record.path if shows_itself else None,
                (record, *companions[name]),
            )
        )
    return assets

"""Walk a library root and list its files. Reads names, sizes and dates; opens nothing."""

import os
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path


class Kind(Enum):
    USD = "usd"
    ALEMBIC = "alembic"
    FBX = "fbx"
    OBJ = "obj"
    TEXTURE = "texture"
    HDRI = "hdri"
    MATERIAL = "material"
    CACHE = "cache"
    HDA = "hda"
    OTHER = "other"


# Matched against the end of the lower-case file name, so ".bgeo.sc" works.
# An .exr counts as a texture: nothing in its name says whether it is an HDRI.
SUFFIXES: dict[str, Kind] = {
    ".usd": Kind.USD,
    ".usda": Kind.USD,
    ".usdc": Kind.USD,
    ".usdz": Kind.USD,
    ".abc": Kind.ALEMBIC,
    ".fbx": Kind.FBX,
    ".obj": Kind.OBJ,
    ".exr": Kind.TEXTURE,
    ".tx": Kind.TEXTURE,
    ".png": Kind.TEXTURE,
    ".jpg": Kind.TEXTURE,
    ".jpeg": Kind.TEXTURE,
    ".tif": Kind.TEXTURE,
    ".tiff": Kind.TEXTURE,
    ".rat": Kind.TEXTURE,
    ".hdr": Kind.HDRI,
    ".mtlx": Kind.MATERIAL,
    ".bgeo": Kind.CACHE,
    ".bgeo.sc": Kind.CACHE,
    ".vdb": Kind.CACHE,
    ".hda": Kind.HDA,
    ".hdalc": Kind.HDA,
    ".hdanc": Kind.HDA,
    ".otl": Kind.HDA,
}


@dataclass(frozen=True)
class FileRecord:
    path: Path
    size_bytes: int
    modified_time: float  # seconds since 1970, as the file system reports it
    kind: Kind


@dataclass
class Scan:
    files: list[FileRecord] = field(default_factory=list)
    unreadable: list[Path] = field(default_factory=list)


def kind_of(name: str) -> Kind:
    lower = name.lower()
    for suffix, kind in SUFFIXES.items():
        if lower.endswith(suffix):
            return kind
    return Kind.OTHER


def scan(root: Path) -> Scan:
    result = Scan()

    def folder_failed(error: OSError) -> None:
        result.unreadable.append(Path(error.filename))

    # os.walk does not follow links to folders, so a link cannot loop the scan.
    for folder, _, names in os.walk(root, onerror=folder_failed):
        for name in sorted(names):
            path = Path(folder) / name
            try:
                info = path.stat()
            except OSError:
                result.unreadable.append(path)
                continue
            result.files.append(FileRecord(path, info.st_size, info.st_mtime, kind_of(name)))
    return result

"""Tie the parts together: scan the library roots, index the assets, make their thumbnails."""

import os
import sys
from dataclasses import dataclass
from pathlib import Path

from capsa.assets import group
from capsa.index import Changes, Index
from capsa.scanner import scan
from capsa.thumbnails import make_thumbnail

INDEX_NAME = "index.sqlite"
THUMBNAILS_NAME = "thumbnails"


def data_folder() -> Path:
    """The folder for everything Capsa writes, where the system keeps application data."""
    if sys.platform == "win32":
        return Path(os.environ["LOCALAPPDATA"]) / "Capsa"
    base = os.environ.get("XDG_DATA_HOME")
    return (Path(base) if base else Path.home() / ".local" / "share") / "capsa"


@dataclass(frozen=True)
class Refreshed:
    root: Path
    changes: Changes
    unreadable: int  # folders and files the scan could not look at
    thumbnails: int  # covers that have a thumbnail
    without_thumbnail: int  # covers OpenImageIO could not read


def refresh(index: Index, thumbnails: Path) -> list[Refreshed]:
    """Scan every root the index knows and bring index and thumbnails up to date."""
    results = []
    for root in index.roots():
        found = scan(root)
        assets = group(found.files)
        changes = index.update(root, assets)
        made = [make_thumbnail(asset.cover, thumbnails) for asset in assets if asset.cover]
        results.append(
            Refreshed(
                root,
                changes,
                len(found.unreadable),
                sum(1 for thumbnail in made if thumbnail),
                sum(1 for thumbnail in made if not thumbnail),
            )
        )
    return results

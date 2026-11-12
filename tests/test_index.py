import sqlite3
from pathlib import Path

import pytest

from capsa.assets import Asset, group
from capsa.index import Changes, Index
from capsa.scanner import Kind, scan


def found(root: Path) -> list[Asset]:
    return group(scan(root).files)


@pytest.fixture
def library(tmp_path: Path) -> Path:
    root = tmp_path / "library"
    metal = root / "materials" / "metal_053B"
    metal.mkdir(parents=True)
    (metal / "Metal053B.png").write_bytes(b"preview")
    (metal / "Metal053B_Color.png").write_bytes(b"12345")
    (metal / "Metal053B_Roughness.png").write_bytes(b"123")
    (root / "models").mkdir()
    (root / "models" / "chair.obj").write_bytes(b"obj")
    (root / "sky_sunset.hdr").write_bytes(b"")
    return root


@pytest.fixture
def index(tmp_path: Path, library: Path):
    index = Index(tmp_path / "index.sqlite")
    index.add_root(library)
    yield index
    index.close()


def names(index: Index, text: str) -> list[str]:
    return [asset.name for asset in index.search(text)]


def test_first_scan_adds_every_asset(index: Index, library: Path):
    assert index.update(library, found(library)) == Changes(added=3, changed=0, missing=0)


def test_same_scan_twice_changes_nothing(index: Index, library: Path):
    index.update(library, found(library))
    assert index.update(library, found(library)) == Changes(0, 0, 0)


def test_rescan_sees_changed_and_missing_assets(index: Index, library: Path):
    index.update(library, found(library))
    (library / "materials" / "metal_053B" / "Metal053B_Normal.png").write_bytes(b"new map")
    (library / "sky_sunset.hdr").unlink()
    assert index.update(library, found(library)) == Changes(added=0, changed=1, missing=1)
    (sky,) = index.search("sunset")
    assert sky.missing
    # Already marked: a third scan does not count it again.
    assert index.update(library, found(library)) == Changes(0, 0, 0)


def test_asset_that_comes_back_is_no_longer_missing(index: Index, library: Path):
    assets = found(library)
    index.update(library, assets)
    index.update(library, [])  # the drive was unplugged
    assert index.search("chair")[0].missing
    assert index.update(library, assets) == Changes(added=0, changed=3, missing=0)
    assert not index.search("chair")[0].missing


def test_search_matches_words_from_their_start(index: Index, library: Path):
    index.update(library, found(library))
    assert names(index, "sunset") == ["sky_sunset"]
    assert names(index, "053") == ["metal_053B"]
    assert names(index, "mat met") == ["metal_053B"]
    assert names(index, "models") == ["chair"]
    assert names(index, "table") == []
    assert names(index, "   ") == []


def test_search_finds_assets_not_their_files(index: Index, library: Path):
    index.update(library, found(library))
    assert names(index, "roughness") == []


def test_search_survives_search_syntax(index: Index, library: Path):
    index.update(library, found(library))
    assert names(index, 'sky" OR (') == []
    assert names(index, "sky AND") == []


def test_search_returns_the_whole_asset(index: Index, library: Path):
    index.update(library, found(library))
    (metal,) = index.search("metal")
    folder = library / "materials" / "metal_053B"
    assert metal.path == folder
    assert metal.kind == Kind.MATERIAL
    assert metal.cover == folder / "Metal053B.png"
    assert metal.size_bytes == len(b"preview") + 5 + 3
    assert metal.modified_time == max(file.stat().st_mtime for file in folder.iterdir())
    assert not metal.missing
    (chair,) = index.search("chair")
    assert chair.cover is None


def test_index_survives_closing(tmp_path: Path, library: Path):
    path = tmp_path / "index.sqlite"
    first = Index(path)
    first.add_root(library)
    first.update(library, found(library))
    first.close()
    second = Index(path)
    assert second.roots() == [library]
    assert names(second, "sunset") == ["sky_sunset"]
    second.close()


def test_index_inside_a_root_is_refused(library: Path):
    index = Index(library / "index.sqlite")
    with pytest.raises(ValueError, match="inside the library root"):
        index.add_root(library)
    index.close()
    (library / "index.sqlite").unlink()


def test_index_of_another_version_is_refused(tmp_path: Path):
    path = tmp_path / "index.sqlite"
    db = sqlite3.connect(path)
    db.execute("PRAGMA user_version = 99")
    db.close()
    with pytest.raises(RuntimeError, match="version 99"):
        Index(path)

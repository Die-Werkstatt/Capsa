import sqlite3
from pathlib import Path

import pytest

from capsa.index import Changes, Index
from capsa.scanner import Kind, scan


@pytest.fixture
def library(tmp_path: Path) -> Path:
    root = tmp_path / "library"
    (root / "chair" / "tex").mkdir(parents=True)
    (root / "chair" / "chair.usd").write_bytes(b"usd")
    (root / "chair" / "tex" / "chair_basecolor.exr").write_bytes(b"12345")
    (root / "sky_sunset.hdr").write_bytes(b"")
    return root


@pytest.fixture
def index(tmp_path: Path, library: Path):
    index = Index(tmp_path / "index.sqlite")
    index.add_root(library)
    yield index
    index.close()


def paths(index: Index, text: str) -> list[str]:
    return [found.path.name for found in index.search(text)]


def test_first_scan_adds_every_file(index: Index, library: Path):
    assert index.update(library, scan(library).files) == Changes(added=3, changed=0, missing=0)


def test_same_scan_twice_changes_nothing(index: Index, library: Path):
    index.update(library, scan(library).files)
    assert index.update(library, scan(library).files) == Changes(0, 0, 0)


def test_rescan_sees_changed_and_missing_files(index: Index, library: Path):
    index.update(library, scan(library).files)
    (library / "chair" / "chair.usd").write_bytes(b"a longer usd")
    (library / "sky_sunset.hdr").unlink()
    assert index.update(library, scan(library).files) == Changes(added=0, changed=1, missing=1)
    (sky,) = index.search("sunset")
    assert sky.missing
    # Already marked: a third scan does not count it again.
    assert index.update(library, scan(library).files) == Changes(0, 0, 0)


def test_file_that_comes_back_is_no_longer_missing(index: Index, library: Path):
    files = scan(library).files
    index.update(library, files)
    index.update(library, [])  # the drive was unplugged
    assert all(found.missing for found in index.search("chair"))
    assert index.update(library, files) == Changes(added=0, changed=3, missing=0)
    assert not any(found.missing for found in index.search("chair"))


def test_search_matches_words_from_their_start(index: Index, library: Path):
    index.update(library, scan(library).files)
    assert paths(index, "sunset") == ["sky_sunset.hdr"]
    assert paths(index, "base") == ["chair_basecolor.exr"]
    assert sorted(paths(index, "chair")) == ["chair.usd", "chair_basecolor.exr"]
    assert paths(index, "chair exr") == ["chair_basecolor.exr"]
    assert paths(index, "table") == []
    assert paths(index, "   ") == []


def test_search_survives_search_syntax(index: Index, library: Path):
    index.update(library, scan(library).files)
    assert paths(index, 'sky" OR (') == []
    assert paths(index, "sky AND") == []


def test_search_returns_the_full_record(index: Index, library: Path):
    index.update(library, scan(library).files)
    (found,) = index.search("basecolor")
    assert found.path == library / "chair" / "tex" / "chair_basecolor.exr"
    assert found.size_bytes == 5
    assert found.kind == Kind.TEXTURE
    assert not found.missing


def test_index_survives_closing(tmp_path: Path, library: Path):
    path = tmp_path / "index.sqlite"
    first = Index(path)
    first.add_root(library)
    first.update(library, scan(library).files)
    first.close()
    second = Index(path)
    assert second.roots() == [library]
    assert paths(second, "sunset") == ["sky_sunset.hdr"]
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

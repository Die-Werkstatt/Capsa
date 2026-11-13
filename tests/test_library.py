import sys
from pathlib import Path

import numpy as np
import OpenImageIO as oiio
import pytest

from capsa.__main__ import main
from capsa.index import Index
from capsa.library import data_folder, refresh


def write_image(path: Path) -> None:
    image = oiio.ImageBuf(oiio.ImageSpec(8, 4, 3, "float"))
    image.set_pixels(oiio.ROI(0, 8, 0, 4), np.full((4, 8, 3), 0.5, dtype=np.float32))
    assert image.write(str(path)), image.geterror()


@pytest.fixture
def data(tmp_path: Path, monkeypatch) -> Path:
    """Send Capsa's data folder into the test's own folder."""
    monkeypatch.setenv(
        "LOCALAPPDATA" if sys.platform == "win32" else "XDG_DATA_HOME", str(tmp_path)
    )
    return data_folder()


@pytest.fixture
def library(tmp_path: Path) -> Path:
    root = tmp_path / "library"
    (root / "hdri").mkdir(parents=True)
    write_image(root / "hdri" / "goegap_4k.exr")
    (root / "hdri" / "goegap_4k.exr.rat").write_bytes(b"")
    (root / "hdri" / "broken.hdr").write_bytes(b"not an image")
    (root / "chair.usd").write_bytes(b"")
    return root


def test_data_folder_is_the_systems(data, tmp_path):
    assert data == tmp_path / ("Capsa" if sys.platform == "win32" else "capsa")


def test_refresh_indexes_and_makes_thumbnails(library, tmp_path):
    index = Index(tmp_path / "index.sqlite")
    index.add_root(library)
    (result,) = refresh(index, tmp_path / "thumbnails")
    assert result.changes.added == 3
    assert (result.thumbnails, result.without_thumbnail) == (1, 1)
    assert len(list((tmp_path / "thumbnails").iterdir())) == 1
    assert refresh(index, tmp_path / "thumbnails")[0].changes.added == 0
    index.close()


def test_refresh_leaves_the_library_untouched(library, tmp_path):
    before = sorted((p, p.stat().st_mtime_ns) for p in library.rglob("*"))
    index = Index(tmp_path / "index.sqlite")
    index.add_root(library)
    refresh(index, tmp_path / "thumbnails")
    index.close()
    assert sorted((p, p.stat().st_mtime_ns) for p in library.rglob("*")) == before


def test_add_scan_search(library, data, capsys):
    main(["add", str(library)])
    main(["scan"])
    assert "3 added, 0 changed, 0 missing, 0 regrouped" in capsys.readouterr().out
    main(["search", "goegap"])
    found = capsys.readouterr().out
    assert found.startswith("hdri")
    assert "goegap_4k.exr" in found
    assert (data / "index.sqlite").exists()


def test_add_refuses_what_is_no_folder(library, data):
    with pytest.raises(SystemExit):
        main(["add", str(library / "chair.usd")])

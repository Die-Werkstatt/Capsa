import base64
import subprocess
import sys
from pathlib import Path

import numpy as np
import OpenImageIO as oiio

from capsa.index import Index
from capsa.library import INDEX_NAME, refresh
from capsa.window import PAGE, Api


def library_with_one_image(tmp_path: Path) -> Path:
    root = tmp_path / "library"
    root.mkdir()
    image = oiio.ImageBuf(oiio.ImageSpec(8, 4, 3, "float"))
    image.set_pixels(oiio.ROI(0, 8, 0, 4), np.full((4, 8, 3), 0.5, dtype=np.float32))
    assert image.write(str(root / "sky.exr")), image.geterror()
    (root / "chair.obj").write_bytes(b"")
    return root


def api_for(tmp_path: Path) -> Api:
    data = tmp_path / "data"
    data.mkdir()
    index = Index(data / INDEX_NAME)
    index.add_root(library_with_one_image(tmp_path))
    refresh(index, data / "thumbnails")
    index.close()
    return Api(data)


def test_search_gives_the_page_plain_values(tmp_path):
    chair, sky = api_for(tmp_path).search("")
    source = tmp_path / "library" / "chair.obj"
    assert chair == {
        "name": "chair",
        "kind": "obj",
        "path": str(source),
        "cover": None,
        "size": 0,
        "modified": source.stat().st_mtime,
        "missing": False,
    }
    assert sky["kind"] == "hdri"


def test_thumbnail_is_a_jpeg_data_url(tmp_path):
    api = api_for(tmp_path)
    (sky,) = api.search("sky")
    url = api.thumbnail(sky["cover"])
    prefix = "data:image/jpeg;base64,"
    assert url.startswith(prefix)
    assert base64.b64decode(url[len(prefix) :])[:2] == b"\xff\xd8"


def test_unreadable_cover_gives_no_thumbnail(tmp_path):
    junk = tmp_path / "junk.rat"
    junk.write_bytes(b"junk")
    assert api_for(tmp_path).thumbnail(str(junk)) is None


def test_page_files_ship_with_the_package():
    for name in ("index.html", "style.css", "app.js"):
        assert (PAGE.parent / name).is_file()


def test_explorer_on_windows_selects_the_file(tmp_path, monkeypatch):
    calls = []
    monkeypatch.setattr(sys, "platform", "win32")
    monkeypatch.setattr(subprocess, "Popen", calls.append)
    Api(tmp_path).show_in_explorer(r"D:\Work\Library\my sky.exr")
    # Quotes around the path only: Explorer ignores a quoted "/select,...".
    assert calls == [r'explorer /select,"D:\Work\Library\my sky.exr"']


def test_explorer_on_linux_opens_the_folder(tmp_path, monkeypatch):
    calls = []
    monkeypatch.setattr(sys, "platform", "linux")
    monkeypatch.setattr(subprocess, "Popen", calls.append)
    Api(tmp_path).show_in_explorer(str(tmp_path / "sky.exr"))
    assert calls == [["xdg-open", str(tmp_path)]]


class FolderDialog:
    """Stands in for the pywebview window: its folder dialog answers `chosen`."""

    def __init__(self, chosen: Path | None) -> None:
        self.chosen = chosen

    def create_file_dialog(self, dialog_type):
        return (str(self.chosen),) if self.chosen else None


def test_folders_count_the_assets_of_each_root(tmp_path):
    assert api_for(tmp_path).folders() == [{"path": str(tmp_path / "library"), "assets": 2}]


def test_added_folder_is_found_by_rescan(tmp_path):
    api = api_for(tmp_path)
    second = tmp_path / "second"
    second.mkdir()
    (second / "table.fbx").write_bytes(b"")
    api._window = FolderDialog(second)
    assert api.add_folder() == {"added": str(second)}
    api.rescan()
    assert [a["name"] for a in api.search("")] == ["chair", "sky", "table"]


def test_cancelled_dialog_adds_nothing(tmp_path):
    api = api_for(tmp_path)
    api._window = FolderDialog(None)
    assert api.add_folder() is None
    assert len(api.folders()) == 1


def test_folder_holding_the_index_is_refused(tmp_path):
    api = api_for(tmp_path)
    api._window = FolderDialog(tmp_path)
    assert "lies inside" in api.add_folder()["error"]

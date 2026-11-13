import base64
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
    assert chair == {
        "name": "chair",
        "kind": "obj",
        "path": str(tmp_path / "library" / "chair.obj"),
        "cover": None,
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

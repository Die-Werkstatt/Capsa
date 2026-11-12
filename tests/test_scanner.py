import ast
from pathlib import Path

import pytest

from capsa import scanner
from capsa.scanner import Kind, kind_of, scan


@pytest.fixture
def library(tmp_path: Path) -> Path:
    (tmp_path / "chair").mkdir()
    (tmp_path / "chair" / "chair.usd").write_bytes(b"usd")
    (tmp_path / "chair" / "tex").mkdir()
    (tmp_path / "chair" / "tex" / "chair_basecolor.exr").write_bytes(b"12345")
    (tmp_path / "sky.HDR").write_bytes(b"")
    (tmp_path / "notes.txt").write_bytes(b"x")
    return tmp_path


@pytest.mark.parametrize(
    ("name", "kind"),
    [
        ("chair.usd", Kind.USD),
        ("chair.USDZ", Kind.USD),
        ("anim.abc", Kind.ALEMBIC),
        ("wood_rough.tx", Kind.TEXTURE),
        ("sky.hdr", Kind.HDRI),
        ("smoke.0001.bgeo.sc", Kind.CACHE),
        ("tool.hdanc", Kind.HDA),
        ("readme.txt", Kind.OTHER),
        ("usd", Kind.OTHER),
    ],
)
def test_kind_of(name: str, kind: Kind):
    assert kind_of(name) == kind


def test_scan_lists_every_file(library: Path):
    found = {record.path.relative_to(library).as_posix(): record for record in scan(library).files}
    assert set(found) == {
        "chair/chair.usd",
        "chair/tex/chair_basecolor.exr",
        "sky.HDR",
        "notes.txt",
    }
    texture = found["chair/tex/chair_basecolor.exr"]
    assert texture.size_bytes == 5
    assert texture.kind == Kind.TEXTURE
    assert texture.modified_time == texture.path.stat().st_mtime
    assert found["sky.HDR"].kind == Kind.HDRI


def test_scan_leaves_the_library_unchanged(library: Path):
    def snapshot() -> dict[str, tuple[int, int]]:
        return {
            path.as_posix(): (path.stat().st_size, path.stat().st_mtime_ns)
            for path in library.rglob("*")
        }

    before = snapshot()
    scan(library)
    assert snapshot() == before


def test_scan_reports_a_missing_root(tmp_path: Path):
    missing = tmp_path / "unplugged-drive"
    result = scan(missing)
    assert result.files == []
    assert result.unreadable == [missing]


def test_scan_reports_a_broken_link(library: Path):
    link = library / "gone.usd"
    try:
        link.symlink_to(library / "deleted.usd")
    except OSError:
        pytest.skip("this system does not let the test create links")
    result = scan(library)
    assert result.unreadable == [link]
    assert len(result.files) == 4


def test_scanner_calls_nothing_that_writes():
    # The brief's first rule: Capsa never changes a library. The scanner may ask
    # for names, sizes and dates only.
    allowed = {"walk", "stat", "append", "lower", "endswith", "items", "sorted"}
    allowed |= {"Path", "FileRecord", "Scan", "kind_of", "field", "dataclass"}
    tree = ast.parse(Path(scanner.__file__).read_text(encoding="utf-8"))
    called = {
        node.func.attr if isinstance(node.func, ast.Attribute) else node.func.id
        for node in ast.walk(tree)
        if isinstance(node, ast.Call)
    }
    assert called <= allowed

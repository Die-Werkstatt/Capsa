from pathlib import Path

import pytest

from capsa.assets import Asset, group
from capsa.scanner import Kind, scan

# The shape of Sandro's library on 2026-11-12 (issue #11), as empty files.
# The metal_053B and goegap names are his; the metalPlates file names are assumed
# (Poly Haven's pattern), and orphan, sunset, branding and models are made up.
LIBRARY = [
    "materials/metal/metal_053B/Metal053B.png",
    "materials/metal/metal_053B/Metal053B_4K-PNG.usdc",
    "materials/metal/metal_053B/Metal053B_4K-PNG.mtlx",
    "materials/metal/metal_053B/Metal053B_4K-PNG.tres",
    "materials/metal/metal_053B/Metal053B_4K-PNG_Color.png",
    "materials/metal/metal_053B/Metal053B_4K-PNG_Displacement.png",
    "materials/metal/metal_053B/Metal053B_4K-PNG_Metalness.png",
    "materials/metal/metal_053B/Metal053B_4K-PNG_NormalDX.png",
    "materials/metal/metal_053B/Metal053B_4K-PNG_NormalGL.png",
    "materials/metal/metal_053B/Metal053B_4K-PNG_NormalGL.png.rat",
    "materials/metal/metal_053B/Metal053B_4K-PNG_Roughness.png",
    "materials/metal/metal_053B/Metal053B_4K-PNG_Roughness.png.rat",
    "materials/metal/plates/metalPlates_08/metalPlates_08_4K/metalPlates_08_diff_4k.jpg",
    "materials/metal/plates/metalPlates_08/metalPlates_08_4K/metalPlates_08_rough_4k.jpg",
    "materials/metal/plates/metalPlates_08/metalPlates_08_4K/metalPlates_08_nor_gl_4k.jpg",
    "hdri/exterior/4k/goegap_4k.exr",
    "hdri/exterior/4k/goegap_4k.exr.rat",
    "hdri/exterior/4k/sunset_4k.hdr",
    "hdri/exterior/4k/orphan_4k.exr.rat",
    "branding/logo.png",
    "branding/intro.mov",
    "models/crate.obj",
    "models/crate.fbx",
]


@pytest.fixture
def assets(tmp_path: Path) -> dict[str, Asset]:
    for name in LIBRARY:
        path = tmp_path / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.touch()
    found = group(scan(tmp_path).files)
    return {asset.path.relative_to(tmp_path).as_posix(): asset for asset in found}


def test_every_file_lands_in_exactly_one_asset(assets: dict[str, Asset]):
    assert sum(len(asset.files) for asset in assets.values()) == len(LIBRARY)


def test_texture_set_folder_is_one_material(assets: dict[str, Asset]):
    metal = assets["materials/metal/metal_053B"]
    assert metal.name == "metal_053B"
    assert metal.kind == Kind.MATERIAL
    assert len(metal.files) == 12
    # The preview picture that came with the download, not one of the maps.
    assert metal.cover.name == "Metal053B.png"


def test_material_without_preview_shows_its_color_map(assets: dict[str, Asset]):
    plates = assets["materials/metal/plates/metalPlates_08/metalPlates_08_4K"]
    assert plates.kind == Kind.MATERIAL
    assert plates.cover.name == "metalPlates_08_diff_4k.jpg"


def test_rat_copy_joins_its_source(assets: dict[str, Asset]):
    goegap = assets["hdri/exterior/4k/goegap_4k.exr"]
    assert goegap.name == "goegap_4k"
    assert goegap.kind == Kind.HDRI
    assert [record.path.name for record in goegap.files] == [
        "goegap_4k.exr",
        "goegap_4k.exr.rat",
    ]
    assert goegap.cover == goegap.path


def test_rat_without_source_stands_alone(assets: dict[str, Asset]):
    orphan = assets["hdri/exterior/4k/orphan_4k.exr.rat"]
    assert orphan.kind == Kind.TEXTURE
    # OpenImageIO cannot read .rat, so there is nothing to show.
    assert orphan.cover is None


def test_other_files_are_one_asset_each(assets: dict[str, Asset]):
    assert assets["hdri/exterior/4k/sunset_4k.hdr"].kind == Kind.HDRI
    assert assets["branding/logo.png"].kind == Kind.TEXTURE
    assert assets["branding/logo.png"].cover is not None
    assert assets["branding/intro.mov"].kind == Kind.OTHER
    assert assets["models/crate.obj"].kind == Kind.OBJ
    assert assets["models/crate.fbx"].kind == Kind.FBX
    assert assets["models/crate.obj"].cover is None


def test_one_map_alone_is_not_a_material(tmp_path: Path):
    (tmp_path / "wall_normal.png").touch()
    (tmp_path / "wall_photo.png").touch()
    assert [asset.kind for asset in group(scan(tmp_path).files)] == [Kind.TEXTURE, Kind.TEXTURE]

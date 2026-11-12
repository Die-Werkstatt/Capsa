import tomllib
from importlib.metadata import version
from pathlib import Path


def test_installed_version_matches_pyproject():
    pyproject = Path(__file__).parent.parent / "pyproject.toml"
    declared = tomllib.loads(pyproject.read_text(encoding="utf-8"))["project"]["version"]
    assert version("capsa") == declared

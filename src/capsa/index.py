"""Capsa's notebook: one SQLite file that remembers the assets a scan found."""

import sqlite3
from dataclasses import dataclass
from pathlib import Path

from capsa.assets import Asset
from capsa.scanner import Kind

SCHEMA_VERSION = 2

# Every path in the index is relative to its root and uses forward slashes.
SCHEMA = """
CREATE TABLE roots (
    id INTEGER PRIMARY KEY,
    path TEXT NOT NULL UNIQUE
);
CREATE TABLE assets (
    id INTEGER PRIMARY KEY,
    root_id INTEGER NOT NULL REFERENCES roots (id),
    path TEXT NOT NULL,
    name TEXT NOT NULL,
    kind TEXT NOT NULL,
    cover TEXT,
    missing INTEGER NOT NULL DEFAULT 0,
    UNIQUE (root_id, path)
);
CREATE TABLE files (
    asset_id INTEGER NOT NULL REFERENCES assets (id),
    path TEXT NOT NULL,
    size_bytes INTEGER NOT NULL,
    modified_time REAL NOT NULL,
    kind TEXT NOT NULL
);
CREATE INDEX files_by_asset ON files (asset_id);
-- The search table. Its rowid is the id of the asset in `assets`.
CREATE VIRTUAL TABLE assets_search USING fts5 (path);
"""


@dataclass(frozen=True)
class IndexedAsset:
    name: str
    kind: Kind
    path: Path
    cover: Path | None
    size_bytes: int  # all its files together
    modified_time: float  # its newest file
    missing: bool


@dataclass(frozen=True)
class Changes:
    added: int
    changed: int
    missing: int


class Index:
    def __init__(self, path: Path) -> None:
        self.path = path
        self._db = sqlite3.connect(path)
        version = self._db.execute("PRAGMA user_version").fetchone()[0]
        if version == 0:
            self._create()
        elif version != SCHEMA_VERSION:
            self._db.close()
            raise RuntimeError(f"{path} is an index of version {version}, not {SCHEMA_VERSION}.")

    def _create(self) -> None:
        try:
            self._db.executescript(SCHEMA)
        except sqlite3.OperationalError as error:
            if "fts5" in str(error):
                raise RuntimeError("This Python's SQLite has no FTS5 full-text search.") from error
            raise
        self._db.execute(f"PRAGMA user_version = {SCHEMA_VERSION}")

    def close(self) -> None:
        self._db.close()

    def add_root(self, root: Path) -> None:
        # The index must never end up inside the library it describes.
        if self.path.resolve().is_relative_to(root.resolve()):
            raise ValueError(f"The index {self.path} lies inside the library root {root}.")
        with self._db:
            self._db.execute("INSERT OR IGNORE INTO roots (path) VALUES (?)", (str(root),))

    def roots(self) -> list[Path]:
        return [Path(path) for (path,) in self._db.execute("SELECT path FROM roots ORDER BY path")]

    def update(self, root: Path, assets: list[Asset]) -> Changes:
        """Bring the index in line with the assets a scan of `root` found.

        An asset the scan did not find is marked missing, not forgotten: an
        unplugged drive must not cost its tags.
        """
        (root_id,) = self._db.execute(
            "SELECT id FROM roots WHERE path = ?", (str(root),)
        ).fetchone()
        known = {
            path: (asset_id, missing)
            for asset_id, path, missing in self._db.execute(
                "SELECT id, path, missing FROM assets WHERE root_id = ?", (root_id,)
            )
        }
        added = changed = 0
        with self._db:
            for asset in assets:
                path = asset.path.relative_to(root).as_posix()
                cover = asset.cover.relative_to(root).as_posix() if asset.cover else None
                files = [
                    (
                        f.path.relative_to(root).as_posix(),
                        f.size_bytes,
                        f.modified_time,
                        f.kind.value,
                    )
                    for f in asset.files
                ]
                before = known.pop(path, None)
                if before is None:
                    cursor = self._db.execute(
                        "INSERT INTO assets (root_id, path, name, kind, cover) VALUES (?, ?, ?, ?, ?)",
                        (root_id, path, asset.name, asset.kind.value, cover),
                    )
                    asset_id = cursor.lastrowid
                    self._db.execute(
                        "INSERT INTO assets_search (rowid, path) VALUES (?, ?)", (asset_id, path)
                    )
                    added += 1
                else:
                    asset_id, was_missing = before
                    if not was_missing and files == self._files(asset_id):
                        continue
                    self._db.execute(
                        "UPDATE assets SET kind = ?, cover = ?, missing = 0 WHERE id = ?",
                        (asset.kind.value, cover, asset_id),
                    )
                    self._db.execute("DELETE FROM files WHERE asset_id = ?", (asset_id,))
                    changed += 1
                self._db.executemany(
                    "INSERT INTO files (asset_id, path, size_bytes, modified_time, kind)"
                    " VALUES (?, ?, ?, ?, ?)",
                    [(asset_id, *file) for file in files],
                )
            # Whatever is left in `known` was not in the scan.
            newly_missing = [(asset_id,) for asset_id, missing in known.values() if not missing]
            self._db.executemany("UPDATE assets SET missing = 1 WHERE id = ?", newly_missing)
        return Changes(added, changed, len(newly_missing))

    def _files(self, asset_id: int) -> list[tuple[str, int, float, str]]:
        return self._db.execute(
            "SELECT path, size_bytes, modified_time, kind FROM files WHERE asset_id = ? ORDER BY rowid",
            (asset_id,),
        ).fetchall()

    def search(self, text: str) -> list[IndexedAsset]:
        """Assets whose path contains every word of `text`, best match first.

        A word matches from its start: "cha" finds "chair".
        """
        words = ['"' + word.replace('"', '""') + '"*' for word in text.split()]
        if not words:
            return []
        rows = self._db.execute(
            "SELECT roots.path, assets.path, name, assets.kind, cover, missing,"
            " SUM(files.size_bytes), MAX(files.modified_time)"
            " FROM assets_search"
            " JOIN assets ON assets.id = assets_search.rowid"
            " JOIN roots ON roots.id = assets.root_id"
            " JOIN files ON files.asset_id = assets.id"
            " WHERE assets_search MATCH ?"
            " GROUP BY assets.id ORDER BY assets_search.rank",
            (" ".join(words),),
        )
        return [
            IndexedAsset(
                name,
                Kind(kind),
                Path(root) / path,
                Path(root) / cover if cover else None,
                size_bytes,
                modified_time,
                bool(missing),
            )
            for root, path, name, kind, cover, missing, size_bytes, modified_time in rows
        ]

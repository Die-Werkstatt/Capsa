"""Capsa's notebook: one SQLite file that remembers what the scanner found."""

import sqlite3
from dataclasses import dataclass
from pathlib import Path

from capsa.scanner import FileRecord, Kind

SCHEMA_VERSION = 1

SCHEMA = """
CREATE TABLE roots (
    id INTEGER PRIMARY KEY,
    path TEXT NOT NULL UNIQUE
);
CREATE TABLE files (
    id INTEGER PRIMARY KEY,
    root_id INTEGER NOT NULL REFERENCES roots (id),
    path TEXT NOT NULL,  -- relative to the root, with forward slashes
    size_bytes INTEGER NOT NULL,
    modified_time REAL NOT NULL,
    kind TEXT NOT NULL,
    missing INTEGER NOT NULL DEFAULT 0,
    UNIQUE (root_id, path)
);
-- The search table. Its rowid is the id of the file in `files`.
CREATE VIRTUAL TABLE files_search USING fts5 (path);
"""


@dataclass(frozen=True)
class IndexedFile:
    path: Path
    size_bytes: int
    modified_time: float
    kind: Kind
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

    def update(self, root: Path, files: list[FileRecord]) -> Changes:
        """Bring the index in line with a scan of `root`.

        A file the scan did not find is marked missing, not forgotten: an
        unplugged drive must not cost its tags.
        """
        (root_id,) = self._db.execute(
            "SELECT id FROM roots WHERE path = ?", (str(root),)
        ).fetchone()
        known = {
            path: (file_id, size_bytes, modified_time, missing)
            for file_id, path, size_bytes, modified_time, missing in self._db.execute(
                "SELECT id, path, size_bytes, modified_time, missing FROM files WHERE root_id = ?",
                (root_id,),
            )
        }
        added = changed = 0
        with self._db:
            for record in files:
                path = record.path.relative_to(root).as_posix()
                values = (record.size_bytes, record.modified_time, record.kind.value)
                before = known.pop(path, None)
                if before is None:
                    cursor = self._db.execute(
                        "INSERT INTO files (root_id, path, size_bytes, modified_time, kind)"
                        " VALUES (?, ?, ?, ?, ?)",
                        (root_id, path, *values),
                    )
                    self._db.execute(
                        "INSERT INTO files_search (rowid, path) VALUES (?, ?)",
                        (cursor.lastrowid, path),
                    )
                    added += 1
                elif before[1:] != (record.size_bytes, record.modified_time, 0):
                    self._db.execute(
                        "UPDATE files SET size_bytes = ?, modified_time = ?, kind = ?, missing = 0"
                        " WHERE id = ?",
                        (*values, before[0]),
                    )
                    changed += 1
            # Whatever is left in `known` was not in the scan.
            newly_missing = [(file_id,) for file_id, _, _, missing in known.values() if not missing]
            self._db.executemany("UPDATE files SET missing = 1 WHERE id = ?", newly_missing)
        return Changes(added, changed, len(newly_missing))

    def search(self, text: str) -> list[IndexedFile]:
        """Files whose path contains every word of `text`, best match first.

        A word matches from its start: "cha" finds "chair".
        """
        words = ['"' + word.replace('"', '""') + '"*' for word in text.split()]
        if not words:
            return []
        rows = self._db.execute(
            "SELECT roots.path, files.path, size_bytes, modified_time, kind, missing"
            " FROM files_search"
            " JOIN files ON files.id = files_search.rowid"
            " JOIN roots ON roots.id = files.root_id"
            " WHERE files_search MATCH ? ORDER BY rank",
            (" ".join(words),),
        )
        return [
            IndexedFile(Path(root) / path, size_bytes, modified_time, Kind(kind), bool(missing))
            for root, path, size_bytes, modified_time, kind, missing in rows
        ]

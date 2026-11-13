# aislop-ignore-file hallucinated-import -- the pywebview package is imported as "webview"
"""Capsa's window: a frameless pywebview window showing the index as a grid.

The page in `web/` calls the methods of `Api` as `window.pywebview.api.<name>`.
No web server of our own: pywebview passes the calls between JavaScript and Python.
"""

import base64
import subprocess
import sys
import threading
from pathlib import Path

import webview

from capsa.index import Index
from capsa.library import INDEX_NAME, THUMBNAILS_NAME, refresh
from capsa.thumbnails import make_thumbnail

PAGE = Path(__file__).parent / "web" / "index.html"


class Api:
    def __init__(self, data: Path) -> None:
        self._data = data
        self._window: webview.Window | None = None
        self._maximized = False
        # A rescan and the page's thumbnail calls run in different threads and can
        # make the same thumbnail at once. They take turns.
        self._thumbnails = threading.Lock()

    def search(self, text: str) -> list[dict]:
        # pywebview runs each call in its own thread; an SQLite connection
        # belongs to the thread that opened it, so every call opens its own.
        index = Index(self._data / INDEX_NAME)
        try:
            return [
                {
                    "name": asset.name,
                    "kind": asset.kind.value,
                    "path": str(asset.path),
                    "cover": str(asset.cover) if asset.cover else None,
                    "size": asset.size_bytes,
                    "modified": asset.modified_time,
                    "missing": asset.missing,
                }
                for asset in index.search(text)
            ]
        finally:
            index.close()

    def folders(self) -> list[dict]:
        """The library roots, each with the number of assets in it."""
        index = Index(self._data / INDEX_NAME)
        try:
            assets = index.search("")
            return [
                {"path": str(root), "assets": sum(a.path.is_relative_to(root) for a in assets)}
                for root in index.roots()
            ]
        finally:
            index.close()

    def add_folder(self) -> dict | None:
        """Ask for a folder and add it as a library root. None when the dialog is cancelled."""
        chosen = self._window.create_file_dialog(webview.FileDialog.FOLDER)
        if not chosen:
            return None
        folder = Path(chosen[0]).resolve()
        index = Index(self._data / INDEX_NAME)
        try:
            index.add_root(folder)
        except ValueError as error:
            return {"error": str(error)}
        finally:
            index.close()
        return {"added": str(folder)}

    def rescan(self) -> None:
        """Scan every library root, as `capsa scan` does."""
        with self._thumbnails:
            index = Index(self._data / INDEX_NAME)
            try:
                refresh(index, self._data / THUMBNAILS_NAME)
            finally:
                index.close()

    def thumbnail(self, cover: str) -> str | None:
        """The thumbnail of a cover image as a data URL the page can show."""
        with self._thumbnails:
            path = make_thumbnail(Path(cover), self._data / THUMBNAILS_NAME)
        if path is None:
            return None
        return "data:image/jpeg;base64," + base64.b64encode(path.read_bytes()).decode()

    def show_in_explorer(self, path: str) -> None:
        """Open the folder that holds `path` in the system file manager."""
        if sys.platform == "win32":
            # A string, not a list: list quoting would wrap "/select,..." in quotes,
            # and Explorer only accepts the quotes around the path.
            subprocess.Popen(f'explorer /select,"{path}"')
        else:
            subprocess.Popen(["xdg-open", str(Path(path).parent)])

    def minimize(self) -> None:
        self._window.minimize()

    def toggle_maximize(self) -> None:
        if self._maximized:
            self._window.restore()
        else:
            self._window.maximize()
        self._maximized = not self._maximized

    def close(self) -> None:
        self._window.destroy()


def open_window(data: Path) -> None:
    api = Api(data)
    api._window = webview.create_window(
        "Capsa",
        str(PAGE),
        js_api=api,
        frameless=True,
        easy_drag=False,
        width=1280,
        height=800,
        min_size=(720, 480),
        background_color="#0B0B0C",
    )
    webview.start()

"""The command line: `capsa add <folder>`, `capsa scan`, `capsa search <words>`."""

import argparse
from pathlib import Path

from capsa.index import Index
from capsa.library import INDEX_NAME, THUMBNAILS_NAME, data_folder, refresh


def main(arguments: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(prog="capsa")
    commands = parser.add_subparsers(dest="command", required=True)
    add = commands.add_parser("add", help="add a library root")
    add.add_argument("folder", type=Path)
    commands.add_parser("scan", help="scan every library root")
    search = commands.add_parser("search", help="find assets")
    search.add_argument("words", nargs="+")
    options = parser.parse_args(arguments)

    data = data_folder()
    data.mkdir(parents=True, exist_ok=True)
    index = Index(data / INDEX_NAME)
    try:
        if options.command == "add":
            folder = options.folder.resolve()
            if not folder.is_dir():
                parser.error(f"{folder} is not a folder.")
            index.add_root(folder)
            print(f"Added {folder}. Capsa's data is in {data}.")
        elif options.command == "scan":
            for result in refresh(index, data / THUMBNAILS_NAME):
                changes = result.changes
                print(result.root)
                print(
                    f"  {changes.added} added, {changes.changed} changed, {changes.missing} missing"
                )
                print(
                    f"  {result.thumbnails} thumbnails, {result.without_thumbnail} covers unreadable"
                )
                if result.unreadable:
                    print(f"  {result.unreadable} folders or files could not be read")
        else:
            for asset in index.search(" ".join(options.words)):
                print(f"{asset.kind.value:10} {asset.name:30} {asset.path}")
    finally:
        index.close()


if __name__ == "__main__":
    main()

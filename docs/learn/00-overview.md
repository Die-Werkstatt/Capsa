# Capsa in plain language

Think of Capsa as a **contact sheet for everything you own**: every model, texture and HDRI on your drives, on one page, with a search box.

Your assets stay where they are. Capsa walks through the folders you point it at, the way you would click through them in Explorer, and writes down what it finds in its own notebook, the **index**. When you search, Capsa looks in the notebook, not on the drives. That is why it is fast.

## The parts

- **The scanner** walks the folders and lists the files. Like a File Pattern node: it finds files, it does not open them.
- **The index** is the notebook: one database file that remembers every asset, its tags and where it lives.
- **Thumbnails** are small preview images Capsa makes once and keeps, like a texture cache.
- **The interface** shows the index as a grid you can search and filter.

The scanner, the grouping into assets, the index and thumbnails exist so far: see [scanner.md](scanner.md), [assets.md](assets.md), [index.md](index.md) and [thumbnails.md](thumbnails.md).

## What Capsa never does

It never moves, renames, changes or deletes your files. Everything Capsa writes goes into its own folder.

## Phases

1. Index and browse: scan folders, thumbnails, search, tags.
2. Inspect: what is inside an asset before you open it.
3. Into Houdini: a panel that imports the selected asset.

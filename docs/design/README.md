# Interface

The agreed direction for Capsa's interface. Open [`prototype.html`](prototype.html) in a browser to click through it. It runs on 24 example assets and reads nothing from disk.

The look carries over from Laterna: dark, sharp corners, hairline rows, little text. Detail that isn't needed to pick an asset goes to the log, not the window.

## Window

One frameless window with a custom title bar:

- Left: the Capsa lockup. In the Inspector, a breadcrumb follows it.
- Centre: the search box (`Ctrl K`).
- Right: settings, then minimise, maximise, close. In the Inspector, previous/next and the position (`9 / 24`) sit before settings.

No status text in the title bar. A scan shows a thin progress line while it runs and nothing otherwise.

## Views

### Catalogue

The home view. Three columns:

- **Sidebar:** Library (All, Favourites, Models, Textures, HDRIs, Caches), Collections (manual, plus "Added this week" as an automatic one), Needs Attention (Missing files, Units not set, Duplicates). Counts on the right.
- **Grid:** a heading with the count, Filter, a thumbnail size slider, one button that switches grid and list, and sort (Recent, Name, Size).
- **Details:** preview, name, type, a short key/value list, dimensions, variants, texture set, tags, then Copy path and Show in Explorer.

### Search

Opened from the title bar or `Ctrl K`. One large input, results grouped by type. `type:` tokens filter. `Enter` opens the first result in the Inspector.

### Inspector

One asset, large. A filmstrip of the current list along the bottom, the details panel on the right. Arrow keys step through the list. HDRIs get an exposure slider. Texture sets render as a material sphere you can drag to rotate.

### Settings

A sheet from the right: library folders (Add folder, file count per folder), index (asset count, last scan, Rescan all), display (units, texture set preview), thumbnail cache (location, size, Clear cache), Houdini node status.

## Interaction

- Shortcuts live in the right-click menu next to each action, not in a bar: Open in Inspector (`Space`), Copy path (`Ctrl C`), Show in Explorer (`Ctrl E`), Favourite (`F`), Add to collection, Edit tags (`T`), Rescan folder.
- Double-click or `Space` opens the Inspector. `Esc` closes a menu, then the settings sheet, then goes back a view.
- Click selects. The selection is the only thing drawn in blue.

## Tokens

| Token | Value | Use |
|---|---|---|
| Ground | `#0B0B0C` | Window background |
| Surface | `#111113` | Title bar, panels |
| Tile | `#141416` | Thumbnail background |
| Edge | `#2A2A2E` | Borders |
| Line | ink at 8% | Hairline rows |
| Ink | `#EDEDED` | Primary text |
| Mid | `#8C8D94` | Secondary text |
| Low | `#55565D` | Counts, placeholders |
| Lid | `#4F8CFF` | Selected, nothing else |
| Fault | `#E8664A` | Errors and missing files, nothing else |
| Close | `#C42B1C` | Close button hover |

- Selection: a 4px Lid bar lifted 8px above the selected tile, or on the left edge of a list row. It is the lid from the logo.
- Corners: square everywhere.
- Text: sentence case, plain-noun labels, no helper text, no tracked all-caps labels. Mono only for data and paths.
- Type: IBM Plex Sans and IBM Plex Mono are placeholders until the font is chosen.

## Not decided yet

The prototype shows these, but they are proposals:

- **Units:** dimensions shown in metres, read from the stage's `metersPerUnit`. A USD file that doesn't author it falls back to centimetres (OpenUSD's default) and lands under Units not set.
- **Texture sets:** one set per folder, with name-prefix matching as a fallback. The colour map is the cover; the Catalogue shows it on a material sphere. EXR and TX maps need PNG previews made with OpenImageIO.
- **USD variants:** a Component Builder folder counts as one asset (payload, geo and mtl files are its layers). Variants come from the file, thumbnails from its `variants/` folder.
- **Houdini:** a Capsa Import LOP with a Browse button that opens the Capsa picker, instead of a Send to Houdini button. See the brief, section 5.
- **Font:** see Type above.

The earlier concept rounds are in the project's design board, not in this repo.

# Capsa: Website

One-page site with a hero, the library window, features and download. Open `index.html` in a browser; there is no build step.

A wireframe Capsa box floats over a perspective grid with your assets circling it. It scrolls away with the hero and comes back at the download section, where the lid closes. The asset type named in the title is drawn larger. The library section draws the Capsa window in line art.

Blue is used only where the app uses it: the lids and the selected tile.

## Hosting on Cloudflare Pages

Connect this repository as a Pages project (Git integration) with:

- Production branch: `main`
- Framework preset: None
- Build command: empty
- Root directory: `docs/website`
- Build output directory: `/`

The folder is self-contained, so nothing outside `docs/website` is published.

## Dependencies

- three.js r128 from cdnjs
- Barlow, IBM Plex Sans and IBM Plex Mono from Google Fonts

## Placeholders

- Download for Windows is shown as unavailable until there is a build. Run from source links to the README.
- System requirement ("Windows 11"): the only system Capsa has run on

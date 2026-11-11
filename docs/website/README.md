# Capsa: Website

One-page site with a hero, features and download. Open `index.html` in a browser; there is no build step.

A wireframe Capsa box floats over a perspective grid. While you scroll, the lid lifts, assets (models, textures, HDRIs, stages, caches) circle the box, the box comes apart into labelled parts and then closes again at the download section. The highlighted asset type follows the cycling word in the title.

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
- Michroma, IBM Plex Sans and JetBrains Mono from Google Fonts

## Placeholders

- Houdini minimum version ("20.5 or later")
- System requirement ("Windows 10 or 11")
- Download and Source links point to the repository
- The brief says Capsa is not distributed publicly, so whether the site offers a download is still open

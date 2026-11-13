// The details panel: preview, name, facts, tags and actions of the selected asset.

import { KINDS, askText, button, copyPath, explore, size, star } from "./ui.js";

const details = document.getElementById("details");

// `url` is the thumbnail, when it has loaded; `onFavourite` runs when the star is clicked.
export function drawDetails(asset, url, onFavourite) {
  if (!asset) {
    const none = document.createElement("p");
    none.className = "none";
    none.textContent = "Select an asset";
    details.replaceChildren(none);
    return;
  }
  const preview = document.createElement("div");
  preview.className = "preview";
  if (url) preview.style.backgroundImage = `url("${url}")`;
  const name = document.createElement("span");
  name.className = "big-name";
  name.textContent = asset.name;
  const head = document.createElement("div");
  head.className = "name-row";
  head.append(name, star(asset, onFavourite));
  const rows = document.createElement("div");
  rows.className = "rows";
  const row = (key, value, bad) => {
    const k = document.createElement("span");
    k.textContent = key;
    const v = document.createElement("span");
    v.textContent = value;
    v.title = value;
    if (bad) v.className = "bad";
    rows.append(k, v);
  };
  row("Type", KINDS[asset.kind]);
  row("Size", size(asset.size));
  row("Modified", new Date(asset.modified * 1000).toLocaleDateString());
  row("Path", asset.path);
  if (asset.missing) row("Status", "Missing", true);
  const actions = document.createElement("div");
  actions.className = "actions";
  const copy = button("Copy path", "action primary", () => copyPath(asset));
  const explorer = button("Show in Explorer", "action", () => explore(asset));
  explorer.disabled = asset.missing;
  actions.append(copy, explorer);
  details.replaceChildren(preview, head, rows, tagList(asset), actions);
}

// Tag chips remove their tag when clicked; "+ tag" (or T) asks for a new one.
function tagList(asset) {
  const list = document.createElement("div");
  list.className = "tags";
  const redraw = (tags) => {
    asset.tags = tags;
    list.replaceWith(tagList(asset));
  };
  for (const tag of asset.tags) {
    const chip = button(tag, "tag", async () => redraw(await window.pywebview.api.remove_tag(asset.path, tag)));
    chip.title = `Remove ${tag}`;
    list.append(chip);
  }
  const add = button("+ tag", "tag add", () =>
    askText(add, "New tag", async (tag) => {
      redraw(tag ? await window.pywebview.api.add_tag(asset.path, tag) : asset.tags);
    }),
  );
  add.id = "add-tag";
  list.append(add);
  return list;
}

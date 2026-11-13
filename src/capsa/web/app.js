// The catalogue: asks Python for assets (window.pywebview.api.search) and shows them as
// a sidebar of groups, a grid of tiles and the details of the selected asset.
// Thumbnails load one by one after the tiles are drawn, so the grid appears at once.

const KINDS = {
  material: "Material", hdri: "HDRI", texture: "Texture", sequence: "Sequence",
  usd: "USD", alembic: "Alembic", fbx: "FBX", obj: "OBJ", cache: "Cache", hda: "HDA", other: "Other",
};
// Sidebar groups: [id, label, kinds]. "All" has no kinds and takes everything.
const GROUPS = [
  ["all", "All", []],
  ["models", "Models", ["usd", "alembic", "fbx", "obj"]],
  ["materials", "Materials", ["material"]],
  ["textures", "Textures", ["texture", "sequence"]],
  ["hdris", "HDRIs", ["hdri"]],
  ["caches", "Caches", ["cache"]],
];

const nav = document.getElementById("nav");
const grid = document.getElementById("grid");
const count = document.getElementById("count");
const title = document.getElementById("title");
const details = document.getElementById("details");
const search = document.getElementById("search");
const toast = document.getElementById("toast");

let assets = []; // the answer to the last search
let group = "all";
let selected = null; // path of the selected asset
let drawn = 0; // which drawing the tiles belong to, so an old thumbnail loop stops
const thumbnails = new Map(); // cover path -> data URL, or null when it cannot be read

function inGroup(asset, id) {
  if (id === "missing") return asset.missing;
  const kinds = GROUPS.find((g) => g[0] === id)[2];
  return kinds.length === 0 || kinds.includes(asset.kind);
}

function label(id) {
  return id === "missing" ? "Missing files" : GROUPS.find((g) => g[0] === id)[1];
}

let asked = 0;
async function find(text) {
  const ask = ++asked;
  const answer = await window.pywebview.api.search(text);
  if (ask !== asked) return;
  assets = answer;
  if (group === "missing" && !assets.some((a) => a.missing)) group = "all";
  draw();
}

function draw() {
  const ask = ++drawn;
  const visible = assets.filter((a) => inGroup(a, group));
  if (!visible.some((a) => a.path === selected)) selected = visible.length ? visible[0].path : null;
  drawNav();
  title.textContent = label(group);
  count.textContent = visible.length;
  grid.replaceChildren(...visible.map(tile));
  drawDetails();
  loadThumbnails(ask);
}

function drawNav() {
  const item = (id, extra) => {
    const button = document.createElement("button");
    button.type = "button";
    button.dataset.group = id;
    const name = document.createElement("b");
    name.textContent = label(id);
    const number = document.createElement("span");
    number.className = "number";
    number.textContent = assets.filter((a) => inGroup(a, id)).length;
    button.append(name, number);
    const li = document.createElement("li");
    li.className = [id === group ? "on" : "", extra].join(" ").trim();
    li.append(button);
    return li;
  };
  const section = (caption, items) => {
    const div = document.createElement("div");
    div.className = "section";
    const head = document.createElement("span");
    head.className = "caption";
    head.textContent = caption;
    const list = document.createElement("ul");
    list.append(...items);
    div.append(head, list);
    return div;
  };
  const sections = [section("Library", GROUPS.map((g) => item(g[0])))];
  if (assets.some((a) => a.missing)) sections.push(section("Needs attention", [item("missing", "bad")]));
  nav.replaceChildren(...sections);
}

function tile(asset) {
  const element = document.createElement("button");
  element.type = "button";
  element.className = asset.missing ? "tile missing" : "tile";
  element.title = asset.path;
  element.dataset.path = asset.path;
  const picture = document.createElement("div");
  picture.className = asset.path === selected ? "picture on" : "picture";
  showThumbnail(picture, asset);
  const name = document.createElement("span");
  name.className = "name";
  name.textContent = asset.name;
  const kind = document.createElement("span");
  kind.className = "kind";
  kind.textContent = asset.missing ? "Missing" : KINDS[asset.kind];
  element.append(picture, name, kind);
  return element;
}

function showThumbnail(element, asset) {
  const url = thumbnails.get(asset.cover);
  if (url) element.style.backgroundImage = `url("${url}")`;
}

async function loadThumbnails(ask) {
  for (const element of grid.children) {
    const asset = assets.find((a) => a.path === element.dataset.path);
    if (!asset.cover || thumbnails.has(asset.cover)) continue;
    const url = await window.pywebview.api.thumbnail(asset.cover);
    thumbnails.set(asset.cover, url);
    if (ask !== drawn) return;
    showThumbnail(element.firstChild, asset);
    if (asset.path === selected) showThumbnail(details.querySelector(".preview"), asset);
  }
}

function drawDetails() {
  const asset = assets.find((a) => a.path === selected);
  if (!asset) {
    const none = document.createElement("p");
    none.className = "none";
    none.textContent = "Select an asset";
    details.replaceChildren(none);
    return;
  }
  const preview = document.createElement("div");
  preview.className = "preview";
  showThumbnail(preview, asset);
  const name = document.createElement("span");
  name.className = "big-name";
  name.textContent = asset.name;
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
  const copy = button("Copy path", "primary", () => copyPath(asset));
  const explorer = button("Show in Explorer", "", () =>
    window.pywebview.api.show_in_explorer(asset.kind === "sequence" ? asset.cover : asset.path),
  );
  explorer.disabled = asset.missing;
  actions.append(copy, explorer);
  details.replaceChildren(preview, name, rows, actions);
}

function button(text, extra, onClick) {
  const element = document.createElement("button");
  element.type = "button";
  element.className = ["action", extra].join(" ").trim();
  element.textContent = text;
  element.onclick = onClick;
  return element;
}

function size(bytes) {
  const units = ["B", "KB", "MB", "GB", "TB"];
  let value = bytes;
  let unit = 0;
  while (value >= 1000 && unit < units.length - 1) {
    value /= 1000;
    unit += 1;
  }
  return `${unit === 0 ? value : value.toFixed(1)} ${units[unit]}`;
}

async function copyPath(asset) {
  try {
    await navigator.clipboard.writeText(asset.path);
    say(`Copied ${asset.path}`);
  } catch {
    say("Could not copy the path");
  }
}

let hiding;
function say(text) {
  toast.textContent = text;
  toast.classList.add("on");
  clearTimeout(hiding);
  hiding = setTimeout(() => toast.classList.remove("on"), 1900);
}

function select(path) {
  selected = path;
  for (const element of grid.children) {
    element.firstChild.classList.toggle("on", element.dataset.path === path);
  }
  drawDetails();
}

nav.addEventListener("click", (event) => {
  const button = event.target.closest("[data-group]");
  if (!button) return;
  group = button.dataset.group;
  draw();
  grid.parentElement.scrollTop = 0;
});
grid.addEventListener("click", (event) => {
  const element = event.target.closest(".tile");
  if (element) select(element.dataset.path);
});

// Settings sheet: library folders, Add folder, Rescan all.
const sheet = document.getElementById("sheet");
const settings = document.getElementById("settings");
const progress = document.getElementById("progress");
const rescanButton = document.getElementById("rescan");
const addButton = document.getElementById("add-folder");

function openSheet(open) {
  sheet.hidden = !open;
  settings.classList.toggle("on", open);
  if (open) drawSheet();
}

async function drawSheet() {
  const folders = await window.pywebview.api.folders();
  document.getElementById("folders").replaceChildren(
    ...folders.map((folder) => {
      const row = document.createElement("div");
      row.className = "folder";
      const path = document.createElement("span");
      path.textContent = folder.path;
      path.title = folder.path;
      const number = document.createElement("span");
      number.textContent = folder.assets;
      row.append(path, number);
      return row;
    }),
  );
  document.getElementById("asset-count").textContent = folders.reduce((sum, f) => sum + f.assets, 0);
}

async function rescan() {
  rescanButton.disabled = addButton.disabled = true;
  progress.classList.add("on");
  try {
    await window.pywebview.api.rescan();
  } finally {
    progress.classList.remove("on");
    rescanButton.disabled = addButton.disabled = false;
  }
  thumbnails.clear(); // a changed file has a new thumbnail under the same cover path
  await find(search.value);
  if (!sheet.hidden) drawSheet();
}

settings.onclick = () => openSheet(sheet.hidden);
document.getElementById("sheet-close").onclick = () => openSheet(false);
rescanButton.onclick = rescan;
addButton.onclick = async () => {
  const result = await window.pywebview.api.add_folder();
  if (!result) return;
  if (result.error) {
    say(result.error);
    return;
  }
  drawSheet();
  await rescan();
};

let typing;
search.addEventListener("input", () => {
  clearTimeout(typing);
  typing = setTimeout(() => find(search.value), 150);
});
document.addEventListener("keydown", (event) => {
  if (event.key === "Escape" && !sheet.hidden) openSheet(false);
  if (event.ctrlKey && event.key.toLowerCase() === "k") {
    event.preventDefault();
    search.focus();
    search.select();
  }
});
document.getElementById("minimize").onclick = () => window.pywebview.api.minimize();
document.getElementById("maximize").onclick = () => window.pywebview.api.toggle_maximize();
document.getElementById("close").onclick = () => window.pywebview.api.close();

// window.pywebview.api exists only after this event.
window.addEventListener("pywebviewready", () => find(""));

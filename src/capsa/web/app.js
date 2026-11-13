// The catalogue: asks Python for assets (window.pywebview.api.search) and shows them as tiles.
// Thumbnails load one by one after the tiles are drawn, so the grid appears at once.

const KINDS = {
  material: "Material", hdri: "HDRI", texture: "Texture", sequence: "Sequence",
  usd: "USD", alembic: "Alembic", fbx: "FBX", obj: "OBJ", cache: "Cache", hda: "HDA", other: "Other",
};

const grid = document.getElementById("grid");
const count = document.getElementById("count");
const title = document.getElementById("title");
const search = document.getElementById("search");
let shown = 0; // which search the tiles belong to, so a slow answer cannot overwrite a newer one

async function show(text) {
  const ask = ++shown;
  const assets = await window.pywebview.api.search(text);
  if (ask !== shown) return;
  title.textContent = text.trim() ? "Results" : "All";
  count.textContent = assets.length;
  grid.replaceChildren(...assets.map(tile));
  for (const element of grid.children) {
    if (ask !== shown) return;
    const cover = element.dataset.cover;
    if (!cover) continue;
    const url = await window.pywebview.api.thumbnail(cover);
    if (url) element.firstChild.style.backgroundImage = `url("${url}")`;
  }
}

function tile(asset) {
  const element = document.createElement("div");
  element.className = asset.missing ? "tile missing" : "tile";
  element.title = asset.path;
  if (asset.cover) element.dataset.cover = asset.cover;
  const picture = document.createElement("div");
  picture.className = "picture";
  const name = document.createElement("div");
  name.className = "name";
  name.textContent = asset.name;
  const kind = document.createElement("div");
  kind.className = "kind";
  kind.textContent = asset.missing ? "Missing" : KINDS[asset.kind];
  element.append(picture, name, kind);
  return element;
}

let typing;
search.addEventListener("input", () => {
  clearTimeout(typing);
  typing = setTimeout(() => show(search.value), 150);
});
document.addEventListener("keydown", (event) => {
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
window.addEventListener("pywebviewready", () => show(""));

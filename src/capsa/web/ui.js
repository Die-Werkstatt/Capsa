// Pieces every part of the window uses: buttons, icons, sizes, the toast, the
// right-click menu, a text field in place of a button, and the asset actions.

export const KINDS = {
  material: "Material", hdri: "HDRI", texture: "Texture", sequence: "Sequence",
  usd: "USD", alembic: "Alembic", fbx: "FBX", obj: "OBJ", cache: "Cache", hda: "HDA", other: "Other",
};

export function button(text, className, onClick) {
  const element = document.createElement("button");
  element.type = "button";
  element.className = className;
  element.textContent = text;
  element.onclick = onClick;
  return element;
}

// Icons are <template>s in index.html; each use takes a copy.
export function icon(id) {
  return document.getElementById(id).content.cloneNode(true);
}

export function size(bytes) {
  const units = ["B", "KB", "MB", "GB", "TB"];
  let value = bytes;
  let unit = 0;
  while (value >= 1000 && unit < units.length - 1) {
    value /= 1000;
    unit += 1;
  }
  return `${unit === 0 ? value : value.toFixed(1)} ${units[unit]}`;
}

const toast = document.getElementById("toast");
let hiding;
export function say(text) {
  toast.textContent = text;
  toast.classList.add("on");
  clearTimeout(hiding);
  hiding = setTimeout(() => toast.classList.remove("on"), 1900);
}

// Swaps `element` for a text field. `done` gets the typed text, or "" after Escape.
export function askText(element, name, done) {
  const input = document.createElement("input");
  input.className = "tag-input";
  input.setAttribute("aria-label", name);
  element.replaceWith(input);
  input.focus();
  let finished = false;
  const finish = (keep) => {
    if (finished) return;
    finished = true;
    done(keep ? input.value.trim() : "");
  };
  input.addEventListener("keydown", (event) => {
    event.stopPropagation();
    if (event.key === "Enter") finish(true);
    if (event.key === "Escape") finish(false);
  });
  input.addEventListener("blur", () => finish(true));
}

// The right-click menu: [label, shortcut, action] rows, or a string for a caption, or "-" for a line.
const menu = document.getElementById("menu");

export function openMenu(rows, x, y) {
  menu.replaceChildren(
    ...rows.map((row) => {
      if (row === "-") return document.createElement("hr");
      if (typeof row === "string") {
        const caption = document.createElement("span");
        caption.className = "caption";
        caption.textContent = row;
        return caption;
      }
      const [text, key, action] = row;
      const entry = button(text, "entry", () => {
        closeMenu();
        action();
      });
      if (key) {
        const shortcut = document.createElement("kbd");
        shortcut.textContent = key;
        entry.append(shortcut);
      }
      entry.disabled = !action;
      return entry;
    }),
  );
  menu.hidden = false;
  const box = menu.getBoundingClientRect();
  menu.style.left = `${Math.min(x, innerWidth - box.width - 8)}px`;
  menu.style.top = `${Math.min(y, innerHeight - box.height - 8)}px`;
}

// True when the menu was open.
export function closeMenu() {
  const open = !menu.hidden;
  menu.hidden = true;
  return open;
}

document.addEventListener("click", (event) => {
  if (!menu.contains(event.target)) closeMenu();
});

export function star(asset, onClick) {
  const element = document.createElement("span");
  element.className = asset.favourite ? "star on" : "star";
  element.dataset.star = "";
  element.title = asset.favourite ? "Remove from Favourites (F)" : "Add to Favourites (F)";
  element.append(icon("star-icon"));
  element.onclick = (event) => {
    event.stopPropagation();
    onClick(asset);
  };
  return element;
}

export async function copyPath(asset) {
  try {
    await navigator.clipboard.writeText(asset.path);
    say(`Copied ${asset.path}`);
  } catch {
    say("Could not copy the path");
  }
}

export function explore(asset) {
  window.pywebview.api.show_in_explorer(asset.kind === "sequence" ? asset.cover : asset.path);
}

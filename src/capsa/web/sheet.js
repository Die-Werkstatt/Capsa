// Settings sheet: library folders, Add folder, Rescan all.
// After a scan it sends a "rescanned" event, and the catalogue searches again.

import { say } from "./ui.js";

const sheet = document.getElementById("sheet");
const settings = document.getElementById("settings");
const progress = document.getElementById("progress");
const rescanButton = document.getElementById("rescan");
const addButton = document.getElementById("add-folder");

export function openSheet(open) {
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
  window.dispatchEvent(new Event("rescanned"));
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

import { app } from "../../scripts/app.js";
import { api } from "../../scripts/api.js";

const NODE = "RICHIEPIC_H3ReferenceGallery";
const SUBFOLDER = "refgallery";
const KIND = (name) => {
  const ext = name.split(".").pop().toLowerCase();
  if (["png", "jpg", "jpeg", "webp", "bmp", "gif", "tif", "tiff"].includes(ext)) return "image";
  if (["mp4", "mov", "webm", "mkv", "avi", "m4v"].includes(ext)) return "video";
  if (["wav", "mp3", "flac", "ogg", "m4a", "aac", "opus"].includes(ext)) return "audio";
  return null;
};
const COLORS = { image: "#4a9eff", video: "#ff6b6b", audio: "#c792ea" };

const CSS = `
.h3g{display:flex;flex-direction:column;gap:6px;font:12px sans-serif;color:#ddd;height:100%;box-sizing:border-box}
.h3g-bar{display:flex;gap:6px;align-items:center;flex-wrap:wrap}
.h3g-bar button{background:#2b2f36;color:#ddd;border:1px solid #444;border-radius:6px;padding:4px 10px;cursor:pointer}
.h3g-bar button:hover{background:#363b44}
.h3g-count{opacity:.7;margin-left:auto}
.h3g-grid{flex:1;overflow:auto;display:grid;grid-template-columns:repeat(auto-fill,minmax(120px,1fr));gap:6px;
  grid-auto-rows:max-content;border:1px dashed #555;border-radius:8px;padding:6px;min-height:80px;align-content:start}
.h3g-grid.drag{border-color:#4a9eff;background:rgba(74,158,255,.08)}
.h3g-empty{grid-column:1/-1;text-align:center;opacity:.5;padding:20px}
.h3g-card{position:relative;border:2px solid #444;border-radius:8px;background:#1d2026;overflow:hidden;cursor:grab;
  min-height:max-content;flex-shrink:0}
.h3g-card.off{opacity:.35}
.h3g-card.over{outline:2px solid #fff}
.h3g-thumb{width:100%;height:110px;min-height:110px;max-height:none;object-fit:cover;display:block;background:#111}
.h3g-audio{width:100%;height:110px;display:flex;align-items:center;justify-content:center;font-size:32px;background:#111}
.h3g-x{position:absolute;top:3px;right:3px;background:rgba(0,0,0,.7);border:none;color:#fff;border-radius:4px;cursor:pointer;width:20px;height:20px}
.h3g-on{position:absolute;top:3px;left:3px}
.h3g-meta{padding:3px 5px}
.h3g-tag{font-weight:bold}
.h3g-name{opacity:.7;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.h3g-trim{display:flex;gap:3px;margin-top:2px}
.h3g-trim input{width:50%;background:#111;color:#ddd;border:1px solid #444;border-radius:4px;padding:1px 3px;font-size:11px}
`;

function injectCss() {
  if (document.getElementById("h3g-css")) return;
  const style = document.createElement("style");
  style.id = "h3g-css";
  style.textContent = CSS;
  document.head.appendChild(style);
}

function viewUrl(item) {
  const q = new URLSearchParams({ filename: item.name, subfolder: item.subfolder || "", type: item.type || "input" });
  return api.apiURL(`/view?${q}`);
}

async function upload(file) {
  const body = new FormData();
  body.append("image", file, file.name);
  body.append("subfolder", SUBFOLDER);
  body.append("type", "input");
  const resp = await api.fetchApi("/upload/image", { method: "POST", body });
  if (resp.status !== 200) throw new Error(`${file.name}: upload failed (${resp.status})`);
  const data = await resp.json();
  return { name: data.name, subfolder: data.subfolder, type: data.type, kind: KIND(file.name), enabled: true };
}

function setupNode(node) {
  injectCss();
  const store = node.widgets.find((w) => w.name === "gallery");
  // Keep the JSON widget (it is what gets saved and sent), but hide it.
  store.hidden = true;
  store.computeSize = () => [0, -4];

  const read = () => {
    try {
      const v = JSON.parse(store.value || "[]");
      return Array.isArray(v) ? v : v.items || [];
    } catch {
      return [];
    }
  };
  const write = (items) => {
    store.value = JSON.stringify(items);
    store.callback?.(store.value);
    render();
    node.setDirtyCanvas(true, true);
  };

  const root = document.createElement("div");
  root.className = "h3g";
  const bar = document.createElement("div");
  bar.className = "h3g-bar";
  const add = document.createElement("button");
  add.textContent = "+ Add references";
  const clear = document.createElement("button");
  clear.textContent = "Clear";
  const count = document.createElement("span");
  count.className = "h3g-count";
  bar.append(add, clear, count);
  const grid = document.createElement("div");
  grid.className = "h3g-grid";
  root.append(bar, grid);

  const picker = document.createElement("input");
  picker.type = "file";
  picker.multiple = true;
  picker.accept = "image/*,video/*,audio/*";
  picker.style.display = "none";
  root.appendChild(picker);

  async function addFiles(files) {
    const list = [...files].filter((f) => KIND(f.name));
    if (!list.length) return;
    count.textContent = `uploading ${list.length}…`;
    const items = read();
    for (const f of list) {
      try {
        items.push(await upload(f));
      } catch (e) {
        console.error("[H3 Reference Gallery]", e);
        alertMsg(String(e.message || e));
      }
    }
    write(items);
  }
  function alertMsg(text) {
    app.extensionManager?.toast?.add?.({ severity: "error", summary: "H3 Reference Gallery", detail: text, life: 6000 });
  }

  add.onclick = () => picker.click();
  picker.onchange = () => {
    addFiles(picker.files);
    picker.value = "";
  };
  clear.onclick = () => write([]);

  grid.addEventListener("dragover", (e) => {
    if ([...(e.dataTransfer?.types || [])].includes("Files")) {
      e.preventDefault();
      e.stopPropagation();
      grid.classList.add("drag");
    }
  });
  grid.addEventListener("dragleave", () => grid.classList.remove("drag"));
  grid.addEventListener("drop", (e) => {
    grid.classList.remove("drag");
    if (e.dataTransfer?.files?.length) {
      e.preventDefault();
      e.stopPropagation(); // do not let ComfyUI open the file as a workflow
      addFiles(e.dataTransfer.files);
    }
  });

  let dragIndex = null;
  function render() {
    const items = read();
    grid.replaceChildren();
    const n = { image: 0, video: 0, audio: 0 };
    let refIndex = 0; // reference position (#N) shared by images and videos, as in the node summary
    if (!items.length) {
      const empty = document.createElement("div");
      empty.className = "h3g-empty";
      empty.textContent = "Drop photos, videos or audio here";
      grid.appendChild(empty);
    }
    items.forEach((item, i) => {
      const kind = item.kind || KIND(item.name);
      if (item.enabled !== false) {
        n[kind] += 1;
        if (kind !== "audio") refIndex += 1;
      }
      const card = document.createElement("div");
      card.className = "h3g-card" + (item.enabled === false ? " off" : "");
      card.style.borderColor = COLORS[kind];
      card.draggable = true;

      let thumb;
      if (kind === "image") {
        thumb = document.createElement("img");
        thumb.src = viewUrl(item);
      } else if (kind === "video") {
        thumb = document.createElement("video");
        thumb.src = viewUrl(item);
        thumb.muted = true;
        thumb.loop = true;
        thumb.preload = "metadata";
        thumb.onmouseenter = () => thumb.play().catch(() => {});
        thumb.onmouseleave = () => thumb.pause();
      } else {
        thumb = document.createElement("div");
        thumb.className = "h3g-audio";
        thumb.textContent = "♪";
      }
      if (!thumb.className) thumb.className = "h3g-thumb";

      const x = document.createElement("button");
      x.className = "h3g-x";
      x.textContent = "×";
      x.title = "Remove (the file stays in input/refgallery)";
      x.onclick = () => write(read().filter((_, j) => j !== i));

      const on = document.createElement("input");
      on.type = "checkbox";
      on.className = "h3g-on";
      on.checked = item.enabled !== false;
      on.title = "Use this reference";
      on.onchange = () => write(read().map((it, j) => (j === i ? { ...it, enabled: on.checked } : it)));

      const meta = document.createElement("div");
      meta.className = "h3g-meta";
      const tag = document.createElement("div");
      tag.className = "h3g-tag";
      tag.style.color = COLORS[kind];
      tag.textContent = item.enabled === false ? `${kind} (off)` : kind === "audio" ? "audio" : `#${refIndex} ${kind}`;
      const name = document.createElement("div");
      name.className = "h3g-name";
      name.textContent = item.name;
      name.title = item.name;
      meta.append(tag, name);

      if (kind !== "image") {
        // Per-card trim; empty fields use the node's video_start / video_seconds.
        const trim = document.createElement("div");
        trim.className = "h3g-trim";
        for (const [key, label] of [["start", "start s"], ["seconds", "len s"]]) {
          const f = document.createElement("input");
          f.type = "number";
          f.min = "0";
          f.step = "0.1";
          f.placeholder = label;
          f.title = `${label} (empty = node default)`;
          f.value = item[key] ?? "";
          f.onpointerdown = (e) => e.stopPropagation();
          f.onchange = () =>
            write(read().map((it, j) => (j === i ? { ...it, [key]: f.value === "" ? null : Number(f.value) } : it)));
          trim.appendChild(f);
        }
        meta.appendChild(trim);
      }

      card.addEventListener("dragstart", (e) => {
        dragIndex = i;
        e.dataTransfer.effectAllowed = "move";
      });
      card.addEventListener("dragover", (e) => {
        if (dragIndex === null) return;
        e.preventDefault();
        card.classList.add("over");
      });
      card.addEventListener("dragleave", () => card.classList.remove("over"));
      card.addEventListener("drop", (e) => {
        card.classList.remove("over");
        if (dragIndex === null || dragIndex === i) return;
        e.preventDefault();
        e.stopPropagation();
        const list = read();
        const [moved] = list.splice(dragIndex, 1);
        list.splice(i, 0, moved);
        dragIndex = null;
        write(list);
      });
      card.addEventListener("dragend", () => (dragIndex = null));

      card.append(thumb, x, on, meta);
      grid.appendChild(card);
    });
    count.textContent = `${n.image} images | ${n.video} videos | ${n.audio} audio (external inputs follow)`;
  }

  node.addDOMWidget("references", "h3_gallery", root, { serialize: false, hideOnZoom: false });
  node.h3GalleryRender = render;
  render();
  const [w, h] = node.size;
  node.setSize([Math.max(w, 560), Math.max(h, 620)]);
}

app.registerExtension({
  name: "RICHIEPIC.H3.ReferenceGallery",
  async beforeRegisterNodeDef(nodeType, nodeData) {
    if (nodeData.name !== NODE) return;
    const created = nodeType.prototype.onNodeCreated;
    nodeType.prototype.onNodeCreated = function () {
      const r = created?.apply(this, arguments);
      setupNode(this);
      return r;
    };
    const configured = nodeType.prototype.onConfigure;
    nodeType.prototype.onConfigure = function () {
      const r = configured?.apply(this, arguments);
      this.h3GalleryRender?.(); // redraw cards after a saved workflow is loaded
      return r;
    };
  },
});

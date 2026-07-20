#!/usr/bin/env python3
"""Build the portfolio into a deployable dist/ folder.

Produces:
  dist/index.html   — a small HTML file (fonts + portrait inlined; those are tiny)
  dist/assets/…     — every project photo copied out as a real file, referenced
                      by a relative URL and lazy-loaded in the browser.

Why not one big self-contained file? Inlining ~30MB of photos as base64 makes a
~43MB HTML that the browser must download in full before it can show anything —
that's the 1-2 minute first load. With external + lazy-loaded images the HTML is
a couple hundred KB, paints instantly, and photos stream in on demand.

Deploy: push the CONTENTS of dist/ to your GitHub Pages repo (index.html and the
assets/ folder side by side).

Add / edit a project:
  1. Featured "Selected Work" -> projects/<order>-<slug>/
     Browse grid          -> categories/<order>-<slug>/
     Folders sort by name; the number prefix controls order.
  2. Drop a meta.json inside: {"title", "tag", "desc", "url"}.
  3. Drop images (jpg/png/webp…), named 01, 02, … for the order you want.
  4. Run: python3 build.py

Usage: python3 build.py
"""
import base64
import json
import mimetypes
import os
import shutil

HERE = os.path.dirname(os.path.abspath(__file__))
DIST = os.path.join(HERE, "dist")
ASSETS = os.path.join(DIST, "assets")
OUT = os.path.join(DIST, "index.html")
PROJECTS_DIR = os.path.join(HERE, "projects")
CATEGORIES_DIR = os.path.join(HERE, "categories")

IMAGE_EXTS = (".jpg", ".jpeg", ".png", ".webp", ".gif", ".avif")


def data_uri(path: str, mime: str | None = None) -> str:
    mime = mime or mimetypes.guess_type(path)[0] or "application/octet-stream"
    with open(path, "rb") as f:
        return f"data:{mime};base64," + base64.b64encode(f.read()).decode()


def emit_image(src: str, rel_dir: str) -> str:
    """Copy an image into dist/assets/<rel_dir>/ and return its relative URL."""
    out_dir = os.path.join(ASSETS, rel_dir)
    os.makedirs(out_dir, exist_ok=True)
    fn = os.path.basename(src)
    shutil.copy2(src, os.path.join(out_dir, fn))
    return f"assets/{rel_dir}/{fn}"


def load_project(folder: str, name: str, rel_dir: str,
                 require_images: bool = True) -> dict:
    """Read one project folder (meta.json + images) into a dict, copying its
    images out to dist/assets/<rel_dir>/. With require_images=False an empty
    folder is allowed (a placeholder like K Villas with no photos yet)."""
    meta_path = os.path.join(folder, "meta.json")
    if not os.path.exists(meta_path):
        raise SystemExit(f"{name}: missing meta.json")
    with open(meta_path, encoding="utf-8") as f:
        meta = json.load(f)

    for key in ("title", "tag", "desc", "url"):
        if key not in meta:
            raise SystemExit(f"{name}: meta.json is missing \"{key}\"")

    image_files = sorted(
        fn for fn in os.listdir(folder)
        if fn.lower().endswith(IMAGE_EXTS)
    )
    if not image_files and require_images:
        raise SystemExit(f"{name}: no images found in folder")

    images = [emit_image(os.path.join(folder, fn), rel_dir) for fn in image_files]
    return {
        "title": meta["title"],
        "tag": meta["tag"],
        "desc": meta["desc"],
        "url": meta["url"],
        "images": images,
    }


def load_projects() -> list[dict]:
    """Featured 'Selected Work' — one project per folder in projects/."""
    if not os.path.isdir(PROJECTS_DIR):
        raise SystemExit(f"No projects/ folder found at {PROJECTS_DIR}")

    projects: list[dict] = []
    for name in sorted(os.listdir(PROJECTS_DIR)):
        folder = os.path.join(PROJECTS_DIR, name)
        if not os.path.isdir(folder) or name.startswith("."):
            continue
        p = load_project(folder, name, f"featured/{name}", require_images=False)
        projects.append(p)
        n = len(p["images"])
        print(f"  + {name} ({n} image{'s' if n != 1 else ''})")

    if not projects:
        raise SystemExit("No projects found in projects/")
    return projects


def load_categories() -> list[dict]:
    """"Browse the projects" grid — one folder per project-category in
    categories/<NN-slug>/, each with a meta.json {title,tag,desc,url} and its
    images in filename order. A category may have no images yet (placeholder,
    shown as "Coming soon" and not clickable)."""
    if not os.path.isdir(CATEGORIES_DIR):
        return []

    categories: list[dict] = []
    for name in sorted(os.listdir(CATEGORIES_DIR)):
        folder = os.path.join(CATEGORIES_DIR, name)
        if not os.path.isdir(folder) or name.startswith("."):
            continue
        p = load_project(folder, f"categories/{name}", f"categories/{name}",
                          require_images=False)
        categories.append(p)
        n = len(p["images"])
        print(f"  # {p['title']}: {n} image{'s' if n != 1 else ''}"
              + ("  (empty placeholder)" if n == 0 else ""))

    return categories


def main() -> None:
    with open(os.path.join(HERE, "template.html"), encoding="utf-8") as f:
        tpl = f.read()

    # fresh dist/
    if os.path.exists(DIST):
        shutil.rmtree(DIST)
    os.makedirs(ASSETS, exist_ok=True)

    # fonts + portrait are tiny (~200KB total) → keep inline to avoid FOUT and
    # extra round-trips.
    tpl = tpl.replace("{{F_SYNE}}", data_uri(os.path.join(HERE, "fonts/Syne.woff2"), "font/woff2"))
    tpl = tpl.replace("{{F_INSTR}}", data_uri(os.path.join(HERE, "fonts/InstrumentSans.woff2"), "font/woff2"))
    tpl = tpl.replace("{{PORTRAIT}}", data_uri(os.path.join(HERE, "images/profile-photo.jpg")))

    print("Featured (Selected Work):")
    projects = load_projects()

    print("Categories:")
    categories = load_categories()

    # json.dumps produces a valid JS literal; ensure_ascii=False keeps the · etc.
    tpl = tpl.replace("{{PROJECTS}}", json.dumps(projects, ensure_ascii=False, indent=2))
    tpl = tpl.replace("{{PROJECT_COUNT}}", str(len(projects)).zfill(2))
    tpl = tpl.replace("{{CATEGORIES}}", json.dumps(categories, ensure_ascii=False, indent=2))
    tpl = tpl.replace("{{CATEGORY_COUNT}}", str(len(categories)).zfill(2))

    if "{{" in tpl:
        raise SystemExit("Unresolved {{...}} placeholders left in output")

    with open(OUT, "w", encoding="utf-8") as f:
        f.write(tpl)

    # GitHub Pages: skip Jekyll so nothing gets mangled.
    open(os.path.join(DIST, ".nojekyll"), "w").close()

    cat_imgs = sum(len(c["images"]) for c in categories)
    assets_bytes = sum(
        os.path.getsize(os.path.join(dp, f))
        for dp, _, fns in os.walk(ASSETS) for f in fns
    )
    print(f"OK {OUT} ({os.path.getsize(OUT) // 1024} KB HTML) + "
          f"assets/ ({assets_bytes // (1024 * 1024)} MB, "
          f"{len(projects)} featured, {len(categories)} categories, "
          f"{cat_imgs} category images)")
    print(f"Deploy: push the contents of {DIST}/ to your GitHub Pages repo.")


if __name__ == "__main__":
    main()

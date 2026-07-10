#!/usr/bin/env python3
"""Build viktoriia-portfolio.html from template.html.

Auto-discovers projects from the projects/ folder and inlines every asset
(fonts, portrait, project images) as base64 data URIs, so the output is a
single self-contained HTML file you can host anywhere.

Add a project:
  1. Make a new folder in projects/ named "<order>-<slug>", e.g. "07-my-work".
     Folders are sorted by name, so the number prefix controls display order.
  2. Drop a meta.json inside: {"title", "tag", "desc", "url"}.
  3. Drop the slide images inside (jpg/jpeg/png/webp). They are shown in
     filename order, so name them 01.jpg, 02.jpg, ... to control the sequence.
  4. Run: python3 build.py

Usage: python3 build.py
"""
import base64
import json
import mimetypes
import os

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "index.html")
PROJECTS_DIR = os.path.join(HERE, "projects")
CATEGORIES_DIR = os.path.join(HERE, "categories")

IMAGE_EXTS = (".jpg", ".jpeg", ".png", ".webp", ".gif", ".avif")


def data_uri(path: str, mime: str | None = None) -> str:
    mime = mime or mimetypes.guess_type(path)[0] or "application/octet-stream"
    with open(path, "rb") as f:
        return f"data:{mime};base64," + base64.b64encode(f.read()).decode()


def load_project(folder: str, name: str, require_images: bool = True) -> dict:
    """Read one project folder (meta.json + images) into a dict.
    With require_images=False an empty folder is allowed (e.g. a placeholder
    category like K Villas that has no photos yet)."""
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

    images = [data_uri(os.path.join(folder, fn)) for fn in image_files]
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
        p = load_project(folder, name, require_images=False)
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
        p = load_project(folder, f"categories/{name}", require_images=False)
        categories.append(p)
        n = len(p["images"])
        print(f"  # {p['title']}: {n} image{'s' if n != 1 else ''}"
              + ("  (empty placeholder)" if n == 0 else ""))

    return categories


def main() -> None:
    with open(os.path.join(HERE, "template.html"), encoding="utf-8") as f:
        tpl = f.read()

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
    cat_imgs = sum(len(c["images"]) for c in categories)
    print(f"OK {OUT} ({os.path.getsize(OUT)} bytes, {len(projects)} featured, "
          f"{len(categories)} categories, {cat_imgs} category images)")


if __name__ == "__main__":
    main()

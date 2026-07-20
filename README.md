# Viktoriia Moiseienko — Portfolio

Single-page portfolio site for graphic designer Viktoriia Moiseienko
(https://www.behance.net/viktoriiamoiseienko).

Live artifact: https://claude.ai/code/artifact/64a4e8e6-d55e-480c-8ba6-da9f8cf969ca

## Files

- `template.html` — the source page. Edit this one. Assets are referenced via
  placeholders (`{{F_SYNE}}`, `{{F_INSTR}}`, `{{PORTRAIT}}`, `{{PROJECTS}}`,
  `{{PROJECT_COUNT}}`, `{{CATEGORIES}}`, `{{CATEGORY_COUNT}}`) that `build.py`
  fills in.
- `projects/` — the **featured "Selected Work"** grid at the top: one folder per
  project (see below).
- `categories/` — the **"Browse the projects"** grid below Selected Work: one
  folder per project-category (see below). Each is a cover card that opens a
  full-screen gallery of all its images.
- `behance-downloads/` — the raw image pool pulled from Behance, kept in the
  original gallery order (one subfolder per gallery, images numbered `01`,
  `02`, …). This is the staging source: copy images from here into
  `categories/…/<project>/` when assigning photos to projects.
- `images/profile-photo.jpg` — the hero portrait. Swap the file (keep the name)
  and rebuild.
- `fonts/` — Syne and Instrument Sans (latin subsets, woff2, OFL-licensed).
- `build.py` — auto-discovers projects and builds the deployable `dist/` folder.
- `dist/` — the **built output** (generated; safe to delete, `build.py` recreates
  it). Contains `index.html` (~300KB, fonts + portrait inlined) and `assets/`
  (the photos, copied out as real files and lazy-loaded). This is what you deploy.

  > Photos are **external files**, not inlined. An earlier version base64-inlined
  > every image into one ~43MB HTML — that's why the live site took 1-2 minutes to
  > first load. External + lazy loading makes the HTML tiny and paints instantly;
  > photos stream in as you scroll / open a gallery.

## Projects

Each project is a folder in `projects/` named `<order>-<slug>`, e.g.
`01-devtalk`. Folders are sorted by name, so the **number prefix controls the
display order** — rename to reorder. Inside each folder:

- `meta.json` — `{ "title", "tag", "desc", "url" }`.
- image files (`.jpg`/`.png`/`.webp`…) — shown in **filename order**, so name
  them `01.jpg`, `02.jpg`, … to control the sequence. The first image is the
  card cover.

**To add a project:** make a new folder (e.g. `07-new-thing`), drop in a
`meta.json` and the images, then run `python3 build.py`. The card and the
"NN Projects" count update automatically.

## Categories (Browse the projects)

`categories/` holds the 8 project-categories shown as a 3-column cover grid
under Selected Work. Each is a folder `<order>-<slug>` (number prefix controls
order) with the **same shape as a `projects/` folder**:

- `meta.json` — `{ "title", "tag", "desc", "url" }`.
- image files in filename order (`01.jpg`, `02.jpg`, …). The **first image is
  the cover**; the rest open in order in the full-screen lightbox.

A category with **no images** renders as a "Coming soon" placeholder tile that
isn't clickable (that's how **K Villas** currently shows).

Current order: 1 The Seals · 2 Beso Academy · 3 DevTalk · 4 Grid Design ·
5 K Villas *(empty)* · 6 Natalia Getta Coaching · 7 Personal · 8 Stories.

**To fill / add a category:** create or edit its folder, drop in `meta.json` +
images (copy from `behance-downloads/…`, keeping the Behance carousel order),
then `python3 build.py`. The count updates automatically.

## Build

```sh
python3 build.py
```

Rebuilds `dist/` from scratch each time.

## Deploy (GitHub Pages)

The live site is https://crlnshd.github.io/viktoriia-portfolio/ . Deploy the
**contents of `dist/`** (the `index.html`, the `assets/` folder, and `.nojekyll`)
to the repo/branch GitHub Pages serves. In a clone of that repo:

```sh
python3 build.py                     # regenerate dist/
rm -rf assets index.html .nojekyll   # clear the old build at the repo root
cp -R dist/. .                       # copy the new build in (note the trailing /.)
git add -A && git commit -m "Update site" && git push
```

(Adjust if Pages serves from `/docs` or the `gh-pages` branch instead of the
repo root — copy `dist/`'s contents into that location instead.)

## TODO / placeholders

- Contact section: the email and Telegram username in `template.html` are the
  designer's real contacts — update there if they change, then rebuild.
- Everything else (project data, order, portrait) is now data-driven from
  `projects/` and `images/profile-photo.jpg` — no HTML editing needed.

Note: the built page is wrapped in a proper `<!doctype html><head>...` skeleton
by the artifact host. If you host it elsewhere, you may want to add
`<!doctype html>` and `<html lang="en">` at the top yourself.

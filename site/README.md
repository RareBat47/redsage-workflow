# RedSage v2 — Landing Page

A simple, static landing page (HTML + CSS only, no build tools, no images
required). All diagrams are inline SVG, so the page is fully self-contained.

## Files

| File | Purpose |
|---|---|
| `index.html` | Landing page: hero, how-it-works diagram, differentiators, safety diagram, architecture diagram, outputs, contact |
| `style.css` | Dark theme matching the app (`#101415` / `#72e0ba`) |
| `assets/` | Empty — reserved for future use; the page needs nothing from it |
| `.nojekyll` | Tells GitHub Pages to serve files as-is |

## Preview locally

**Option 1 — open directly.**
Double-click `index.html` (or drag it into a browser). Everything works from
the file system because the diagrams are inline and `style.css` is relative.

**Option 2 — local server.**
From this `site/` folder:

```powershell
python -m http.server 5179
```

Then open http://127.0.0.1:5179.

## Edit points

- **Copy:** all text lives in `index.html`; colors live once in `:root` at
  the top of `style.css`.
- **GitHub link:** already points to `RareBat47/redsage-workflow`.
  with the real repository URL.
- **Demo email:** replace the `hello@redsage.example` placeholder in the
  contact section.
- **Diagrams:** plain inline SVG (boxes + arrows) inside `index.html` —
  edit the `<text>` values directly; the `viewBox` keeps them responsive.

## Publish with GitHub Pages

1. Commit the `site/` folder to the `main` branch.
2. Repository **Settings → Pages**.
3. Source: **Deploy from a branch** → Branch: **main** → Folder: **/site**.
4. Save. Live at `https://<username>.github.io/<repo>/` in a minute or two.

## What is intentionally not here

No secrets (`.env`), no databases, no evidence artifacts, no application
data, and no screenshots — the page is diagrams-only by design.

# Chef Tash House website

A single-page static site for Chef Tash House, structured like a keepsake booklet: a pink cover, a short hello, sideways-scrolling collections of recent tables and weekly meal prep, a quiet list of services, and a brown back-cover invitation. No build step is required for the site.

## Live site

[https://cheftashhouse.com/](https://cheftashhouse.com/)

Hosted with GitHub Pages directly from the `main` branch. Push changes to `main` to publish updates automatically.

## Preview

Double-click `index.html`, or run a small local server from this folder:

```bash
python3 -m http.server 8000
```

Then visit `http://localhost:8000`.

## Before publishing

- "Menus and pricing: just ask" in the services list — replace with real pricing wording if desired

## Content worth adding next (highest value first)

1. A real client testimonial with permission to name them (a quiet single quote would fit after the tables)
2. A booking or contact form link (Google Form, Formspree, HoneyBook) if email alone isn't enough
3. Matching food photos for the 60th birthday, bachelorette, and Valentine&rsquo;s menus (none are present in the current source library)

## Files

- `index.html` — all page content and structure
- `styles.css` — colors, typography, layout, scalloped dividers, and mobile styles
- `script.js` — current year, scroll-in reveal, and the modal image gallery
- `assets/tash-main-framed.webp` — cover portrait with its brush-shaped transparency baked in for reliable local previews
- `assets/hero-mask.png` and `assets/hero-outline.png` — reusable pink brush treatment around the portrait
- `assets/chili.png` — favicon and floating chili decoration
- `assets/instagram.png` — footer Instagram mark
- `assets/social-preview-20260719.jpg` — 1200×630 Open Graph link preview on the brand pink background
- `assets/menus/` — web-ready menus and event photos in "from recent tables"
- `assets/meal-prep/` — lightweight photos used in the meal-prep slider
- `assets/gallery/` — higher-resolution derivatives loaded only when the modal gallery opens
- `assets/asset-manifest.json` — source-to-web filename map, section, output settings, and alt text
- `scripts/assets.py` — source-library audit and WebP generator
- `resume/` — public `/resume/` viewer and downloadable resume PDF

To add a menu group to the strip, add its web images to `assets/menus/`, then copy one `.menu-group` block in `index.html` and update the filenames, alt text, and caption. Use `.menu-group--paired` when a menu has matching food photos and `.menu-group--solo` when it does not.

## Updating the photo library

`assets/assets-source/` is the local working library copied from the client&rsquo;s drive. It is intentionally gitignored: GitHub Pages would otherwise publish every raw image and its metadata. The optimized, metadata-free WebPs and their manifest are tracked instead.

After replacing or adding to the source folder:

```bash
python3 -m pip install -r requirements-assets.txt  # first time only
python3 scripts/assets.py audit
```

The audit reports new/unmapped files, missing files, exact source duplicates, and source-to-published visual matches. Add approved images to `assets/asset-manifest.json` with a readable output name, section, and alt text, then run. The script creates both lightweight page images and high-resolution modal-gallery derivatives; on macOS it also converts HEIC sources through `sips`.

```bash
python3 scripts/assets.py sync                 # generate missing derivatives
python3 scripts/assets.py audit --verbose     # verify every relationship
```

Existing derivatives are left untouched by default. After reviewing an intentionally replaced source image, regenerate its manifest section with `python3 scripts/assets.py sync --force --section meal-prep` (or the relevant section).

Current source review: all existing event images have published derivatives and ten meal-prep images are in use. `charcuterie board.JPG` is held for a future curated-food update, while `IG LINK.png` is intentionally ignored. There are no exact duplicates and no additional event photos available for the three menu-only groups.

The site uses Google Fonts (`Labrada` and `DM Sans`). If it must work fully offline, download those font files and update the font declarations in `styles.css`.

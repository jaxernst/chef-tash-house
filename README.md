# Chef Tash House website

A single-page static site for Chef Tash House, structured like a keepsake booklet: a pink cover, a two-line hello that leads straight into a sideways-scrolling strip of real menus from recent tables, a quiet list of services, and a brown back-cover invitation. No build tools required.

## Live site

[https://jaxernst.github.io/chef-tash-house/](https://jaxernst.github.io/chef-tash-house/)

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

1. More food photos for the "from recent tables" strip — especially ones matching the bbq, izakaya, and valentine's menus
2. A real client testimonial with permission to name them (a quiet single quote would fit after the tables)
3. An Instagram or booking link for the back cover
4. A contact form link (Google Form, Formspree, HoneyBook) if email alone isn't enough

## Files

- `index.html` — all page content and structure
- `styles.css` — colors, typography, layout, scalloped dividers, and mobile styles
- `script.js` — current year and the scroll-in reveal
- `assets/tash-table.jpg` — cover portrait (circular crop from the supplied concept artwork)
- `assets/chili.png` — favicon and floating chili decoration
- `assets/menus/` — menus and food photos shown in the "from recent tables" section, resized for web

To add a menu group to the strip: drop the images in `assets/menus/`, then copy one `.menu-group` block in `index.html` and update its filenames, alt text, and caption. Use `.menu-group--paired` when a menu has matching food photos and `.menu-group--solo` when it does not. Resize big phone photos first (`sips -Z 1400 file.jpg`) so the page stays fast.

The site uses Google Fonts (`Labrada` and `DM Sans`). If it must work fully offline, download those font files and update the font declarations in `styles.css`.

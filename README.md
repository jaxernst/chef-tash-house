# Chef Tash House website

A single-page static site for Chef Tash House, structured like a keepsake booklet: a pink cover, a two-line hello with an expandable full bio, a sideways-scrolling strip of real menus from recent tables, a quiet list of services, and a brown back-cover invitation. No build tools required.

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

- `hello@cheftashhouse.com` in `index.html` — confirm or replace the contact email (it appears once, marked with an HTML comment)
- "Menus and pricing: just ask" in the services list — replace with real pricing wording if desired

## Content worth adding next (highest value first)

1. Food photos from the four menus shown in "from recent tables" — each row is built to hold a photo beside its menu, and the "photos are on their way" note comes out once they're in
2. A real client testimonial with permission to name them (a quiet single quote would fit after the tables)
3. An Instagram or booking link for the back cover
4. A contact form link (Google Form, Formspree, HoneyBook) if email alone isn't enough

## Files

- `index.html` — all page content and structure
- `styles.css` — colors, typography, layout, scalloped dividers, and mobile styles
- `script.js` — current year and the scroll-in reveal
- `assets/tash-table.jpg` — cover portrait (circular crop from the supplied concept artwork)
- `assets/menus/` — sample menus shown in the "from recent tables" section, resized for web

To add a menu or a food photo to the strip: drop the image in `assets/menus/`, then copy one `<li>` block inside `.menu-strip` in `index.html` and update the filename, alt text, and caption. Photos and menus can be interleaved in the same strip; once real food photos are in, delete the "photos from these tables are on their way" line.

The site uses Google Fonts (`Labrada` and `DM Sans`). If it must work fully offline, download those font files and update the font declarations in `styles.css`.

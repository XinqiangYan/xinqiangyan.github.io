# Yan Lab website

Website for Yan Lab (MRI RF engineering, Vanderbilt University Medical Center). It is built with [Hugo](https://gohugo.io) (extended, v0.135+) using a custom theme in `layouts/` and `assets/`, with no external theme modules. Pushing to `main` deploys to GitHub Pages through `.github/workflows/publish.yaml`.

## Preview locally

```bash
hugo server
# open http://localhost:1313
```

## Where to edit things

| What | File(s) |
| --- | --- |
| Site title, emails, address, Google Scholar link, hero and team photos | `config/_default/hugo.yaml` (`params`) |
| Navigation menu | `config/_default/hugo.yaml` (`menus`) |
| Home page layout and headline copy | `layouts/index.html` |
| Research areas (home and Research page) | `data/research.yaml` |
| Research page text | `content/research/_index.md` |
| **Publications** | `data/publications.yaml` |
| **Products** | `content/products/<product>/index.md` |
| People | `content/people/<name>/index.md` and `avatar.png` |
| News | `content/news/<post>/index.md` (+ optional `featured.jpg`) |
| Contact page | `content/contact/index.md` |
| Colors, fonts, spacing | `assets/css/main.css` (variables at the top) |

### Add a product

Create `content/products/my-coil/index.md`:

```yaml
---
title: My New Coil
summary: One-sentence description shown on cards.
category: Human imaging        # used for the filter buttons
field_strengths: [3T, 7T]
status: Accepting inquiries    # or "In development", "Available", ...
featured: true                 # show on the home page (first 3 by weight)
weight: 70                     # sort order
image: media/my-photo.jpg      # file in assets/media/, or put featured.jpg in the folder
image_fit: contain             # optional: don't crop (good for figures with labels)
art: array                     # used if there is no image: array | flex | birdcage | shim | animal
highlights:
  - Key feature one
specs:
  - { label: Channels, value: "32" }
applications: [Neuro, Research]
publications:                  # exact titles from data/publications.yaml
  - "Self-decoupled radiofrequency coils for magnetic resonance imaging"
datasheet: /files/my-coil.pdf  # optional, put the PDF in static/files/
---

Longer description in Markdown.
```

### Add a publication

Add an entry at any position in `data/publications.yaml` (the list is sorted by year automatically):

```yaml
- title: "Paper title"
  authors: "Yan X, Coauthor A"
  venue: "Magnetic Resonance in Medicine"
  details: "91(2):123-135"
  year: 2025
  type: journal          # journal | conference | patent | preprint
  doi: 10.1002/mrm.xxxxx
  featured: true         # also show on the home page
```

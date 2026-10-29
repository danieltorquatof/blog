# DT's Blog

Personal blog of Daniel Torquato, built with [Quarto](https://quarto.org) and published to GitHub Pages at <https://blog.danieltorquatof.spikeystudio.com/>.

## Development

The project uses [uv](https://docs.astral.sh/uv/) (Python 3.13). Quarto itself comes from the `quarto-cli` dev dependency, so no separate install is needed.

```bash
uv sync
uv run quarto preview
uv run quarto render
```

Publishing runs on GitHub Actions (`.github/workflows/publish.yml`) when a `v*` tag is pushed.

## Writing a post

Each post lives in its own folder, named after its **keyword slug** (the public URL):

```
posts/<keyword-slug>/index.qmd   ->  /posts/<keyword-slug>/
```

Give it a `uuid` in the front matter: `/posts/<uuid>/` becomes a permanent short link that redirects to the slug URL. The same applies to projects, articles and achievements.

```yaml
---
title: "..."
subtitle: "..."
description: "..."   # used by Google and social previews; aim for 120–160 characters
date: 2026-01-31     # ISO format
uuid: 00000000-0000-0000-0000-000000000000
categories:
  - ...
draft: false         # every section defaults to draft: true
---
```

Set `image:` only to override the generated social preview card.

## SEO build scripts

- `utils/og_images.py` (pre-render): generates the 1200x630 social preview cards (`*og-image.png`, git-ignored).
- `utils/seo_postrender.py` (post-render): adds JSON-LD, `og:url` and the per-page cards, cleans canonical/sitemap URLs, writes the UUID short links and removes the empty draft outputs.

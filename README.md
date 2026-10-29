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

### Updating a post

Edit the post in place: it keeps its URL, ranking and shared links.

1. Add `date-modified: YYYY-MM-DD` to the front matter (shown as "Modified", used in the JSON-LD `dateModified`). Keep `date` as the original publication date.
2. Add a short note at the top describing what changed:

   ```markdown
   ::: {.callout-note}
   ## Updated on October 22, 2026

   What changed and why, with links to the PR or commit.
   :::
   ```

3. Add an entry to the `## Revision history` section at the end (create it on the first update).
4. When quoting code from another repository, link it to a commit permalink (`.../blob/<sha>/path`) so the excerpt never drifts silently.

## Projects

A project lives in `projects/<keyword-slug>/index.qmd` and follows the post front matter, plus:

```yaml
date: 2025-12-04           # project start
date-modified: 2026-10-22  # last update (the listing is sorted by it)
status: maintained         # required, see below
repository: https://github.com/<owner>/<repo>
code-license: MIT          # code license (`license` is reserved by Quarto for the page content)
languages: [Bash, Dockerfile]
```

| Status | Meaning |
| --- | --- |
| `planned` | Idea or design, no usable code yet |
| `experimental` | Prototype or proof of concept |
| `active` | Under active development |
| `maintained` | Stable, receiving fixes and updates |
| `paused` | On hold, may resume |
| `completed` | Done; no further work planned |
| `deprecated` | Superseded or no longer recommended |
| `archived` | Read-only, kept for reference |

The build fails when a published project has no valid `status`. The status appears as a badge in the title block, in the projects listing (filterable) and on the social preview card. Record each release in the project's `## Updates` table, and update the related posts as described above.

## SEO build scripts

- `utils/og_images.py` (pre-render): generates the 1200x630 social preview cards (`*og-image.png`, git-ignored).
- `utils/seo_postrender.py` (post-render): adds JSON-LD, `og:url` and the per-page cards, cleans canonical/sitemap URLs, writes the UUID short links and removes the empty draft outputs.

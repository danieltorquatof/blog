"""Quarto pre-render script: generates the social preview cards (1200x630 PNG).

- assets/images/og-image.png: default card (website.image in _quarto.yml), used by the home page
- <page dir>/og-image.png (or <page>-og-image.png): one card per page without its own `image`;
  utils/seo_postrender.py publishes it and points og:image / twitter:image to it

Files are only rewritten when their content changes, so `quarto preview` does not loop.
"""

from io import BytesIO
from pathlib import Path
from typing import Any

from PIL import Image, ImageDraw, ImageFont
from site_pages import PROJECT_DIR, SOCIAL_CARD_SUFFIX, Page, discoverPages, loadSiteConfig, validateProjects

WIDTH: int = 1200
HEIGHT: int = 630
PADDING: int = 80

BACKGROUND: str = "#151515"
FOREGROUND: str = "#fafafa"
MUTED: str = "#b9b9b9"
ACCENT: str = "#ff7f00"

FONTS_DIR: Path = PROJECT_DIR / "utils" / "fonts"

DEFAULT_CARD: Path = PROJECT_DIR / "assets" / "images" / SOCIAL_CARD_SUFFIX

SECTION_LABELS: dict[str, str] = {
    "posts": "Post",
    "projects": "Project",
    "articles": "Article",
    "achievements": "Achievement",
    "aboutMe": "About me",
}


def font(weight: str, size: int) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(FONTS_DIR / f"Poppins-{weight}.ttf", size)


def wrapText(text: str, typeface: ImageFont.FreeTypeFont, maxWidth: int) -> list[str]:
    lines: list[str] = []
    current: str = ""

    for word in text.split():
        candidate: str = f"{current} {word}".strip()

        if typeface.getlength(candidate) <= maxWidth or not current:
            current = candidate
        else:
            lines.append(current)
            current = word

    if current:
        lines.append(current)

    return lines


def clampLines(lines: list[str], maxLines: int, typeface: ImageFont.FreeTypeFont, maxWidth: int) -> list[str]:
    if len(lines) <= maxLines:
        return lines

    clamped: list[str] = lines[:maxLines]
    last: str = clamped[-1]

    while last and typeface.getlength(f"{last}…") > maxWidth:
        last = last.rsplit(" ", 1)[0] if " " in last else last[:-1]

    clamped[-1] = f"{last}…"

    return clamped


def fitTitle(title: str, maxWidth: int) -> tuple[ImageFont.FreeTypeFont, list[str]]:
    for size in (68, 62, 56, 50, 46):
        typeface = font("SemiBold", size)
        lines = wrapText(title, typeface, maxWidth)

        if len(lines) <= 3:
            return typeface, lines

    return typeface, clampLines(lines, 4, typeface, maxWidth)


def renderCard(label: str, title: str, subtitle: str | None, footerNote: str | None, domain: str) -> bytes:
    image = Image.new("RGB", (WIDTH, HEIGHT), BACKGROUND)
    draw = ImageDraw.Draw(image)

    contentWidth: int = WIDTH - 2 * PADDING

    draw.rectangle((0, 0, 16, HEIGHT), fill=ACCENT)

    labelFont = font("SemiBold", 26)
    draw.text((PADDING, PADDING - 10), label.upper(), font=labelFont, fill=ACCENT)

    titleFont, titleLines = fitTitle(title, contentWidth)
    titleLineHeight: int = int(titleFont.size * 1.2)

    y: int = PADDING + 60

    for line in titleLines:
        draw.text((PADDING, y), line, font=titleFont, fill=FOREGROUND)
        y += titleLineHeight

    if subtitle:
        subtitleFont = font("Regular", 30)
        y += 16

        for line in clampLines(wrapText(subtitle, subtitleFont, contentWidth), 2, subtitleFont, contentWidth):
            draw.text((PADDING, y), line, font=subtitleFont, fill=MUTED)
            y += 42

    footerFont = font("Medium", 26)
    footerY: int = HEIGHT - PADDING - 10

    draw.line((PADDING, footerY - 28, WIDTH - PADDING, footerY - 28), fill="#414141", width=2)
    draw.text((PADDING, footerY), "Daniel Torquato", font=footerFont, fill=FOREGROUND)

    note: str = footerNote or domain
    noteFont = font("Regular", 24)
    noteLines = clampLines(wrapText(note, noteFont, contentWidth // 2), 1, noteFont, contentWidth // 2)
    draw.text((WIDTH - PADDING, footerY + 2), noteLines[0], font=noteFont, fill=MUTED, anchor="ra")

    buffer = BytesIO()
    image.save(buffer, format="PNG", optimize=True)

    return buffer.getvalue()


def writeIfChanged(path: Path, data: bytes) -> bool:
    if path.exists() and path.read_bytes() == data:
        return False

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(data)

    return True


def pageLabel(page: Page, siteTitle: str) -> str:
    parts: tuple[str, ...] = page.relativeSource.parts
    section: str = parts[0] if len(parts) > 1 else ""

    if section in SECTION_LABELS and page.relativeSource.name == "index.qmd" and len(parts) == 2:
        return siteTitle

    label: str = SECTION_LABELS.get(section, siteTitle)

    return f"{label} · {page.projectStatus}" if page.projectStatus else label


def main() -> None:
    website: dict[str, Any] = loadSiteConfig()["website"]
    siteTitle: str = website.get("navbar", {}).get("title") or website["title"]
    domain: str = website["site-url"].split("://", 1)[-1].rstrip("/")

    pages: list[Page] = discoverPages()
    validateProjects(pages)

    generated: int = 0

    generated += writeIfChanged(
        DEFAULT_CARD,
        renderCard(siteTitle, website["title"], "Software Engineering, AI & Systems Design", None, domain),
    )

    for page in pages:
        if not page.usesGeneratedCard:
            continue

        categories: list[str] = [str(category) for category in page.meta.get("categories") or []]

        card: bytes = renderCard(
            label=pageLabel(page, siteTitle),
            title=str(page.meta.get("title", website["title"])),
            subtitle=page.meta.get("subtitle") or page.meta.get("description"),
            footerNote=" · ".join(categories[:3]) or None,
            domain=domain,
        )

        generated += writeIfChanged(PROJECT_DIR / page.socialCard, card)

    print(f"og_images: {generated} social preview card(s) updated")


if __name__ == "__main__":
    main()

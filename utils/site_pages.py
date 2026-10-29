"""Discovers the site's .qmd pages and resolves their metadata the way Quarto does.

Shared by the pre/post-render scripts (utils/og_images.py, utils/seo_postrender.py).
Quarto runs those scripts from the project root.
"""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml

PROJECT_DIR: Path = Path.cwd()

IGNORED_DIRS: set[str] = {".git", ".github", ".quarto", ".venv", "_freeze", "_site", "utils"}

SOCIAL_CARD_SUFFIX: str = "og-image.png"

# Pages that use the default card (website.image) instead of a generated one
DEFAULT_CARD_PAGES: set[str] = {"index.qmd", "404.qmd"}

# Lifecycle of a project page (`status:` in projects/<slug>/index.qmd) and its display label
PROJECT_STATUSES: dict[str, str] = {
    "planned": "Planned",
    "experimental": "Experimental",
    "active": "Active",
    "maintained": "Maintained",
    "paused": "Paused",
    "completed": "Completed",
    "deprecated": "Deprecated",
    "archived": "Archived",
}


@dataclass
class Page:
    source: Path
    meta: dict[str, Any] = field(default_factory=dict)

    @property
    def relativeSource(self) -> Path:
        return self.source.relative_to(PROJECT_DIR)

    @property
    def outputPath(self) -> Path:
        """Output file relative to the output dir (e.g. posts/foo/index.html)."""
        return self.relativeSource.with_suffix(".html")

    @property
    def urlPath(self) -> str:
        """Clean URL path relative to the site root (e.g. posts/foo/)."""
        path: str = self.outputPath.as_posix()

        if path == "index.html":
            return ""

        return path.removesuffix("index.html")

    @property
    def isDraft(self) -> bool:
        return bool(self.meta.get("draft", False))

    @property
    def isProject(self) -> bool:
        """A project page (projects/<slug>/...), not the projects listing."""
        parts: tuple[str, ...] = self.relativeSource.parts

        return parts[0] == "projects" and len(parts) > 2

    @property
    def projectStatus(self) -> str | None:
        status: Any = self.meta.get("status")

        return PROJECT_STATUSES.get(str(status)) if self.isProject and status else None

    @property
    def socialCard(self) -> Path:
        """Generated preview card, relative to the project (and output) dir."""
        name: str = SOCIAL_CARD_SUFFIX if self.source.name == "index.qmd" else f"{self.source.stem}-{SOCIAL_CARD_SUFFIX}"

        return self.relativeSource.parent / name

    @property
    def usesGeneratedCard(self) -> bool:
        """True unless the page sets its own image or is meant to use the default card."""
        if self.isDraft or self.relativeSource.as_posix() in DEFAULT_CARD_PAGES:
            return False

        ownImages: list[Any] = [
            self.meta.get("image"),
            *(self.meta.get(key, {}).get("image") for key in ("open-graph", "twitter-card") if isinstance(self.meta.get(key), dict)),
        ]

        return not any(ownImages)


def readFrontMatter(path: Path) -> dict[str, Any]:
    text: str = path.read_text(encoding="utf-8")

    if not text.startswith("---"):
        return {}

    end: int = text.find("\n---", 3)

    if end == -1:
        return {}

    return yaml.safe_load(text[3:end]) or {}


def readDirectoryMetadata(directory: Path) -> dict[str, Any]:
    metadataFile: Path = directory / "_metadata.yml"

    if not metadataFile.exists():
        return {}

    return yaml.safe_load(metadataFile.read_text(encoding="utf-8")) or {}


def mergeMetadata(base: dict[str, Any], override: dict[str, Any]) -> dict[str, Any]:
    merged: dict[str, Any] = dict(base)

    for key, value in override.items():
        if isinstance(value, dict) and isinstance(merged.get(key), dict):
            merged[key] = mergeMetadata(merged[key], value)
        else:
            merged[key] = value

    return merged


def resolveMetadata(source: Path) -> dict[str, Any]:
    """_metadata.yml files from the project root down to the page, then its front matter."""
    meta: dict[str, Any] = {}

    directory: Path = source.parent
    chain: list[Path] = [directory, *directory.parents]

    for parent in reversed(chain):
        if parent == PROJECT_DIR or PROJECT_DIR in parent.parents:
            meta = mergeMetadata(meta, readDirectoryMetadata(parent))

    return mergeMetadata(meta, readFrontMatter(source))


def loadSiteConfig() -> dict[str, Any]:
    return yaml.safe_load((PROJECT_DIR / "_quarto.yml").read_text(encoding="utf-8"))


def validateProjects(pages: list[Page]) -> None:
    """Fails the build when a published project has no valid `status`."""
    errors: list[str] = [
        f"{page.relativeSource}: status {page.meta.get('status')!r} is not one of {', '.join(PROJECT_STATUSES)}"
        for page in pages
        if page.isProject and not page.isDraft and page.projectStatus is None
    ]

    if errors:
        raise SystemExit("Invalid project metadata:\n  " + "\n  ".join(errors))


def discoverPages() -> list[Page]:
    pages: list[Page] = []

    for source in sorted(PROJECT_DIR.rglob("*.qmd")):
        relative: Path = source.relative_to(PROJECT_DIR)

        if any(part in IGNORED_DIRS or part.startswith("_") for part in relative.parts):
            continue

        pages.append(Page(source=source, meta=resolveMetadata(source)))

    return pages

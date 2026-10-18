"""Compose vector PDF blocks into the remaining printable space on uniform pages."""

from __future__ import annotations

from io import BytesIO
from typing import TYPE_CHECKING, Self

from matplotlib.colors import to_rgb
from pypdf import PdfReader, PdfWriter, Transformation
from pypdf.generic import ContentStream

if TYPE_CHECKING:
    from pathlib import Path

    from pypdf import PageObject


class _PageComposer:
    """Place ordered PDF blocks top to bottom, advancing only when necessary.

    Dimensions are in points internally. Small visuals keep their native scale;
    oversized blocks shrink only enough to fit a fresh page, never merely to
    squeeze into an occupied page's remaining space. Source readers remain open
    until writing completes so vector resources and fonts remain available.
    """

    def __init__(
        self, figsize: tuple[float, float], margin: float, background: str, title: str
    ) -> None:
        self.width, self.height = (dimension * 72 for dimension in figsize)
        self.margin = margin * 72
        self.content_width = self.width - 2 * self.margin
        self.content_height = self.height - 2 * self.margin
        self._background = to_rgb(background)
        self._writer = PdfWriter()
        self._writer.add_metadata({"/Title": title})
        self._readers: list[PdfReader] = []
        self._page: PageObject | None = None
        self._cursor = self.height - self.margin
        self._break_requested = False

    def __enter__(self) -> Self:
        """Keep source resources alive throughout composition and writing."""
        return self

    def __exit__(self, *_: object) -> None:
        """Release in-memory PDF resources, including after failed exports."""
        self._writer.close()
        for reader in self._readers:
            reader.stream.close()

    @property
    def remaining_height(self) -> float:
        """Printable height left after preceding content and its spacing."""
        if self._break_requested:
            return 0
        return max(0, self._cursor - self.margin)

    def new_page(self) -> PageObject:
        """Start a themed paper sheet and reset the vertical cursor."""
        page = self._writer.add_blank_page(width=self.width, height=self.height)
        red, green, blue = self._background
        backdrop = ContentStream(None, self._writer)
        backdrop.set_data(
            f"q {red} {green} {blue} rg 0 0 {self.width} {self.height} re f Q\n".encode(
                "ascii"
            )
        )
        page.replace_contents(backdrop)
        self._page = page
        self._cursor = self.height - self.margin
        self._break_requested = False
        return page

    def request_break(self) -> None:
        """Advance before the next content block without creating empty pages."""
        if self._page is not None:
            self._break_requested = True

    def add_pdf(self, data: bytes) -> None:
        """Place each native PDF page as a vector block with 12-point spacing."""
        reader = PdfReader(BytesIO(data))
        self._readers.append(reader)
        for source in reader.pages:
            width = float(source.mediabox.width)
            height = float(source.mediabox.height)
            scale = min(1, self.content_width / width, self.content_height / height)
            placed_height = height * scale
            if self._page is None or placed_height > self.remaining_height + 1e-6:
                page = self.new_page()
            else:
                page = self._page
            left = (self.width - width * scale) / 2
            bottom = self._cursor - placed_height
            transform = (
                Transformation()
                .translate(-float(source.mediabox.left), -float(source.mediabox.bottom))
                .scale(scale)
                .translate(left, bottom)
            )
            page.merge_transformed_page(source, transform)
            self._cursor = bottom - 12

    def save(self, path: str | Path) -> None:
        """Write the composed pages while preserving searchable vector content."""
        self._writer.write(path)

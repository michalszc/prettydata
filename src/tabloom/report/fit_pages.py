"""Fit native matplotlib PDF pages onto a consistent paper size without rasterizing."""

from __future__ import annotations

from math import isclose
from typing import TYPE_CHECKING

from matplotlib.colors import to_rgb
from pypdf import PdfReader, PdfWriter, Transformation
from pypdf.generic import ContentStream

if TYPE_CHECKING:
    from io import BytesIO
    from pathlib import Path


def _fit_pages(
    source: BytesIO,
    path: str | Path,
    *,
    figsize: tuple[float, float],
    margin: float,
    background: str,
) -> None:
    """Write uniform pages while preserving vector graphics and searchable text.

    Args:
        source: Matplotlib-produced PDF containing native-sized visual pages.
        path: Destination PDF filename.
        figsize: Common paper width and height in inches.
        margin: Minimum printable margin in inches around fitted visuals.
        background: Report theme color used outside the original visual.

    Pages already matching the target paper size are retained unchanged. Other
    pages are reduced uniformly when needed, centered horizontally, and aligned
    to the top margin. Matplotlib figures are never resized, copied, or modified.
    """
    source.seek(0)
    reader = PdfReader(source)
    writer = PdfWriter()
    width, height = (dimension * 72 for dimension in figsize)
    padding = margin * 72
    red, green, blue = to_rgb(background)
    for original in reader.pages:
        original_width = float(original.mediabox.width)
        original_height = float(original.mediabox.height)
        if isclose(original_width, width) and isclose(original_height, height):
            writer.add_page(original)
            continue
        page = writer.add_blank_page(width=width, height=height)
        backdrop = ContentStream(None, writer)
        backdrop.set_data(
            f"q {red} {green} {blue} rg 0 0 {width} {height} re f Q\n".encode("ascii")
        )
        page.replace_contents(backdrop)
        scale = min(
            1.0,
            (width - 2 * padding) / original_width,
            (height - 2 * padding) / original_height,
        )
        left = (width - original_width * scale) / 2
        bottom = height - padding - original_height * scale
        transform = (
            Transformation()
            .translate(-float(original.mediabox.left), -float(original.mediabox.bottom))
            .scale(scale)
            .translate(left, bottom)
        )
        page.merge_transformed_page(original, transform)
    if reader.metadata is not None:
        writer.add_metadata({key: str(value) for key, value in reader.metadata.items()})
    writer.write(path)

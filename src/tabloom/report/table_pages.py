"""Paginate measured table rows while reusing the Table renderer and styling."""

from __future__ import annotations

from io import BytesIO
from typing import TYPE_CHECKING, Literal

import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages

if TYPE_CHECKING:
    from tabloom.report.page_composer import _PageComposer
    from tabloom.table import Table
    from tabloom.table.layout import _TableLayout


class _TablePages:
    """Place complete rows with repeated headers and stable column proportions."""

    def __init__(
        self,
        table: Table,
        composer: _PageComposer,
        resize: Literal["full", "original"] | float,
        *,
        paginate: bool,
    ) -> None:
        self.table = table
        self.composer = composer
        self.resize = resize
        self.paginate = paginate

    def _place(
        self,
        layout: _TableLayout,
        start: int = 0,
        stop: int | None = None,
        *,
        width: float | None = None,
    ) -> None:
        """Export one reused table rendering, closing only its temporary figure."""
        stop = len(layout.rows) - 1 if stop is None else stop
        size = None
        if width is not None:
            height = (
                layout.page_heights[0]
                + sum(layout.page_heights[start + 1 : stop + 1])
                + layout.page_padding
            )
            size = (width, height)
        fig, _ = self.table._render_layout(  # noqa: SLF001 - shared table renderer
            layout, start=start, stop=stop, figsize=size, exact=width is not None
        )
        try:
            with BytesIO() as buffer:
                with PdfPages(buffer) as pdf:
                    pdf.savefig(
                        fig,
                        bbox_inches=fig.bbox_inches if width is not None else "tight",
                        pad_inches=0 if width is not None else 0.15,
                    )
                self.composer.add_pdf(buffer.getvalue(), resize=self.resize)
        finally:
            plt.close(fig)

    def write(self) -> None:
        """Fill remaining space, then continue rows on fresh pages without captions.

        A single row taller than a fresh page is kept intact and fitted to it.
        Explicit whole-table sizing remains available with paginate=False.
        """
        layout = self.table._layout()  # noqa: SLF001 - measure all columns once
        count = len(layout.rows) - 1
        target = self.composer.target_width(layout.size[0] * 72, self.resize) / 72
        width = max(layout.size[0], target)
        scale = target / width
        if (
            not self.paginate
            or not layout.widths
            or count <= 1
            or layout.natural_height * scale * 72 <= self.composer.content_height
        ):
            self._place(layout)
            return
        start = 0
        while start < count:
            budget = (
                self.composer.remaining_height / (72 * scale)
                - layout.page_padding
                - layout.page_heights[0]
            )
            stop, height = start, 0.0
            while (
                stop < count and height + layout.page_heights[stop + 1] <= budget + 1e-6
            ):
                height += layout.page_heights[stop + 1]
                stop += 1
            if stop == start:
                if self.composer.remaining_height < self.composer.content_height - 1e-6:
                    self.composer.new_page()
                    continue
                stop += 1
            self._place(layout, start, stop, width=width)
            start = stop
            if start < count:
                self.composer.request_break()

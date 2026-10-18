"""Internal chart-kind annotation shared by factory and plot dispatch."""

from __future__ import annotations

from typing import Literal

_Kind = Literal["line", "bar", "scatter", "hist", "box", "pie"]

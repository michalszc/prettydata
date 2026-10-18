"""Create themed matplotlib charts from vectors, DataFrames, or Tabloom tables.

The public ``Chart`` class provides six chart factories and exposes its Figure
and Axes for advanced customization. Import it from ``tabloom`` or
``tabloom.chart``. Common factory options and type-specific methods are
documented below."""

from __future__ import annotations

from tabloom.chart.chart import Chart

__all__ = ["Chart"]

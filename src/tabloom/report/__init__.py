"""Compose text, tables, and charts into ordered multipage PDF reports.

The public ``Report`` class retains supplied visuals for reuse and manages
only its own temporary figures. Import it from ``tabloom`` or
``tabloom.report``. Constructor and composition methods are documented below."""

from __future__ import annotations

from tabloom.report.report import Report

__all__ = ["Report"]

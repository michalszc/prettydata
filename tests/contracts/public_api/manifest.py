"""Explicit v0.1.0 API expectations, independent of live implementation details.

Each signature records positional and keyword-only parameters with their defaults.
New optional parameters and exports are allowed; removing or changing existing
entries requires an intentional compatibility decision and manifest update.
"""

from inspect import Parameter

PUBLIC_EXPORTS = {
    "tabloom": {"Table", "Chart", "Report"},
    "tabloom.table": {"Table"},
    "tabloom.chart": {"Chart"},
    "tabloom.report": {"Report"},
}

REFERENCE_CLASSES = {
    "Table": ("table", "tables"),
    "Chart": ("chart", "charts"),
    "Report": ("report", "reports"),
}

REQUIRED = Parameter.empty
PUBLIC_SIGNATURES: dict[str, tuple[dict[str, object], dict[str, object]]] = {
    "Table": (
        {"data": None},
        {
            "columns": None,
            "title": None,
            "theme": "plain",
            "style": None,
            "figsize": None,
            "copy": True,
        },
    ),
    "Table.from_dataframe": ({"df": REQUIRED}, {}),
    "Table.add_row": ({"row": REQUIRED}, {}),
    "Table.add_rows": ({"rows": REQUIRED}, {}),
    "Table.add_column": ({"name": REQUIRED, "values": REQUIRED}, {}),
    "Table.update_row": ({"position": REQUIRED, "row": REQUIRED}, {}),
    "Table.remove_row": ({"position": REQUIRED}, {}),
    "Table.rename_column": ({"old": REQUIRED, "new": REQUIRED}, {}),
    "Table.to_dataframe": ({}, {"copy": True}),
    "Table.render": ({}, {"head": None, "tail": None}),
    "Table.show": ({}, {"head": None, "tail": None}),
    "Table.save": ({"path": REQUIRED}, {"dpi": 200}),
    "Chart": ({"fig": REQUIRED, "ax": REQUIRED}, {}),
    "Chart.scatter": (
        {"x": None, "y": None},
        {
            "hue": None,
            "colorbar": None,
            "colorbar_label": None,
            "trendline": False,
            "trendline_kwargs": None,
        },
    ),
    "Chart.show": ({}, {}),
    "Chart.save": ({"path": REQUIRED}, {"dpi": 200}),
    "Report": (
        {"title": None},
        {"theme": "blue", "figsize": (8.27, 11.69), "margin": 0.6},
    ),
    "Report.add_text": (
        {"text": REQUIRED},
        {
            "font_family": "DejaVu Sans",
            "font_size": 12,
            "font_weight": "normal",
            "font_style": "normal",
            "color": None,
            "align": "left",
            "line_spacing": 1.5,
            "space_after": 12,
        },
    ),
    "Report.add_table": ({"table": REQUIRED}, {"resize": "full", "paginate": True}),
    "Report.add_chart": ({"chart": REQUIRED}, {"resize": "full"}),
    "Report.add_page_break": ({}, {}),
    "Report.save": ({"path": REQUIRED}, {}),
    **{
        f"Table.from_{kind}": (
            {"path": REQUIRED},
            {"title": None, "theme": "plain", "style": None},
        )
        for kind in ("csv", "excel", "json")
    },
    **{
        f"Table.to_{kind}": ({"path": REQUIRED}, {})
        for kind in ("csv", "excel", "json")
    },
    **{f"Chart.{kind}": ({"x": None, "y": None}, {}) for kind in ("line", "bar")},
    **{f"Chart.{kind}": ({"x": None}, {}) for kind in ("hist", "box", "pie")},
}

FORWARDED_OPTIONS = {
    "Table.from_dataframe",
    "Table.from_csv",
    "Table.from_excel",
    "Table.from_json",
    "Table.to_csv",
    "Table.to_excel",
    "Table.to_json",
    "Table.save",
    "Chart.line",
    "Chart.bar",
    "Chart.scatter",
    "Chart.hist",
    "Chart.box",
    "Chart.pie",
    "Chart.save",
}

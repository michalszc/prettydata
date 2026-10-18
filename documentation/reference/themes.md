# Themes and Styling

All three primary classes accept a `theme` name. Themes define figure and cell
backgrounds, text colors, borders, and a matching chart palette. Styling applies
to Tabloom-owned figures without permanently changing matplotlib settings.

| Theme | Appearance |
| --- | --- |
| `plain` | Black text and borders, white cells, no alternating backgrounds; table default |
| `blue` | White background, dark blue headers, teal-led chart palette |
| `soft_blue` | Pale background, soft headers, restrained blue-led palette |
| `dark_blue` | Dark background, light text, and high-contrast series colors |

Table constructors and file loaders use `plain` by default. Charts and reports
continue to use `blue`. Selecting `theme="blue"` on a table preserves the
original colored styling.

Tables additionally accept a `style` mapping. Supported keys are
`header_background`, `header_color`, `row_colors`, `font_size`, `cell_alignment`,
and `column_widths`. See the [Table constructor](tables.md) for its contract and
the [theme guide](../guides/themes.md) for a complete example.

Charts accept `font_size`, `figsize`, and plotting options such as `color`,
`linewidth`, or `marker`; available options depend on the chart type. See
[Charts](charts.md). Report themes style page backgrounds and report text;
supplied tables and charts retain their own appearance. Use the same theme on
all objects for a uniform document.

Unknown theme names raise `ValueError`; unsupported style keys raise `TypeError`.
The theme configuration classes and palette registry are internal and are not
part of the supported public API.

# Saving Visual Output

## Save visual output

```python
from tabloom import Chart, Table

table = Table({"Model": ["A", "B"], "Score": [85, 92]}, title="Results")
chart = Chart.bar(data=table, x="Model", y="Score", title="Scores")
for extension in ("png", "pdf", "svg"):
    table.save(f"results.{extension}", dpi=200)
    chart.save(f"comparison.{extension}", dpi=200)
```

Save methods accept matplotlib savefig options such as `transparent=True`.
Output uses tight bounds by default. Parent directories must already exist.
Saving never forces interactive display. `table.show()` and `chart.show()` use
the active backend; use an interactive backend when opening graphical windows.

# Installation

Install Tabloom using Python 3.12 or newer:

```bash
python -m pip install tabloom
```

This installs pandas, matplotlib, openpyxl, and pypdf. Excel `.xlsx` reading and writing
work with the standard installation. pypdf preserves vector content when fitting
report pages to a consistent paper size. The distribution and import names are both
`tabloom`.

For optional Jupyter kernel and widget support:

```bash
python -m pip install "tabloom[example]"
```

Verify the installed package:

```python
import tabloom

print(tabloom.__version__)  # 0.1.0
```

For development tools, see
[CONTRIBUTING.md](https://github.com/michalszc/tabloom/blob/master/CONTRIBUTING.md).
Continue with the [quick start](quickstart.md).

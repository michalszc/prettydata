# Examples

Explore the notebooks below for examples of using Tabloom.

| Notebook | What it demonstrates | Links |
| --- | --- | --- |
| **Basic usage** | Table editing, themes, charts, and PDF reports | [![View on GitHub](https://img.shields.io/badge/View_on-GitHub-181717?logo=github)](https://github.com/michalszc/tabloom/blob/master/notebooks/basic_usage.ipynb) [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/michalszc/tabloom/blob/master/notebooks/basic_usage.ipynb) |
| **Wine quality report** | Download 1,599 rows and 12 columns, build plain tables, compare distributions, and export a complete data appendix | [![View on GitHub](https://img.shields.io/badge/View_on-GitHub-181717?logo=github)](https://github.com/michalszc/tabloom/blob/master/notebooks/wine_quality_report.ipynb) [![Open In Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/michalszc/tabloom/blob/master/notebooks/wine_quality_report.ipynb) |

The basic notebook explicitly selects `theme="blue"` to demonstrate colored
tables. The wine-quality notebook uses plain tables, a color-encoded scatter
plot with an association line, overlaid histograms, and grouped box plots.

The larger example downloads the red-wine CSV from the
[UCI Wine Quality dataset](https://archive.ics.uci.edu/dataset/186/wine+quality)
(Cortez et al., 2009; [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/)).
Internet access is needed for its first run; later runs reuse the local CSV.
It includes every observation in a landscape PDF appendix, explicitly splitting
the DataFrame into 32-row tables with repeated headers and row numbers. Report
keeps each supplied table intact; it does not split a giant table automatically.

Run notebooks from `notebooks/` to keep downloaded CSVs in its ignored `data/`
directory. The complete `outputs/` directory is ignored, covering any generated
format. Common data and image exports (including CSV, Excel, JSON, PDF, PNG,
and SVG) written beside notebooks are also ignored. The large example writes
its PDF and three PNG charts to `outputs/`. No dataset package or
additional dependencies are needed.

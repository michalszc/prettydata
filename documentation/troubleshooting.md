# Troubleshooting

## `ModuleNotFoundError: No module named 'prettydata'`

Activate the environment where PrettyData is installed. Install using that
environment's Python interpreter, then retry `import prettydata`:

```bash
python -m pip install prettydata
```

In a notebook, select the kernel belonging to the environment where you installed
PrettyData.

## Python version is unsupported

PrettyData requires Python 3.12 or newer. Check `python --version` in the same
environment used for installation and select a compatible interpreter.

## Feature troubleshooting

Table, chart, and report troubleshooting will be added with their implementations.
No feature APIs are available in this milestone. For contributor setup and checks,
see [CONTRIBUTING.md](https://github.com/michalszc/prettydata/blob/master/CONTRIBUTING.md).

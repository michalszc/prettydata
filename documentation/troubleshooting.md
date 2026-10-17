# Troubleshooting

## `ModuleNotFoundError: No module named 'tabloom'`

Activate the environment where Tabloom is installed. Install using that
environment's Python interpreter, then retry `import tabloom`:

```bash
python -m pip install tabloom
```

In a notebook, select the kernel belonging to the environment where you installed
Tabloom.

## Python version is unsupported

Tabloom requires Python 3.12 or newer. Check `python --version` in the same
environment used for installation and select a compatible interpreter.

## Feature troubleshooting

Table, chart, and report troubleshooting will be added with their implementations.
No feature APIs are available in this milestone. For contributor setup and checks,
see [CONTRIBUTING.md](https://github.com/michalszc/tabloom/blob/master/CONTRIBUTING.md).

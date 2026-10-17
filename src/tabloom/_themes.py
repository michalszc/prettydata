"""Small, immutable visual defaults shared by Tabloom objects."""

from dataclasses import dataclass


@dataclass(frozen=True)
class _Theme:
    background: str
    foreground: str
    muted: str
    grid: str
    header_background: str
    header_color: str
    rows: tuple[str, str]
    palette: tuple[str, ...]


_THEMES = {
    "default": _Theme(
        "#ffffff",
        "#243447",
        "#637487",
        "#dce3e9",
        "#244c66",
        "#ffffff",
        ("#ffffff", "#f1f5f8"),
        ("#287c8e", "#dc8853", "#698554", "#8875a9", "#bc6573", "#718da5"),
    ),
    "light": _Theme(
        "#fafbfd",
        "#293746",
        "#6c7988",
        "#e0e6ec",
        "#e4edf3",
        "#293746",
        ("#ffffff", "#f4f7fa"),
        ("#377eb8", "#d68942", "#56927a", "#9877b1", "#c96f7d", "#778899"),
    ),
    "dark": _Theme(
        "#18232e",
        "#e7edf3",
        "#b2bfcc",
        "#394958",
        "#2e5369",
        "#ffffff",
        ("#202e3b", "#283847"),
        ("#65bed0", "#efac79", "#9cc789", "#b8a0d5", "#e49ba7", "#a0bed7"),
    ),
}


def _get_theme(name: str) -> _Theme:
    if name not in _THEMES:
        message = f"Unknown theme {name!r}; choose default, light, or dark."
        raise ValueError(message)
    return _THEMES[name]

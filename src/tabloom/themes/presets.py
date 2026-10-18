"""Plain, blue, soft blue, and dark blue palettes without global style changes."""

from __future__ import annotations

from tabloom.themes.theme import _Theme

_THEMES = {
    "plain": _Theme(
        "#ffffff",
        "#000000",
        "#000000",
        "#000000",
        "#ffffff",
        "#000000",
        ("#ffffff", "#ffffff"),
        ("#000000", "#444444", "#777777", "#aaaaaa", "#333333", "#999999"),
    ),
    "blue": _Theme(
        "#ffffff",
        "#243447",
        "#637487",
        "#dce3e9",
        "#244c66",
        "#ffffff",
        ("#ffffff", "#f1f5f8"),
        ("#287c8e", "#dc8853", "#698554", "#8875a9", "#bc6573", "#718da5"),
    ),
    "soft_blue": _Theme(
        "#fafbfd",
        "#293746",
        "#6c7988",
        "#e0e6ec",
        "#e4edf3",
        "#293746",
        ("#ffffff", "#f4f7fa"),
        ("#377eb8", "#d68942", "#56927a", "#9877b1", "#c96f7d", "#778899"),
    ),
    "dark_blue": _Theme(
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

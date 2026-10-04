"""Shared colors, matplotlib rcParams and number formatting for figures."""

TEAL_DARK = "#14515E"
TEAL = "#1F7A8C"
AMBER = "#E8A33D"
AMBER_DARK = "#B67816"
CORAL = "#D1495B"
CORAL_DARK = "#9E2F3D"
NAVY = "#22333B"
GREY = "#8A979E"
GREY_DARK = "#5A6B73"
PURPLE = "#6A4C93"

CATEGORY_COLORS = [
    "#1F7A8C", "#D1495B", "#E8A33D", "#6A4C93", "#2A9D8F",
    "#B08968", "#5A6B73", "#4A3568", "#9E2F3D", "#14515E",
]

RC_PARAMS = {
    "font.family": "DejaVu Sans",
    "figure.facecolor": "white",
}


def vn_int(value: int) -> str:
    """1067371 -> '1.067.371'."""
    return f"{value:,}".replace(",", ".")


def vn_pct(fraction: float, decimals: int = 1) -> str:
    """0.728 -> '72,8%'."""
    return f"{fraction * 100:.{decimals}f}%".replace(".", ",")

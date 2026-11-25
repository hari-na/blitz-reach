"""Indian number formatting."""

from __future__ import annotations

CRORE = 10_000_000
LAKH = 100_000


def inr(amount: float) -> str:
    """Format rupees the way an Indian annual report reads."""
    if abs(amount) >= CRORE:
        return f"Rs {amount / CRORE:,.2f} cr"
    if abs(amount) >= LAKH:
        return f"Rs {amount / LAKH:,.2f} lakh"
    return f"Rs {amount:,.0f}"


def pct(fraction: float, places: int = 3) -> str:
    return f"{fraction * 100:.{places}f}%"

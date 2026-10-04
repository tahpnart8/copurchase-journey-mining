"""RQ1: compare category systems on variable quality and on transition results."""

import pandas as pd

from . import category, sequence
from .config import MIN_CELL_OBSERVATIONS


def system_metrics(df: pd.DataFrame, category_col: str) -> dict:
    quality = category.category_quality(df, category_col)
    events = sequence.build_purchase_events(df, category_col)
    counts, _, _ = sequence.transition_matrix(events, category_col)
    assert list(counts.index) == list(counts.columns), "transition matrix is not square"

    return {
        **quality,
        "n_groups": counts.shape[0],
        "n_events": len(events),
        "n_eligible_customers": len(sequence.eligible_customers(events)),
        "n_transitions": int(counts.values.sum()),
        "n_cells": counts.size,
        "n_cells_below_min": int((counts < MIN_CELL_OBSERVATIONS).sum().sum()),
        "self_transition_rate": sequence.self_transition_rate(counts),
        "self_transition_expected": sequence.self_transition_rate_expected(counts),
        "self_transition_lift": sequence.self_transition_lift(counts),
    }


def compare_to_expected(metrics: dict, expected: dict, tol: float) -> list[str]:
    return [
        f"{key}: got {metrics[key]:.4f}, expected {value} (tol {tol})"
        for key, value in expected.items()
        if abs(metrics[key] - value) > tol
    ]

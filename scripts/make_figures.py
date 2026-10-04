"""Generate report figures 2-7 into <outdir>/figures.

Usage:
    python scripts/make_figures.py [--input path/to/online_retail_II.xlsx] [--outdir outputs]
"""

import pickle
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src import pipeline, report_stats, rq1, sequence, viz  # noqa: E402
from src.config import (  # noqa: E402
    CATEGORY_DISPLAY_NAMES, DEMO_CUSTOMER_ID, MIN_CELL_OBSERVATIONS, N_CATEGORIES, NETWORK_EDGES_PER_NODE,
)
from src.palette import CATEGORY_COLORS  # noqa: E402

STEP_LABELS = [
    "Dữ liệu gốc",
    "Sau loại hóa đơn hủy",
    "Sau loại thiếu Customer ID",
    "Sau loại Quantity hoặc Price không dương",
    "Sau loại mã dịch vụ và phí",
    "Sau loại dòng trùng lặp",
]


def log(message: str, start: float) -> None:
    print(f"[{time.time() - start:6.1f}s] {message}", flush=True)


def network_layout(frame, cache_path: Path) -> dict:
    if cache_path.exists():
        return pickle.loads(cache_path.read_bytes())
    pos = viz.compute_network_layout(frame)
    cache_path.write_bytes(pickle.dumps(pos))
    return pos


def main():
    start = time.time()
    args = pipeline.parse_args(__doc__)
    figdir = args.outdir / "figures"
    figdir.mkdir(parents=True, exist_ok=True)

    df, audit, n_raw = pipeline.load_clean_cached(pipeline.find_raw_xlsx(args.input), args.outdir)
    log("loaded cleaned data", start)
    df, graph, communities = pipeline.add_categories(df, keyword=True)
    log("built co-purchase graph and categories", start)

    remaining = [n_raw]
    for _, removed in audit:
        remaining.append(remaining[-1] - removed)
    viz.plot_cleaning_funnel(STEP_LABELS, remaining, figdir / "fig2_cleaning_funnel.png")
    viz.plot_invoice_distribution(report_stats.purchase_frequency(df), figdir / "fig3_invoice_distribution.png")
    log("figures 2-3 done", start)

    events = sequence.build_purchase_events(df, "Category")
    codes = [f"NET_{i}" for i in range(1, N_CATEGORIES + 1)]
    colors = dict(zip(codes, CATEGORY_COLORS), OTHER="#8A979E")
    viz.plot_customer_timeline(
        events[events["CustomerID"] == DEMO_CUSTOMER_ID], "Category",
        CATEGORY_DISPLAY_NAMES, colors, DEMO_CUSTOMER_ID, figdir / "fig4_customer_timeline.png",
    )
    log("figure 4 done", start)

    top = communities[:N_CATEGORIES]
    frame = viz.build_network_frame(graph, top, NETWORK_EDGES_PER_NODE)
    labels = [f"{c}. {CATEGORY_DISPLAY_NAMES[c]}" if c in CATEGORY_DISPLAY_NAMES else c for c in codes]
    layout_cache = args.outdir / "network_layout.pkl"
    if not layout_cache.exists():
        log("computing network layout (about 1 minute, cached afterwards)", start)
    pos = network_layout(frame, layout_cache)
    viz.plot_copurchase_network(frame, top, labels, figdir / "fig5_copurchase_network.png", pos)
    log("figure 5 done", start)

    keyword = rq1.system_metrics(df, "CategoryKeyword")
    network = rq1.system_metrics(df, "Category")
    viz.plot_category_comparison(keyword, network, network["n_events"], figdir / "fig6_category_comparison.png")

    counts, probs, _ = sequence.transition_matrix(events, "Category")
    viz.plot_transition_matrix(
        probs, counts, CATEGORY_DISPLAY_NAMES, MIN_CELL_OBSERVATIONS,
        int(counts.values.sum()), network["n_eligible_customers"], figdir / "fig7_transition_matrix.png",
    )
    log(f"figures 6-7 done; wrote figures to {figdir}", start)


if __name__ == "__main__":
    main()

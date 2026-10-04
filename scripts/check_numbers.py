"""Recompute every reference number and compare; exit code 1 on any mismatch.

Usage:
    python scripts/check_numbers.py [--input path/to/online_retail_II.xlsx] [--outdir outputs]
"""

import sys
from pathlib import Path

import networkx as nx

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src import pipeline, report_stats, rq1, sequence  # noqa: E402
from src.config import CHECK_TOLERANCE, N_CATEGORIES, PERIOD_CUTOFF, REFERENCE_NUMBERS, RQ1_EXPECTED  # noqa: E402


def top10_plus_other_partition(graph: nx.Graph, communities: list[frozenset]) -> list[set]:
    top = [set(c) for c in communities[:N_CATEGORIES]]
    rest = set(graph.nodes) - set().union(*top)
    return top + [rest]


def main():
    args = pipeline.parse_args(__doc__)
    df, audit, n_raw = pipeline.load_clean_cached(pipeline.find_raw_xlsx(args.input), args.outdir)
    audit = dict(audit)
    df, graph, communities = pipeline.add_categories(df, keyword=True)

    aov = report_stats.order_value(df)
    events = sequence.build_purchase_events(df, "Category")
    eligible = sequence.eligible_customers(events)
    counts, _, _ = sequence.transition_matrix(events, "Category")
    period = report_stats.period_split(df, PERIOD_CUTOFF)

    actual = {
        "raw_rows": n_raw,
        **{f"removed_{step}": n for step, n in audit.items()},
        "remaining_rows": len(df),
        "remaining_share": len(df) / n_raw,
        "customers": df["CustomerID"].nunique(),
        "invoices": df["Invoice"].nunique(),
        "skus": df["StockCode"].nunique(),
        "countries": df["Country"].nunique(),
        "total_revenue_gbp": df["Revenue"].sum(),
        "aov_median": aov.median(),
        "aov_mean": aov.mean(),
        "aov_p95": aov.quantile(0.95),
        "graph_nodes": graph.number_of_nodes(),
        "graph_edges": graph.number_of_edges(),
        "communities": len(communities),
        "modularity_all_communities": nx.community.modularity(graph, communities, weight="weight"),
        "modularity_top10_plus_other": nx.community.modularity(
            graph, top10_plus_other_partition(graph, communities), weight="weight"),
        "purchase_events": len(events),
        "eligible_customers": len(eligible),
        "eligible_share": len(eligible) / df["CustomerID"].nunique(),
        "transitions": int(counts.values.sum()),
        "period1_customers": period["period1_customers"],
        "period2_customers": period["period2_customers"],
        "overlap_customers": period["overlap_customers"],
    }

    rq1_results = {
        "keyword": rq1.system_metrics(df, "CategoryKeyword"),
        "community": rq1.system_metrics(df, "Category"),
    }

    failures = []
    print(f"{'metric':45s} {'actual':>16s} {'expected':>16s}  status")
    for key, (expected, tol) in REFERENCE_NUMBERS.items():
        value = actual[key]
        ok = abs(value - expected) <= tol
        if not ok:
            failures.append(key)
        print(f"{key:45s} {value:16,.4f} {expected:16,.4f}  {'ok' if ok else 'MISMATCH'}")

    for system, expected in RQ1_EXPECTED.items():
        for key, exp in expected.items():
            value = rq1_results[system][key]
            ok = abs(value - exp) <= CHECK_TOLERANCE
            if not ok:
                failures.append(f"rq1.{system}.{key}")
            print(f"{'rq1.' + system + '.' + key:45s} {value:16,.4f} {exp:16,.4f}  {'ok' if ok else 'MISMATCH'}")

    for system, (below, cells) in {"keyword": (80, 196), "community": (45, 121)}.items():
        m = rq1_results[system]
        ok = (m["n_cells_below_min"], m["n_cells"]) == (below, cells)
        if not ok:
            failures.append(f"rq1.{system}.cells")
        print(f"{'rq1.' + system + '.cells_below_min/cells':45s} "
              f"{m['n_cells_below_min']:>7d}/{m['n_cells']:<8d} {below:>7d}/{cells:<8d}  {'ok' if ok else 'MISMATCH'}")

    if failures:
        print(f"\n{len(failures)} mismatch(es): {failures}")
        sys.exit(1)
    print("\nAll reference numbers reproduced.")


if __name__ == "__main__":
    main()

"""RQ1: community categories vs keyword-rule baseline, up to the transition matrix.

Usage:
    python scripts/rq1_category_comparison.py [--input path/to/online_retail_II.xlsx] [--outdir outputs]
"""

import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src import pipeline, rq1  # noqa: E402
from src.config import CHECK_TOLERANCE, RQ1_EXPECTED  # noqa: E402


def main():
    args = pipeline.parse_args(__doc__)
    df, _, _ = pipeline.load_clean_cached(pipeline.find_raw_xlsx(args.input), args.outdir)
    df, _, _ = pipeline.add_categories(df, keyword=True)

    results = {
        "keyword": rq1.system_metrics(df, "CategoryKeyword"),
        "community": rq1.system_metrics(df, "Category"),
    }
    table = pd.DataFrame(results)
    table.to_csv(args.outdir / "rq1_comparison.csv")
    with pd.option_context("display.float_format", "{:.4f}".format):
        print(table.to_string())

    failures = [
        f"[{system}] {message}"
        for system, metrics in results.items()
        for message in rq1.compare_to_expected(metrics, RQ1_EXPECTED[system], CHECK_TOLERANCE)
    ]
    if failures:
        print("\nWARNING: RQ1 reference values not reproduced; investigate, do not adjust:")
        print("\n".join(failures))
        sys.exit(1)
    print("\nRQ1 reference values reproduced within tolerance.")


if __name__ == "__main__":
    main()

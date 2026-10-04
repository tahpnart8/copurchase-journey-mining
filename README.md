# Customer Purchase Journeys from Transaction Sequences

Research code for a study on customer purchase journeys derived from
retail transaction sequences, using the Online Retail II dataset.

The central methodological question: retail transaction data rarely
ships with a product category taxonomy. This project generates one
from co-purchase behavior (community detection on a product network)
instead of assuming a taxonomy exists, then measures whether that
choice matters for downstream sequence analysis.

## Status

| Stage | Status |
|---|---|
| Data cleaning | Done, validated against reference numbers |
| Category generation from the co-purchase network | Done |
| Customer sequences (purchase events) | Done |
| First-order Markov transition matrix | Done |
| Sequential pattern mining and association rules | Designed, not yet run |
| Journey clustering and RFM baseline | Designed, not yet run |
| Customer value comparison across clusters | Designed, not yet run |
| Business recommendations | Planned |

## Repository structure

```
.
├── data/                       raw data goes here (not tracked, see data/README.md)
├── src/
│   ├── config.py               paths, thresholds, reference values, category display names
│   ├── pipeline.py             locate raw file, cached cleaning, category assignment
│   ├── clean.py                load both Excel sheets, five-step cleaning
│   ├── category.py             co-purchase graph, Louvain communities, official categories
│   ├── category_keyword.py     keyword-rule baseline (RQ1 contrast only)
│   ├── sequence.py             purchase events, transition matrix, self-transition metrics
│   ├── rq1.py                  RQ1 comparison metrics
│   ├── report_stats.py         descriptive statistics
│   ├── palette.py              figure colors and Vietnamese number formatting
│   └── viz.py                  one plotting function per report figure
├── scripts/
│   ├── run_pipeline.py         clean -> category -> sequences -> transition matrix
│   ├── rq1_category_comparison.py
│   ├── check_numbers.py        recompute and assert all reference numbers
│   └── make_figures.py         regenerate report figures 2-7
├── outputs/
│   └── figures/                report figures (tracked); other outputs are not tracked
└── requirements.txt
```

## Setup

```bash
python -m venv .venv
.venv\Scripts\activate          # Windows; on macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
```

Put `online_retail_II.xlsx` in `data/` (see `data/README.md`), or pass its path with `--input`.
Run all commands from the repo root:

```bash
python scripts/run_pipeline.py
python scripts/rq1_category_comparison.py
python scripts/check_numbers.py
python scripts/make_figures.py
```

The first run reads the Excel file (a few minutes) and caches the cleaned data in
`outputs/clean_base.pkl`; later runs reuse it. Delete that file to force a re-read.
The network layout for figure 5 is cached in `outputs/network_layout.pkl`.

## Method summary

**Cleaning.** Five steps applied in order: drop cancelled invoices
(Invoice prefix `C`), drop rows with no Customer ID, drop non-positive
Quantity or Price, drop service/fee codes (postage, bank charges, and
similar non-product lines), drop exact duplicate rows. Order matters:
changing it changes how many rows each step removes, though not the
final result. See `src/clean.py`.

**Category generation.** A co-purchase graph is built over all SKUs:
two products are connected if they co-occur in at least
`MIN_CO_OCCURRENCE` invoices with lift at least `MIN_LIFT`. Communities
are detected with Louvain (`src/category.py`); the ten largest by number
of products become the official product categories, the remainder is
labelled `OTHER`. This is compared against a keyword-rule baseline on
three metrics: category coverage, median revenue share of the dominant
category per purchase event, and the rate of mixed-category purchase
events. Category names are assigned manually by the team and are
interpretive labels, not algorithm output.

**Why two category methods exist.** Co-purchase communities are the
official categories and are used for all analysis from the clustering stage
onward. The keyword-rule assignment (`src/category_keyword.py`) is kept only
for RQ1: it supplies a contrast transition matrix so we can ask whether the
way categories are generated changes the transition results. The two systems
have different numbers of groups (14 vs 11), and fewer groups raise the
self-transition rate by chance alone, so they are compared with
`self_transition_lift` (observed self-transition rate divided by the rate
expected under independence), not by the raw percentage difference. Run
`scripts/rq1_category_comparison.py` to reproduce the comparison, and
`scripts/check_numbers.py` to check all reference figures.

**Sequences.** Same-day invoices for a customer are merged into a
single purchase event, since a meaningful share of same-day invoice
pairs reflects operational order-splitting rather than two separate
purchase decisions. Each event is labelled by its revenue-dominant
category. Customers with at least `MIN_SEQUENCE_LENGTH` events are
eligible for sequence analysis (`src/sequence.py`).

**Transition matrix.** First-order: the probability of moving from
category A to category B is the number of observed A-to-B transitions
divided by all transitions starting from A. Cells with fewer than
`MIN_CELL_OBSERVATIONS` observations are flagged and not interpreted.

## Roadmap

1. Sequential pattern mining and association rules on constructed sequences
2. Journey-type clustering on sequence-derived features
3. Baseline comparison against RFM clustering on the same customers
4. Customer value comparison across clusters (Kruskal-Wallis)
5. Stability check across two time periods

## Data

Chen, D., Sain, S. L., & Guo, K. (2012). Data mining for the online
retail industry: A case study of RFM model-based customer segmentation
using data mining. *Journal of Database Marketing & Customer Strategy
Management, 19*(3), 197-208. https://doi.org/10.1057/dbm.2012.17

## License

MIT (see LICENSE).

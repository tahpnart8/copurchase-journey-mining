"""Shared constants and thresholds."""

from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_ROOT / "data"
OUTPUT_DIR = PROJECT_ROOT / "outputs"
RAW_XLSX_CANDIDATES = [
    DATA_DIR / "online_retail_II.xlsx",
    PROJECT_ROOT.parent / "online+retail+ii" / "online_retail_II.xlsx",
]

SERVICE_CODES = {
    "POST", "DOT", "M", "m", "C2", "D", "S", "B", "BANK CHARGES", "ADJUST",
    "AMAZONFEE", "PADS", "CRUK", "TEST001", "TEST002",
    "gift_0001_10", "gift_0001_20", "gift_0001_30", "gift_0001_40",
    "gift_0001_50", "gift_0001_60", "gift_0001_70", "gift_0001_80",
    "gift_0001_90",
}

MIN_CO_OCCURRENCE = 10      # min shared invoices per edge
MIN_LIFT = 3                 # minimum lift to keep an edge
MAX_BASKET_SIZE = 60          # larger baskets skipped when counting pairs
LOUVAIN_RESOLUTION = 0.5
LOUVAIN_SEED = 42
N_CATEGORIES = 10             # largest communities kept, rest -> OTHER

MIN_SEQUENCE_LENGTH = 3       # min purchase events per customer
MIN_CELL_OBSERVATIONS = 30    # cells below this are not interpreted

RANDOM_STATE = 42

# reference values for check_numbers.py
CHECK_TOLERANCE = 0.01
RQ1_EXPECTED = {
    "keyword":   {"coverage": 0.839, "median_share": 0.386, "mixed_basket_rate": 0.529,
                  "self_transition_rate": 0.337, "self_transition_lift": 2.32},
    "community": {"coverage": 0.907, "median_share": 0.479, "mixed_basket_rate": 0.338,
                  "self_transition_rate": 0.416, "self_transition_lift": 2.66},
}

PERIOD_CUTOFF = "2010-12-01"
# (expected, absolute tolerance)
REFERENCE_NUMBERS = {
    "raw_rows": (1_067_371, 0),
    "removed_cancelled_invoices": (19_494, 0),
    "removed_missing_customer_id": (242_257, 0),
    "removed_non_positive_quantity_or_price": (71, 0),
    "removed_service_or_fee_codes": (2_912, 0),
    "removed_exact_duplicates": (26_055, 0),
    "remaining_rows": (776_582, 0),
    "remaining_share": (0.728, 0.0005),
    "customers": (5_852, 0),
    "invoices": (36_597, 0),
    "skus": (4_621, 0),
    "countries": (41, 0),
    "total_revenue_gbp": (17_069_314, 0.5),
    "aov_median": (302.55, 0.005),
    "aov_mean": (466.41, 0.005),
    "aov_p95": (1215.63, 0.005),
    "graph_nodes": (2_870, 0),
    "graph_edges": (28_781, 0),
    "communities": (149, 0),
    "modularity_all_communities": (0.857, 0.0005),
    "modularity_top10_plus_other": (0.771, 0.0005),
    "purchase_events": (32_881, 0),
    "eligible_customers": (3_169, 0),
    "eligible_share": (0.542, 0.0005),
    "transitions": (26_019, 0),
    "period1_customers": (4_239, 0),
    "period2_customers": (4_334, 0),
    "overlap_customers": (2_721, 0),
}

DEMO_CUSTOMER_ID = 12828
NETWORK_EDGES_PER_NODE = 4

# manual, interpretive labels for the ten largest communities; unmapped codes are shown as-is
CATEGORY_DISPLAY_NAMES = {
    "NET_1": "Tiệc trà, ăn nhẹ",
    "NET_2": "Giáng sinh",
    "NET_3": "Túi, hộp họa tiết",
    "NET_4": "Đồ chơi, vẽ trẻ em",
    "NET_5": "Trang trí treo cổ điển",
    "NET_6": "Thiệp, quà nhỏ",
    "NET_7": "Union Jack, hoàng gia",
    "NET_8": "Biển hiệu kim loại",
    "NET_9": "Cốc, nến trang trí",
    "NET_10": "Búp bê Nga",
    "OTHER": "Khác",
}

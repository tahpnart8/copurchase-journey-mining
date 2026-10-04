"""One function per figure: takes computed data and an output path, saves a PNG.
Data is computed in scripts/make_figures.py, not here."""

import textwrap

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.colors import LinearSegmentedColormap
from matplotlib.lines import Line2D
from matplotlib.ticker import FuncFormatter

from .palette import AMBER, CATEGORY_COLORS, CORAL, NAVY, RC_PARAMS, TEAL, vn_int, vn_pct

plt.rcParams.update(RC_PARAMS)


def wrap(text: str, width: int) -> str:
    """Wrap to the fewest lines fitting `width`, then balance them by narrowing."""
    lines = textwrap.wrap(text, width) or [text]
    for narrower in range(len(text) // len(lines), width):
        balanced = textwrap.wrap(text, narrower)
        if len(balanced) == len(lines):
            lines = balanced
            break
    return "\n".join(lines)


def plot_cleaning_funnel(step_labels: list[str], step_values: list[int], output_path: str) -> None:
    """Values are rows remaining: raw count first, then one entry per cleaning step."""
    fig, ax = plt.subplots(figsize=(8.2, 4.6))
    colors = ["#9FC5CE", "#7FB3C0", "#4E93A5", "#3A869B", "#2A7B92", TEAL][: len(step_values)]
    ax.barh(range(len(step_values)), step_values, color=colors, edgecolor="white", linewidth=1.2)
    ax.set_yticks(range(len(step_values)))
    ax.set_yticklabels([wrap(label, 22) for label in step_labels], fontsize=9.2, linespacing=1.15)
    ax.invert_yaxis()
    for i, v in enumerate(step_values):
        bold = i in (0, len(step_values) - 1)
        ax.text(
            v + step_values[0] * 0.012,
            i,
            vn_int(v),
            va="center",
            fontsize=9,
            color=NAVY,
            fontweight="bold" if bold else "normal",
        )
    ax.set_xlim(0, step_values[0] * 1.15)
    ax.xaxis.set_major_formatter(FuncFormatter(lambda v, _: vn_int(int(v))))
    ax.set_xlabel("Số dòng dữ liệu")
    ax.set_title(
        "Hình 2. Số dòng còn lại sau từng bước làm sạch\nOnline Retail II, 12/2009 đến 12/2011",
        loc="left",
        fontsize=11,
        color=NAVY,
    )
    kept_pct = step_values[-1] / step_values[0]
    for side in ("top", "right"):
        ax.spines[side].set_visible(False)
    plt.tight_layout(rect=[0, 0.06, 1, 1])
    fig.text(
        0.5,
        0.01,
        f"Giữ lại {vn_int(step_values[-1])} dòng, bằng {vn_pct(kept_pct)} dữ liệu gốc",
        ha="center",
        fontsize=9,
        style="italic",
        color=TEAL,
    )
    plt.savefig(output_path, dpi=170)
    plt.close(fig)


def plot_invoice_distribution(invoices_per_customer: pd.Series, output_path: str) -> None:
    bins = [0, 1, 2, 3, 5, 10, 20, 10_000]
    bin_labels = ["1", "2", "3", "4-5", "6-10", "11-20", ">20"]
    counts = pd.cut(invoices_per_customer, bins, labels=bin_labels).value_counts().sort_index()

    fig, ax = plt.subplots(figsize=(8, 4))
    colors = [CORAL] + [TEAL] * (len(counts) - 1)
    ax.bar(range(len(counts)), counts.values, color=colors, edgecolor="white", linewidth=1.2)
    ax.set_xticks(range(len(counts)))
    ax.set_xticklabels(counts.index)
    for i, v in enumerate(counts.values):
        ax.text(i, v + 25, vn_int(int(v)), ha="center", fontsize=9, color=NAVY)
    ax.set_xlabel("Số hóa đơn của một khách hàng")
    ax.yaxis.set_major_formatter(FuncFormatter(lambda v, _: vn_int(int(v))))
    ax.set_ylabel("Số khách hàng")
    n_total = len(invoices_per_customer)
    ax.set_title(
        f"Hình 3. Phân bố số hóa đơn trên mỗi khách hàng, {vn_int(n_total)} khách hàng sau làm sạch\n"
        "Cột màu đỏ là nhóm chỉ mua một lần, không dùng được cho phân tích chuỗi",
        loc="left",
        fontsize=11,
        color=NAVY,
    )
    one_time = (invoices_per_customer == 1).sum()
    ax.text(
        0.98,
        0.9,
        f"Trung vị {int(invoices_per_customer.median())} hóa đơn\n"
        f"{vn_int(one_time)} khách hàng, bằng {vn_pct(one_time / n_total)}, chỉ mua một lần",
        transform=ax.transAxes,
        ha="right",
        fontsize=9,
        style="italic",
        color=CORAL,
    )
    for side in ("top", "right"):
        ax.spines[side].set_visible(False)
    plt.tight_layout()
    plt.savefig(output_path, dpi=170)
    plt.close(fig)


def plot_customer_timeline(
    customer_events: pd.DataFrame,
    category_col: str,
    category_display_names: dict,
    category_colors: dict,
    customer_id: int,
    output_path: str,
) -> None:
    """customer_events: one customer's events sorted by date (Day, Revenue, NumSKU, category_col)."""
    d = customer_events.reset_index(drop=True)
    fig, ax = plt.subplots(figsize=(10.2, 3.9))
    x = np.arange(len(d))
    ax.plot(x, [1] * len(x), "-", color="#BFC9CE", lw=2.2, zorder=1)
    for i, r in d.iterrows():
        label = category_display_names.get(r[category_col], r[category_col])
        color = category_colors.get(r[category_col], NAVY)
        ax.scatter(
            [i],
            [1],
            s=np.clip(r.Revenue * 1.35, 130, 460),
            facecolor=color,
            edgecolor="white",
            lw=1.6,
            zorder=3,
            alpha=0.92,
        )
        ax.annotate(
            f"Lần {i + 1}\n{wrap(label, 16)}",
            (i, 1),
            xytext=(0, 32),
            textcoords="offset points",
            ha="center",
            fontsize=9.5,
            color=color,
            fontweight="bold",
        )
        day_str = pd.Timestamp(r.Day).strftime("%d/%m/%Y")
        ax.annotate(
            f"{day_str}\n{vn_int(int(round(r.Revenue)))} £\n{r.NumSKU} SKU",
            (i, 1),
            xytext=(0, -54),
            textcoords="offset points",
            ha="center",
            fontsize=8.5,
            color="#5A6B73",
        )
        if i > 0:
            gap_days = (pd.Timestamp(d.Day[i]) - pd.Timestamp(d.Day[i - 1])).days
            ax.annotate(
                f"{gap_days} ngày",
                (i - 0.5, 1),
                xytext=(0, 10),
                textcoords="offset points",
                ha="center",
                fontsize=8.5,
                color="#8A979E",
            )
    ax.set_xlim(-0.55, len(d) - 0.45)
    ax.set_ylim(0.55, 1.45)
    ax.axis("off")
    date_range = f"{pd.Timestamp(d.Day.iloc[0]):%d/%m/%Y} đến {pd.Timestamp(d.Day.iloc[-1]):%d/%m/%Y}"
    ax.set_title(
        f"Hình 4. Chuỗi mua hàng của khách hàng {customer_id}, {len(d)} lần mua từ {date_range}\n"
        "Nhóm sản phẩm theo cộng đồng đồng mua. Đường kính vòng tròn tỷ lệ với giá trị đơn hàng",
        loc="left",
        fontsize=10.5,
        color=NAVY,
    )
    plt.tight_layout()
    plt.savefig(output_path, dpi=170)
    plt.close(fig)


def compute_network_layout(frame_graph) -> dict:
    import networkx as nx

    return nx.spring_layout(frame_graph, seed=7, k=0.55, iterations=200, weight="weight")


def plot_copurchase_network(
    frame_graph,
    top_communities: list,
    community_labels: list[str],
    output_path: str,
    pos: dict,
) -> None:
    """frame_graph: sparse layout-only graph from build_network_frame; top_communities ordered like community_labels."""
    import networkx as nx

    # frame on the largest component; spring_layout scatters small components far away
    components = list(nx.connected_components(frame_graph))
    main_component = max(components, key=len)
    xs = [pos[n][0] for n in main_component]
    ys = [pos[n][1] for n in main_component]
    pad = 0.06
    x_lo, x_hi = min(xs) - pad, max(xs) + pad
    y_lo, y_hi = min(ys) - pad, max(ys) + pad

    colors = CATEGORY_COLORS
    markers = ["o", "s", "^", "D", "v", "P", "X", "*", "h", "8"]

    fig, ax = plt.subplots(figsize=(11.0, 9.2))
    nx.draw_networkx_edges(frame_graph, pos, ax=ax, alpha=0.07, width=0.6, edge_color="#333333")

    degree = dict(frame_graph.degree())
    for i, community in enumerate(top_communities):
        nodes = [n for n in community if n in main_component]
        sizes = 30 + np.array([degree[n] for n in nodes]) * 1.7
        ax.scatter(
            [pos[n][0] for n in nodes],
            [pos[n][1] for n in nodes],
            s=sizes,
            marker=markers[i % len(markers)],
            facecolor=colors[i % len(colors)],
            edgecolor="white",
            linewidth=0.45,
            alpha=0.94,
            zorder=3,
        )
    ax.set_xlim(x_lo, x_hi)
    ax.set_ylim(y_lo, y_hi)

    # fixed-size legend handles, independent of degree-scaled node sizes
    legend_handles = [
        Line2D(
            [0], [0], marker=markers[i % len(markers)], color="none",
            markerfacecolor=colors[i % len(colors)], markeredgecolor="white",
            markeredgewidth=0.4, markersize=7.5, label=community_labels[i],
        )
        for i in range(len(community_labels))
    ]
    legend = ax.legend(handles=legend_handles, loc="upper left", fontsize=9.5, frameon=True, labelspacing=0.7)
    legend.get_frame().set_edgecolor("#DDDDDD")
    ax.axis("off")

    n_total = frame_graph.number_of_nodes()
    n_outliers = n_total - len(main_component)
    ax.set_title(
        f"Hình 5. Mười cộng đồng chính thức trong mạng lưới đồng mua, {vn_int(n_total)} sản phẩm\n"
        "Mỗi sản phẩm nối với bốn sản phẩm có lift cao nhất, dùng để bố trí hình. "
        "Kích thước điểm tỷ lệ với bậc trong đồ thị đầy đủ\n"
        f"Khung nhìn phóng vào cụm chính ({vn_int(len(main_component))} sản phẩm); "
        f"{vn_int(n_outliers)} sản phẩm tách thành các cụm nhỏ rời rạc không hiển thị",
        loc="left",
        fontsize=10.6,
        color=NAVY,
    )
    fig.text(
        0.5,
        0.01,
        "Vị trí điểm trên trục ngang và trục dọc không đo đại lượng nào\n"
        "Thuật toán chỉ đặt các sản phẩm hay được mua cùng nhau ở gần nhau, sản phẩm ít liên quan ở xa nhau\n"
        "Tên nhóm do nhóm nghiên cứu đặt thủ công theo sản phẩm tiêu biểu của từng cộng đồng",
        ha="center",
        va="bottom",
        fontsize=8.6,
        color="#5A6B73",
        style="italic",
    )
    plt.tight_layout(rect=[0, 0.04, 1, 1])
    plt.savefig(output_path, dpi=260)
    plt.close(fig)


def build_network_frame(full_graph, top_communities: list, edges_per_node: int = 4):
    """Layout-only graph: each node in the top communities keeps its strongest edges_per_node edges."""
    import networkx as nx

    nodes = set().union(*top_communities)
    subgraph = full_graph.subgraph(nodes)
    keep_edges = set()
    for node in subgraph.nodes():
        strongest = sorted(subgraph[node].items(), key=lambda kv: -kv[1]["weight"])[:edges_per_node]
        for neighbor, _ in strongest:
            keep_edges.add(tuple(sorted((node, neighbor))))
    frame = nx.Graph()
    frame.add_nodes_from(subgraph.nodes())
    for u, v in keep_edges:
        frame.add_edge(u, v, weight=subgraph[u][v]["weight"])
    return frame


def plot_category_comparison(
    keyword_metrics: dict,
    network_metrics: dict,
    n_events: int,
    output_path: str,
) -> None:
    """Metrics dicts need coverage, median_share, mixed_basket_rate as fractions."""
    panels = [
        ("Tỷ lệ dòng gán\nvào nhóm cụ thể", keyword_metrics["coverage"], network_metrics["coverage"], True),
        ("Tỷ trọng nhóm\nđại diện (trung vị)", keyword_metrics["median_share"], network_metrics["median_share"], True),
        ("Tỷ lệ lần mua\nhỗn hợp (dưới 0,4)", keyword_metrics["mixed_basket_rate"], network_metrics["mixed_basket_rate"], False),
    ]
    fig, axes = plt.subplots(1, 3, figsize=(10.5, 4.0))
    for ax, (title, old_val, new_val, higher_is_better) in zip(axes, panels):
        old_pct, new_pct = old_val * 100, new_val * 100
        ax.bar([0, 1], [old_pct, new_pct], color=[CORAL, TEAL], width=0.55, edgecolor="white", linewidth=1.2)
        ax.set_xticks([0, 1])
        ax.set_xticklabels(["Luật từ khóa\n(đối chứng)", "Cộng đồng\nđồng mua (chính thức)"], fontsize=9.2)
        for i, v in enumerate([old_pct, new_pct]):
            ax.text(i, v + 1.5, f"{v:.1f}%".replace(".", ","), ha="center", fontsize=10, fontweight="bold", color=NAVY)
        ax.set_ylim(0, max(old_pct, new_pct) + 14)
        ax.set_title(title, fontsize=9.8, color=NAVY)
        for side in ("top", "right"):
            ax.spines[side].set_visible(False)
        ax.spines["left"].set_color("#CCCCCC")
        ax.spines["bottom"].set_color("#CCCCCC")
        tag = "càng cao càng tốt" if higher_is_better else "càng thấp càng tốt"
        ax.text(0.5, -0.34, tag, transform=ax.transAxes, ha="center", fontsize=7.8, color="#8A979E", style="italic")

    fig.suptitle(
        f"Hình 6. So sánh hai cách tạo biến nhóm sản phẩm, tính trên {vn_int(n_events)} lần mua "
        "sau khi gộp hóa đơn cùng ngày",
        fontsize=11,
        color=NAVY,
        x=0.02,
        ha="left",
    )
    plt.tight_layout(rect=[0, 0.04, 1, 0.92])
    plt.savefig(output_path, dpi=170)
    plt.close(fig)


def plot_transition_matrix(
    probs: pd.DataFrame,
    counts: pd.DataFrame,
    category_display_names: dict,
    min_observations: int,
    n_transitions: int,
    n_customers: int,
    output_path: str,
) -> None:
    order = [c for c in counts.sum(axis=1).sort_values(ascending=False).index if c != "OTHER"]
    order += [c for c in counts.index if c == "OTHER"]
    probs = probs.loc[order, order]
    counts = counts.loc[order, order]
    labels = [
        f"{c}\n{wrap(category_display_names[c], 14)}" if c in category_display_names else c
        for c in probs.index
    ]

    cmap = LinearSegmentedColormap.from_list(
        "teal_amber", ["#FFFFFF", "#DCEEF2", "#8FC9D4", "#3E96AC", "#1F7A8C", "#14515E"]
    )
    fig, ax = plt.subplots(figsize=(10.4, 8.4))
    im = ax.imshow(probs.values * 100, cmap=cmap, vmin=0, vmax=55)
    ax.set_xticks(range(len(labels)))
    ax.set_xticklabels(labels, rotation=45, ha="right", fontsize=8.2, color=NAVY, linespacing=1.15)
    ax.set_yticks(range(len(labels)))
    ax.set_yticklabels(labels, fontsize=8.2, color=NAVY, linespacing=1.15)
    ax.set_xticks(np.arange(-0.5, len(labels), 1), minor=True)
    ax.set_yticks(np.arange(-0.5, len(labels), 1), minor=True)
    ax.grid(which="minor", color="white", linewidth=1.1)
    ax.tick_params(which="minor", length=0)

    for i in range(len(labels)):
        for j in range(len(labels)):
            value = probs.values[i, j]
            n_obs = counts.values[i, j]
            if n_obs < min_observations:
                text_color = "#C2B8A3"
            elif value > 0.32:
                text_color = "white"
            else:
                text_color = "#2F4550"
            ax.text(
                j, i, f"{value * 100:.0f}", ha="center", va="center", fontsize=8.2,
                color=text_color, fontweight="bold" if i == j else "normal",
            )
    for i in range(len(labels)):
        ax.add_patch(plt.Rectangle((i - 0.5, i - 0.5), 1, 1, fill=False, edgecolor=AMBER, lw=1.6, zorder=4))

    ax.set_xlabel("Nhóm sản phẩm của lần mua sau", color=NAVY)
    ax.set_ylabel("Nhóm sản phẩm của lần mua trước", color=NAVY)
    ax.set_title(
        f"Hình 7. Ma trận chuyển tiếp theo category mới (cộng đồng đồng mua), đơn vị phần trăm\n"
        f"{vn_int(n_transitions)} lần chuyển của {vn_int(n_customers)} khách hàng có từ ba lần mua, "
        f"{len(labels) - 1} nhóm cộng OTHER\n"
        f"Viền vàng là đường chéo. Số mờ là ô dưới {min_observations} quan sát\n"
        "Tên nhóm do nhóm nghiên cứu đặt thủ công theo sản phẩm tiêu biểu của từng cộng đồng",
        loc="left",
        fontsize=10,
        color=NAVY,
    )
    plt.colorbar(im, fraction=0.035, label="Xác suất chuyển (%)")
    plt.tight_layout()
    plt.savefig(output_path, dpi=170)
    plt.close(fig)


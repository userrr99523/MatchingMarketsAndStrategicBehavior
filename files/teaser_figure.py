import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch, Circle, Rectangle

plt.rcParams["font.family"] = "DejaVu Sans"
plt.rcParams["mathtext.fontset"] = "dejavusans"

BLUE, PINK, ORANGE, GREY, DARK = "#3b6ea5", "#c0527a", "#e08a1e", "#b8b8b8", "#222222"
TEAL, PURPLE = "#2a9d8f", "#6a4c93"

fig = plt.figure(figsize=(14, 5.2))

# ---------- helper ----------
def blank(rect):
    ax = fig.add_axes(rect)
    ax.set_xlim(0, 10); ax.set_ylim(0, 10); ax.axis("off")
    return ax

def node(ax, x, y, label, color, r=0.55, fs=10, ec="white"):
    ax.add_patch(Circle((x, y), r, fc=color, ec=ec, lw=1.5, zorder=3))
    ax.text(x, y, label, ha="center", va="center", color="white",
            fontsize=fs, fontweight="bold", zorder=4)

# =====================================================
# Panel 1: what we study
# =====================================================
ax1 = blank([0.02, 0.22, 0.31, 0.62])
men_y = [9.0, 7.6, 6.2]
xm, xw = 2.4, 7.6
# acceptable (non-matched) pairs, faint
for (i, j) in [(0, 0), (0, 2), (1, 2), (2, 0), (2, 1), (1, 0)]:
    ax1.plot([xm, xw], [men_y[i], men_y[j]], color=GREY, lw=1, ls="--", zorder=1)
# stable matching, bold
for (i, j) in [(0, 1), (1, 0), (2, 2)]:
    ax1.plot([xm, xw], [men_y[i], men_y[j]], color=DARK, lw=2.8, zorder=2)
for k, y in enumerate(men_y):
    node(ax1, xm, y, rf"$m_{k+1}$", BLUE)
    node(ax1, xw, y, rf"$w_{k+1}$", PINK)
ax1.text(xm, 10.0, "Men", ha="center", color=BLUE, fontsize=11, fontweight="bold")
ax1.text(xw, 10.0, "Women", ha="center", color=PINK, fontsize=11, fontweight="bold")
ax1.text(5.0, 5.35, "stable matching", ha="center", fontsize=9, style="italic", color="#555")

# preference lists for the manipulating agent (w1 manipulates)
ax1.text(0.0, 4.35, r"Agent $w_1$'s list:", fontsize=10, fontweight="bold", color=DARK)
rows = [
    ("True",        r"$m_1 \succ m_2 \succ m_3$", DARK,   3.35),
    ("Truncation",  r"$m_1 \succ m_2$",           TEAL,   1.95),
    ("Permutation", r"$m_2 \succ m_1 \succ m_3$", PURPLE, 0.55),
]
for name, lst, col, y in rows:
    ax1.add_patch(FancyBboxPatch((0.0, y - 0.45), 3.0, 0.9,
                  boxstyle="round,pad=0.02,rounding_size=0.25", fc=col, ec="none"))
    ax1.text(1.5, y, name, color="white", ha="center", va="center",
             fontsize=9.5, fontweight="bold")
    ax1.text(3.4, y, lst, ha="left", va="center", fontsize=11.5, color=DARK)
# =====================================================
# Panel 2: truncation -> lattice
# =====================================================
ax2 = blank([0.37, 0.22, 0.27, 0.62])
nodes = {"top": (5, 9.0), "a": (2.6, 6.6), "b": (7.4, 6.6),
         "c": (5, 4.4), "bot": (5, 1.9)}
edges = [("top", "a"), ("top", "b"), ("a", "c"), ("b", "c"), ("c", "bot")]
for u, v in edges:
    (x1, y1), (x2, y2) = nodes[u], nodes[v]
    ax2.plot([x1, x2], [y1, y2], color=GREY, lw=2.2, zorder=1)
for k, (x, y) in nodes.items():
    ax2.add_patch(Circle((x, y), 0.5, fc="white", ec=DARK, lw=1.8, zorder=3))
ax2.add_patch(Circle(nodes["top"], 0.5, fc=BLUE, ec=DARK, lw=1.8, zorder=4))
ax2.add_patch(Circle(nodes["bot"], 0.5, fc=PINK, ec=DARK, lw=1.8, zorder=4))
ax2.add_patch(Circle(nodes["a"], 0.5, fc=TEAL, ec=DARK, lw=1.8, zorder=4))
ax2.text(5.8, 9.0, "man-optimal\n(truthful outcome)", fontsize=9, color=BLUE, fontweight="bold", ha="left", va="center")
ax2.text(5.8, 1.9, "woman-optimal", fontsize=9, color=PINK, fontweight="bold", ha="left", va="center")
ax2.annotate("", xy=(nodes["a"][0] + 0.25, nodes["a"][1] + 0.45),
             xytext=(nodes["top"][0] - 0.25, nodes["top"][1] - 0.45),
             arrowprops=dict(arrowstyle="-|>", color=TEAL, lw=3.2,
                             connectionstyle="arc3,rad=0"), zorder=5)
ax2.text(0.0, 8.3, "truncation\nmoves outcome", fontsize=9, color=TEAL,
         fontweight="bold", ha="left", va="center")
# side axis: who is better off
ax2.annotate("", xy=(9.6, 1.4), xytext=(9.6, 9.4),
             arrowprops=dict(arrowstyle="<|-|>", color="#999", lw=1.2))
ax2.text(9.95, 8.6, "better for men", rotation=90, fontsize=8, color="#888", va="top", ha="left")
ax2.text(9.95, 2.2, "better for women", rotation=90, fontsize=8, color="#888", va="bottom", ha="left")

# =====================================================
# Panel 3: permutation -> heatmap (ILLUSTRATIVE DATA)
# =====================================================
ax3 = fig.add_axes([0.715, 0.35, 0.19, 0.40])
phis = np.array([0.1, 0.3, 0.5, 0.7, 0.9])
# ---- replace `data` with your real pivot_table.values to use real results ----
rng = np.random.default_rng(1)
PM, PW = np.meshgrid(phis, phis)           # rows: phi_m, cols: phi_w
data = 0.08 + 0.55 * PW**1.5 * (1 - 0.6 * PM) + 0.04 * rng.standard_normal(PM.shape)
data = np.clip(data, 0, 1)
# -------------------------------------------------------------------------------
im = ax3.imshow(data, origin="lower", cmap="cividis", aspect="auto")
ax3.set_xticks(range(5)); ax3.set_yticks(range(5))
ax3.set_xticklabels([f"{v:.1f}" for v in phis], fontsize=8)
ax3.set_yticklabels([f"{v:.1f}" for v in phis], fontsize=8)
ax3.set_xlabel(r"$\phi_w$", fontsize=14); ax3.set_ylabel(r"$\phi_m$", fontsize=14)
for s in ax3.spines.values():
    s.set_visible(False)
ax3.tick_params(length=0)
cax = fig.add_axes([0.915, 0.35, 0.010, 0.40])
cb = fig.colorbar(im, cax=cax); cb.ax.tick_params(labelsize=7)
cb.set_label("degree of manipulation", fontsize=8)

# =====================================================
# Titles, captions, banners, dividers
# =====================================================
def title(x, t):
    fig.text(x, 0.94, t, ha="center", va="center", fontsize=14, fontweight="bold", color=DARK)

title(0.175, "1  Manipulation in stable matching")
title(0.505, "2  Truncation strategies")
title(0.81,  "3  Permutation strategies")

def cap(x, t):
    fig.text(x, 0.165, t, ha="center", va="center", fontsize=10.5, color="#333", linespacing=1.3)

cap(0.175, "Agents can misreport by cutting\ntheir list short or reordering it")
cap(0.505, "Effect is fully characterized by the\nlattice of stable matchings")
cap(0.81,  "Effect depends on distributional\nfeatures such as preference correlation")

def banner(x0, x1, text, col):
    fig.add_artist(FancyBboxPatch((x0, 0.025), x1 - x0, 0.065,
                   boxstyle="round,pad=0.002,rounding_size=0.012",
                   fc=col, ec="none", transform=fig.transFigure))
    fig.text((x0 + x1) / 2, 0.0575, text, ha="center", va="center",
             color="white", fontsize=12, fontweight="bold")

banner(0.375, 0.635, "Distribution-independent", TEAL)
banner(0.695, 0.935, "Distribution-dependent", PURPLE)

for x in (0.345, 0.665):
    fig.add_artist(plt.Line2D([x, x], [0.12, 0.90], color="#ddd", lw=1.2,
                              transform=fig.transFigure))

fig.savefig("/mnt/user-data/outputs/teaser_figure.pdf", bbox_inches="tight")
fig.savefig("/mnt/user-data/outputs/teaser_figure.png", dpi=200, bbox_inches="tight")

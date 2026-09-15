#!/usr/bin/env python3
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D

# ---- Font: Times New Roman, 16 pt (falls back to another serif if unavailable) ----
matplotlib.rcParams["font.family"] = "serif"
matplotlib.rcParams["font.serif"] = ["Times New Roman", "Nimbus Roman", "Liberation Serif", "DejaVu Serif"]
matplotlib.rcParams["mathtext.fontset"] = "stix"
matplotlib.rcParams["font.size"] = 22
matplotlib.rcParams["axes.titlesize"] = 22
matplotlib.rcParams["axes.labelsize"] = 22
matplotlib.rcParams["xtick.labelsize"] = 22
matplotlib.rcParams["ytick.labelsize"] = 22
matplotlib.rcParams["legend.fontsize"] = 22

# ---- data: (size, quant, latency_s_per_intent, action_correct_%) ----
DATA = [
    ("0.5B", "Q2_K",   1.64, 24.0),
    ("0.5B", "Q4_K_M", 1.74, 32.5),
    ("0.5B", "Q8_0",   1.61, 26.0),
    ("1.5B", "Q2_K",   2.58, 39.5),
    ("1.5B", "Q4_K_M", 3.22, 41.0),
    ("1.5B", "Q8_0",   4.64, 40.5),
    ("3B",   "Q2_K",   4.45, 42.5),
    ("3B",   "Q4_K_M", 5.11, 46.0),
    ("3B",   "Q8_0",   5.90, 44.0),
    ("7B",   "Q2_K",   8.63, 42.0),
    ("7B",   "Q4_K_M", 11.25, 43.0),
    ("7B",   "Q8_0",   12.64, 44.0),
]

SHAPE = {"0.5B": "o", "1.5B": "s", "3B": "^", "7B": "D"}
COLOR = {"Q2_K": "#E8836B", "Q4_K_M": "#3AA6A0", "Q8_0": "#2E4374"}

fig, ax = plt.subplots(figsize=(10, 6.5))

for size, quant, lat, acc in DATA:
    ax.scatter(lat, acc, s=200, marker=SHAPE[size], c=COLOR[quant],
               edgecolors="black", linewidths=0.8, zorder=3)

# Pareto frontier (minimise latency, maximise accuracy)
pts = sorted([(l, a) for _, _, l, a in DATA])
front, best = [], -1
for l, a in pts:
    if a > best:
        front.append((l, a)); best = a
ax.plot([l for l, _ in front], [a for _, a in front],
        "--", color="grey", linewidth=1.3, zorder=1)

# highlight the 3B Q4_K_M sweet spot
sl, sa = 5.11, 46.0
ax.scatter([sl], [sa], s=560, facecolors="none",
           edgecolors="#E0A500", linewidths=3.0, zorder=2)
# annotation placed inside the plot area (open space), with an arrow to the point
ax.annotate("3B Q4_K_M\n46.0% action, 5.11 s",
            xy=(sl, sa), xytext=(8, 45),
            ha="center", va="center", color="#0A0700", fontsize=20,
            arrowprops=dict(arrowstyle="->", color="#B8860B", lw=1.5))

ax.set_xlabel("Latency (s/intent)")
ax.set_ylabel("Action correct (%)")
ax.set_title("Phase 2: action accuracy vs. cost (temp=0, n=200)")

size_handles = [Line2D([0], [0], marker=SHAPE[s], color="w", markerfacecolor="grey",
                       markeredgecolor="black", markersize=10, label=s) for s in SHAPE]
quant_handles = [Line2D([0], [0], marker="o", color="w", markerfacecolor=COLOR[q],
                        markeredgecolor="black", markersize=10, label=q) for q in COLOR]
# two legends stacked vertically at lower-right so they never overlap at 20 pt
leg1 = ax.legend(handles=size_handles, loc="lower right",
                 bbox_to_anchor=(0.72, 0.0), fontsize=20, title="Size", framealpha=0.9)
ax.add_artist(leg1)
ax.legend(handles=quant_handles, loc="lower right",
          bbox_to_anchor=(1.0, 0.0), fontsize=20, title="Quant", framealpha=0.9)

plt.tight_layout()
plt.savefig("fig3.png", dpi=500)
print("wrote fig3.png (dpi=500)")

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

# ---- data: (size, quant, peak_memory_MB, action_correct_%) ----
DATA = [
    ("0.5B", "Q2_K",   421, 24.0),
    ("0.5B", "Q4_K_M", 474, 32.5),
    ("0.5B", "Q8_0",   605, 26.0),
    ("1.5B", "Q2_K",   778, 39.5),
    ("1.5B", "Q4_K_M", 1075, 41.0),
    ("1.5B", "Q8_0",   1714, 40.5),
    ("3B",   "Q2_K",   1372, 42.5),
    ("3B",   "Q4_K_M", 1997, 46.0),
    ("3B",   "Q8_0",   3301, 44.0),
    ("7B",   "Q2_K",   3083, 42.0),
    ("7B",   "Q4_K_M", 4672, 43.0),
    ("7B",   "Q8_0",   7947, 44.0),
]

# style maps
SHAPE = {"0.5B": "o", "1.5B": "s", "3B": "^", "7B": "D"}       # size -> marker
COLOR = {"Q2_K": "#E8836B", "Q4_K_M": "#3AA6A0", "Q8_0": "#2E4374"}  # quant -> fill

fig, ax = plt.subplots(figsize=(10, 6.5))

# scatter every configuration
for size, quant, mem, acc in DATA:
    ax.scatter(mem, acc, s=200, marker=SHAPE[size], c=COLOR[quant],
               edgecolors="black", linewidths=0.8, zorder=3)

# Pareto frontier (minimise memory, maximise accuracy)
pts = sorted([(m, a) for _, _, m, a in DATA])
front, best = [], -1
for m, a in pts:
    if a > best:
        front.append((m, a)); best = a
ax.plot([m for m, _ in front], [a for _, a in front],
        "--", color="grey", linewidth=1.3, zorder=1)

# highlight the 3B Q4_K_M sweet spot
sm, sa = 1997, 46.0
ax.scatter([sm], [sa], s=560, facecolors="none",
           edgecolors="#E0A500", linewidths=3.0, zorder=2)
# annotation placed inside the plot area (open space), with an arrow to the point
ax.annotate(f"3B Q4_K_M\n46.0% action, {1997:.2f} MB",
            xy=(sm, sa), xytext=(550, 45),
            ha="center", va="center", color="#0A0700", fontsize=20,
            arrowprops=dict(arrowstyle="->", color="#B8860B", lw=1.5))

# log x-axis with the same ticks as the reference figure
ax.set_xscale("log")
ax.set_xlim(250, 16000)
ax.set_xticks([250, 500, 1000, 2000, 4000, 8000, 16000])
ax.get_xaxis().set_major_formatter(matplotlib.ticker.ScalarFormatter())

ax.set_xlabel("Peak memory (MB, log)")
ax.set_ylabel("Action correct (%)")
ax.set_title("Phase 2: action accuracy vs. cost (temp=0, n=200)")

# two legends: marker shape = size, fill colour = quant
size_handles = [Line2D([0], [0], marker=SHAPE[s], color="w", markerfacecolor="grey",
                       markeredgecolor="black", markersize=10, label=s) for s in SHAPE]
quant_handles = [Line2D([0], [0], marker="o", color="w", markerfacecolor=COLOR[q],
                        markeredgecolor="black", markersize=10, label=q) for q in COLOR]
leg1 = ax.legend(handles=size_handles, loc="lower right",
                 bbox_to_anchor=(1, 0.3), fontsize=20, framealpha=0.9)
ax.add_artist(leg1)
ax.legend(handles=quant_handles, loc="lower right", fontsize=20, framealpha=0.9)

plt.tight_layout()
plt.savefig("fig2.png", dpi=500)
print("wrote fig2.png")

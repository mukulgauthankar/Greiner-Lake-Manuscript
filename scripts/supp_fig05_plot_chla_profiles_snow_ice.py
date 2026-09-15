from pathlib import Path
from matplotlib.lines import Line2D
from matplotlib.patches import Patch
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

# ============================================================
# 0) REPOSITORY PATHS & SAVING SETUP
# ============================================================
BASE_DIR = Path(__file__).resolve().parent.parent if Path(__file__).resolve().parent.name == "scripts" else Path(__file__).resolve().parent
SAVE_DIR = BASE_DIR / "figures"
SAVE_DIR.mkdir(parents=True, exist_ok=True)

DO_SAVE = True
SAVE_DPIS = [600, 1200]

# ============================================================
# 1) STYLE SETUP
# ============================================================
BASE_FONT = 16
plt.rcParams.update({
    "figure.facecolor": "white",
    "axes.facecolor": "white",
    "font.family": "DejaVu Sans",
    "font.size": BASE_FONT,
    "axes.titlesize": BASE_FONT + 1,
    "axes.labelsize": BASE_FONT,
    "xtick.labelsize": BASE_FONT - 1,
    "ytick.labelsize": BASE_FONT - 1,
    "axes.linewidth": 1.5,
    "xtick.direction": "out",
    "ytick.direction": "out",
    "axes.grid": False,
})

# ============================================================
# 2) REPLICATE DATA & STANDARD ERROR CALCULATION
# ============================================================
raw_replicates = {
    "Year": [
        # 2021 Replicates
        "2021", "2021", "2021", "2021", "2021", "2021", "2021", "2021", "2021", "2021", "2021", "2021",
        # 2022 Replicates
        "2022", "2022", "2022", "2022", "2022", "2022", "2022", "2022", "2022", "2022", "2022", "2022", "2022", "2022", "2022",
        # 2025 Replicates
        "2025", "2025", "2025", "2025", "2025", "2025", "2025", "2025", "2025"
    ],
    "Depth_m": [
        # 2021 Depths
        0, 0, 1, 1, 2, 2, 4, 4, 6, 6, 8, 8,
        # 2022 Depths
        0, 0, 0, 2, 2, 2, 4, 4, 4, 6, 6, 6, 8, 8, 8,
        # 2025 Depths
        0, 0, 0, 5, 5, 5, 9, 9, 9
    ],
    "Chla_ugL": [
        # 2021 Chl-a values
        0.93, 0.93, 1.04, 0.99, 0.86, 0.94, 0.66, 0.65, 0.50, 0.46, 0.29, 0.30,
        # 2022 Chl-a values
        1.61, 1.56, 1.59, 1.53, 1.32, 1.49, 0.79, 0.79, 0.70, 0.82, 0.64, 0.55, 0.55, 0.48, 0.50,
        # 2025 Chl-a values
        2.81, 3.29, 3.81, 3.04, 3.16, 2.93, 2.39, 2.32, 2.32
    ]
}

df_raw = pd.DataFrame(raw_replicates)

def calculate_se(x):
    return x.std(ddof=1) / np.sqrt(len(x)) if len(x) > 1 else 0.0

df = df_raw.groupby(["Year", "Depth_m"])["Chla_ugL"].agg(
    Chla_Mean="mean",
    Chla_SE=calculate_se
).reset_index()

year_order = ["2021", "2022", "2025"]
year_styles = {
    "2021": {"color": "#ff7f0e", "label": "2021 (Nov 29 | Snow: 12.8 cm)"},
    "2022": {"color": "#1f77b4", "label": "2022 (Nov 07 | Snow: 5.0 cm)"},
    "2025": {"color": "#2ca02c", "label": "2025 (Nov 16 | Snow: ~0 cm*)"},
}

# ============================================================
# 3) PLOT GENERATION
# ============================================================
fig, ax1 = plt.subplots(figsize=(6.5, 11))

ice_m = 0.55

# Proportional snow layer calculation
snow_2021_cm = 12.8
snow_2022_cm = 5.0
SCALE_FACTOR = 10.0  # Visual amplification (10x zoom) to render thin snow layers clearly

ymin_2021 = -(ice_m + (snow_2021_cm / 100.0) * SCALE_FACTOR)  # -1.83 m
ymin_2022 = -(ice_m + (snow_2022_cm / 100.0) * SCALE_FACTOR)  # -1.05 m

# 1. Ice Sheet (0.0 to -0.55 m)
ax1.axhspan(
    ymin=-ice_m,
    ymax=0.0,
    facecolor="#07ecec",
    edgecolor="#008b8b",
    linewidth=1.5,
    alpha=0.60,
    zorder=2,
)
ax1.text(
    2.0,
    -ice_m / 2.0,
    "Ice Cover: ≈55 cm",
    ha="center",
    va="center",
    fontsize=12.0,
    fontweight="bold",
    color="#004445",
)

# 2. Chronological Snow Covers Above Ice Sheet
# Slot 1: 2021 Snow (12.8 cm)
ax1.axhspan(
    ymin=ymin_2021,
    ymax=-ice_m,
    xmin=0.04,
    xmax=0.32,
    facecolor="#fff3e0",
    edgecolor="#ff7f0e",
    linewidth=1.5,
    hatch="\\\\",
    alpha=0.9,
    zorder=3,
)
ax1.text(
    0.72,
    ymin_2021 - 0.12,
    f"29-11-2021\nSnow: {snow_2021_cm} cm",
    ha="center",
    va="bottom",
    fontsize=12,
    fontweight="bold",
    color="#e65100",
    bbox=dict(boxstyle="round,pad=0.1", facecolor="white", alpha=0.90, edgecolor="none"),
)

# Slot 2: 2022 Snow (5.0 cm)
ax1.axhspan(
    ymin=ymin_2022,
    ymax=-ice_m,
    xmin=0.36,
    xmax=0.64,
    facecolor="#e3f2fd",
    edgecolor="#1f77b4",
    linewidth=1.5,
    hatch="//",
    alpha=0.9,
    zorder=3,
)
ax1.text(
    2.0,
    ymin_2022 - 0.12,
    f"07-11-2022\nSnow: {snow_2022_cm} cm",
    ha="center",
    va="bottom",
    fontsize=12,
    fontweight="bold",
    color="#0d47a1",
    bbox=dict(boxstyle="round,pad=0.1", facecolor="white", alpha=0.90, edgecolor="none"),
)

# Slot 3: 2025 Sampling (0 cm effective snow)
ax1.text(
    3.28,
    -ice_m - 0.07,
    "16-11-2025\nSnow: ~0 cm*",
    ha="center",
    va="bottom",
    fontsize=12,
    fontweight="bold",
    color="#1b5e20",
    bbox=dict(boxstyle="round,pad=0.15", facecolor="white", alpha=0.90, edgecolor="none"),
)

# Ice-Water Interface (0.0 m)
ax1.axhline(0.0, color="#111111", linestyle="-", linewidth=1.8, zorder=4)

# Water Column Chl-a Profiles with Error Bars
for yr in year_order:
    sub = df[df["Year"] == yr].sort_values("Depth_m").copy()
    style = year_styles[yr]

    ax1.errorbar(
        sub["Chla_Mean"],
        sub["Depth_m"],
        xerr=sub["Chla_SE"],
        color=style["color"],
        linewidth=2.5,
        linestyle="-",
        marker="o",
        markersize=6,
        capsize=4,
        capthick=1.5,
        ecolor=style["color"],
        zorder=5,
    )

ax1.set_xlabel(r"Chl-$a$ ($\mu\mathrm{g}\ \mathrm{L}^{-1}$)", color="black", fontweight="bold", labelpad=8)
ax1.set_ylabel("Lake Depth Below Ice (m)", fontweight="bold")
ax1.set_xlim(0, 4.0)
ax1.set_ylim(10.0, -2.7)

legend_elements = [
    Patch(facecolor="#07ecec", edgecolor="#008b8b", alpha=0.6, label="Ice Sheet (55 cm)"),
    Patch(facecolor="#f5f5f5", edgecolor="#5f6d75", hatch="//", label="On-Ice Snow Cover"),
    Line2D([0], [0], color="#ff7f0e", lw=2, marker="o", label="2021 (Nov 29 | Snow: 12.8 cm)"),
    Line2D([0], [0], color="#1f77b4", lw=2, marker="o", label="2022 (Nov 07 | Snow: 5.0 cm)"),
    Line2D([0], [0], color="#2ca02c", lw=2, marker="o", label="2025 (Nov 16 | Snow: ~0 cm*)"),
]

ax1.legend(
    handles=legend_elements,
    loc="upper center",
    bbox_to_anchor=(0.5, -0.12),
    ncol=2,
    frameon=True,
    facecolor="white",
    edgecolor="#cccccc",
    framealpha=1.0,
    fontsize=12,
    columnspacing=1.5,
)

fig.tight_layout()
plt.subplots_adjust(top=0.92, bottom=0.22)

# ============================================================
# 4) EXPORT FIGURES (SUPPLEMENTARY FIGURE 5)
# ============================================================
if DO_SAVE:
    png_out = SAVE_DIR / "supp_fig05_chla_profiles_snow_ice.png"
    fig.savefig(png_out, dpi=600, bbox_inches="tight")
    print(f"✓ Saved: {png_out.name}")

    for dpi in SAVE_DPIS:
        tiff_out = SAVE_DIR / f"supp_fig05_chla_profiles_snow_ice_{dpi}dpi.tiff"
        fig.savefig(
            tiff_out, 
            dpi=dpi, 
            format="tiff", 
            pil_kwargs={"compression": "tiff_lzw"}, 
            bbox_inches="tight"
        )
        print(f"✓ Saved: {tiff_out.name}")

plt.show()
plt.close(fig)

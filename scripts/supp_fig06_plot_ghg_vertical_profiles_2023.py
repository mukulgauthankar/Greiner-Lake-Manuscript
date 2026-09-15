from pathlib import Path
from matplotlib.lines import Line2D
import matplotlib.pyplot as plt
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
# 1) GLOBAL STYLE / RC PARAMS
# ============================================================
plt.style.use("seaborn-v0_8-white")
BASE_FONT = 14

plt.rcParams.update({
    "font.family": "DejaVu Sans",
    "font.size": BASE_FONT,
    "axes.linewidth": 2.0,
    "axes.edgecolor": "#111111",
    "xtick.major.width": 1.5,
    "ytick.major.width": 1.5,
})

# ============================================================
# 2) DATA PREPARATION
# ============================================================
gas_data = pd.DataFrame({
    "Sample_ID": [
        "CB23_APR_GRL_1.5M", "CB23_APR_GRL_8M", "CB23_MAY_GRL_1.5M", "CB23_MAY_GRL_8M",
        "CB23_JUNE_GRL_1.5M", "CB23_JUNE_GRL_8M", "CB23_JULY1_GRL_1.5M", "CB23_JULY1_GRL_8M",
        "CB23_JULY2_GRL_0.5M", "CB23_JULY2_GRL_9.5M", "CB23_AUGUST_GRL_0.5M", "CB23_AUGUST_GRL_10M"
    ],
    "Campaign": [
        "CB23_APRIL", "CB23_APRIL", "CB23_MAY", "CB23_MAY",
        "CB23_JUNE", "CB23_JUNE", "CB23_EARLY-JULY", "CB23_EARLY-JULY",
        "CB23_LATE-JULY", "CB23_LATE-JULY", "CB23_AUGUST", "CB23_AUGUST"
    ],
    "CH4_ppm": [2.752423, 4.172292, 2.979942, 3.145169, 2.829310, 3.538805,
                9.463682, 3.413722, 3.582804, 10.904161, 4.043091, 3.998306],
    "CO2_ppm": [3340.067, 6015.121, 3793.595, 4715.266, 4017.230, 6612.539,
                451.842, 573.270, 297.931, 432.527, 452.633, 368.477],
    "N2O_ppm": [0.789419, 3.692833, 1.092888, 1.788133, 4.699348, 1.882648,
                0.383727, 0.780734, 0.330638, 0.331248, 0.376938, 0.340408]
})

# Categorize depth (Top vs Bottom water column)
gas_data["Depth_Cat"] = ["Top" if "1.5M" in s or "0.5M" in s else "Bottom" for s in gas_data["Sample_ID"]]

# Standardize campaign month labels
campaign_renamer = {
    "CB23_APRIL": "Apr 2023",
    "CB23_MAY": "May 2023",
    "CB23_JUNE": "Jun 2023",
    "CB23_EARLY-JULY": "Early July\n2023",
    "CB23_LATE-JULY": "Late July\n2023",
    "CB23_AUGUST": "Aug 2023"
}
gas_data["Month"] = gas_data["Campaign"].map(campaign_renamer)

sampled_months = [
    "Apr 2023", "May 2023", "Jun 2023", 
    "Early July\n2023", "Late July\n2023", "Aug 2023"
]

# ============================================================
# 3) SUBPLOT STYLING CONFIGURATIONS
# ============================================================
plot_configs = [
    {"col": "CO2_ppm", "ylabel": r"$\mathrm{CO}_2$ (ppm)", "top_c": "#6D597A", "bot_c": "#352641"},
    {"col": "N2O_ppm", "ylabel": r"$\mathrm{N}_2\mathrm{O}$ (ppm)", "top_c": "#48CAE4", "bot_c": "#0077B6"},
    {"col": "CH4_ppm", "ylabel": r"$\mathrm{CH}_4$ (ppm)", "top_c": "#F3A261", "bot_c": "#E76F51"}
]

# ============================================================
# 4) FIGURE GENERATION
# ============================================================
fig, axes = plt.subplots(3, 1, figsize=(10, 12), sharex=True)
plt.subplots_adjust(hspace=0.35)

for i, config in enumerate(plot_configs):
    ax = axes[i]
    gas_col = config["col"]

    t_data = gas_data[gas_data["Depth_Cat"] == "Top"].set_index("Month").reindex(sampled_months).reset_index()
    b_data = gas_data[gas_data["Depth_Cat"] == "Bottom"].set_index("Month").reindex(sampled_months).reset_index()

    # Top Depth (Solid line, Circle marker)
    ax.plot(
        sampled_months, t_data[gas_col], color=config["top_c"], lw=3, label="Top",
        marker="o", ms=10, mec=config["top_c"], mew=1.0, zorder=3, ls="-"
    )

    # Bottom Depth (Dashed line, Square marker)
    ax.plot(
        sampled_months, b_data[gas_col], color=config["bot_c"], lw=3, label="Bottom",
        marker="s", ms=9, mec=config["bot_c"], mew=1.0, zorder=3, ls="--"
    )

    ax.set_ylabel(config["ylabel"], fontweight="bold", labelpad=12, fontsize=BASE_FONT + 1)
    ax.grid(True, axis="y", linestyle="--", alpha=0.5, color="#CCCCCC")
    ax.grid(True, axis="x", linestyle=":", alpha=0.3, color="#CCCCCC")
    
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_linewidth(2.0)
    ax.spines["bottom"].set_linewidth(2.0)

    for label in ax.get_yticklabels():
        label.set_fontweight("bold")

    # Clean legend on first panel
    if i == 0:
        legend_elements = [
            Line2D([0], [0], color="black", lw=2.5, ls="-", marker="o", ms=8, label="Top"),
            Line2D([0], [0], color="black", lw=2.5, ls="--", marker="s", ms=7, label="Bottom")
        ]
        ax.legend(
            handles=legend_elements, frameon=False, loc="upper right", fontsize=BASE_FONT,
            handletextpad=0.8, borderpad=0.5
        )

# X-Axis Labels and Styling
axes[2].set_xlabel("Sampling Campaign", fontweight="bold", labelpad=18, fontsize=BASE_FONT + 2)
axes[2].set_xticks(range(len(sampled_months)))
axes[2].set_xticklabels(sampled_months, fontweight="bold", fontsize=BASE_FONT)

# ============================================================
# 5) EXPORT FIGURES (SUPPLEMENTARY FIGURE 6)
# ============================================================
if DO_SAVE:
    png_out = SAVE_DIR / "supp_fig06_ghg_vertical_profiles_2023.png"
    fig.savefig(png_out, dpi=600, bbox_inches="tight")
    print(f"✓ Saved: {png_out.name}")

    for dpi in SAVE_DPIS:
        tiff_out = SAVE_DIR / f"supp_fig06_ghg_vertical_profiles_2023_{dpi}dpi.tiff"
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

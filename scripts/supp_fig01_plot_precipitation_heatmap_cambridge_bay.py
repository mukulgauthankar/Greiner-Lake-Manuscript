from pathlib import Path
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

# ============================================================
# 0) REPOSITORY PATHS & SAVING SETUP
# ============================================================
BASE_DIR = Path(__file__).resolve().parent.parent if Path(__file__).resolve().parent.name == "scripts" else Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
SAVE_DIR = BASE_DIR / "figures"
SAVE_DIR.mkdir(parents=True, exist_ok=True)

DO_SAVE = True
SAVE_DPIS = [600, 1200]

# ============================================================
# 1) GLOBAL STYLE / RC PARAMS
# ============================================================
BASE_FONT = 12
plt.rcParams.update({
    "font.family": "DejaVu Sans",
    "font.size": BASE_FONT,
    "axes.titlesize": BASE_FONT + 2,
    "axes.labelsize": BASE_FONT + 1,
    "xtick.labelsize": BASE_FONT,
    "ytick.labelsize": BASE_FONT,
    "figure.dpi": 150,
})

# ============================================================
# 2) DATA LOADING & PREPARATION
# ============================================================
csv_path = DATA_DIR / "cambridge_bay_precipitation_data_heatmap.csv"
if not csv_path.exists():
    raise FileNotFoundError(f"Missing file: {csv_path.name}. Make sure it is placed in the data/ folder.")

# Read wide-format CSV directly
df = pd.read_csv(csv_path, index_col="Year")

# Ensure columns follow standard calendar month order
month_order = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
heatmap_data = df.reindex(columns=month_order)

# ============================================================
# 3) PLOT GENERATION
# ============================================================
fig, ax = plt.subplots(figsize=(11, 4.5))

sns.heatmap(
    heatmap_data, 
    annot=True, 
    fmt=".1f", 
    cmap="Blues", 
    linewidths=0.5, 
    cbar_kws={"label": "Precipitation (mm)"},
    ax=ax
)

ax.set_title("Cambridge Bay Annual Precipitation (mm)", fontsize=BASE_FONT + 2, pad=15, weight="bold")
ax.set_xlabel("Month", fontsize=BASE_FONT + 1, weight="bold")
ax.set_ylabel("Year", fontsize=BASE_FONT + 1, weight="bold")
ax.tick_params(axis="x", labelrotation=0)
ax.tick_params(axis="y", labelrotation=0)

plt.tight_layout()

# ============================================================
# 4) EXPORT FIGURES (SUPPLEMENTARY FIGURE 1)
# ============================================================
if DO_SAVE:
    png_out = SAVE_DIR / "supp_fig01_cambridge_bay_precipitation_heatmap.png"
    fig.savefig(png_out, dpi=600, bbox_inches="tight")
    print(f"✓ Saved: {png_out.name}")

    for dpi in SAVE_DPIS:
        tiff_out = SAVE_DIR / f"supp_fig01_cambridge_bay_precipitation_heatmap_{dpi}dpi.tiff"
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

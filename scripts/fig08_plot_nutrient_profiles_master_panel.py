from pathlib import Path
import textwrap
import warnings
import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator
import numpy as np
import pandas as pd

# 1) PREVENT WARNINGS
warnings.filterwarnings("ignore", category=UserWarning, module="openpyxl")
warnings.filterwarnings("ignore", category=FutureWarning, module="pandas")

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
# 1) GLOBAL STYLE (PUBLICATION STANDARDS)
# ============================================================
BASE_FONT = 16
plt.rcParams.update({
    "font.family": "DejaVu Sans",
    "font.size": BASE_FONT,
    "axes.titlesize": BASE_FONT + 2,
    "axes.labelsize": BASE_FONT + 2,
    "xtick.labelsize": BASE_FONT,
    "ytick.labelsize": BASE_FONT,
    "axes.linewidth": 1.8,
    "figure.dpi": 150,
})

# ============================================================
# 2) DATA LOADING & MERGING
# ============================================================
file_path = DATA_DIR / "TP TN DOC CHL-A.xlsx"
if not file_path.exists():
    raise FileNotFoundError(f"Missing file: {file_path.name}. Make sure it is placed in the data/ folder.")

df_main = pd.read_excel(file_path, sheet_name="Sheet1", engine="openpyxl")
df_main = df_main[df_main["Depth_m"].isin([0, 2, 4, 6, 8, 10])].copy()
df_main["Depth_m"] = df_main["Depth_m"].replace({8: 10})

# Structured a440 dataset (robust dictionary definition)
a440_records = [
    ("CB22_August", 0, 0.287), ("CB22_August", 2, 0.357), ("CB22_August", 4, 0.341),
    ("CB22_August", 6, 0.298), ("CB22_August", 10, 0.333),
    ("CB22_November", 0, 0.743), ("CB22_November", 2, 0.636), ("CB22_November", 4, 0.492),
    ("CB22_November", 6, 0.836), ("CB22_November", 10, 0.613),
    ("CB23_April", 2, 0.605), ("CB23_April", 4, 0.585), ("CB23_April", 6, 0.659), ("CB23_April", 10, 0.712),
    ("CB23_May", 2, 0.640), ("CB23_May", 4, 0.671), ("CB23_May", 6, 0.707), ("CB23_May", 10, 0.693),
    ("CB23_June", 2, 0.481), ("CB23_June", 4, 0.555), ("CB23_June", 6, 0.756), ("CB23_June", 10, 0.675),
    ("CB23_Early July", 0, 0.494), ("CB23_Early July", 2, 0.814), ("CB23_Early July", 4, 0.926),
    ("CB23_Early July", 6, 0.927), ("CB23_Early July", 10, 0.946),
    ("CB23_Late July", 0, 0.565), ("CB23_Late July", 2, 0.635), ("CB23_Late July", 4, 0.672),
    ("CB23_Late July", 6, 0.633), ("CB23_Late July", 10, 0.653),
    ("CB23_August", 0, 0.445), ("CB23_August", 2, 0.448), ("CB23_August", 4, 0.459),
    ("CB23_August", 6, 0.484), ("CB23_August", 10, 0.454)
]

df_a440 = pd.DataFrame(a440_records, columns=["Campaign", "Depth_m", "a440"])

cmap = {
    "CB22_August": "Aug_2022", "CB22_November": "Nov_2022", "CB23_April": "Apr_2023",
    "CB23_May": "May_2023", "CB23_June": "June_2023", "CB23_Early July": "Early_July_2023",
    "CB23_Late July": "Late_July_2023", "CB23_August": "Aug_2023"
}
df_a440["Month_Year"] = df_a440["Campaign"].map(cmap)
df_a440["Depth_m"] = df_a440["Depth_m"].replace({8: 10})

# Final merge
df = pd.merge(df_main, df_a440[["Month_Year", "Depth_m", "a440"]], on=["Month_Year", "Depth_m"], how="outer")

# ============================================================
# 3) STATISTICAL LOOKUPS (SEM BARS)
# ============================================================
DOC_STATS = [
    ("Aug_2022", 0, 2.53, 0.000, 1), ("Aug_2022", 4, 2.83, 0.000, 1), ("Aug_2022", 10, 2.46, 0.000, 1),
    ("Nov_2022", 0, 4.125, 0.235, 2), ("Nov_2022", 2, 4.155, 0.116, 2), ("Nov_2022", 4, 3.75, 0.300, 2), ("Nov_2022", 6, 4.06, 0.113, 2), ("Nov_2022", 10, 4.14, 0.127, 2),
    ("Apr_2023", 0, 5.51, 0.424, 2), ("Apr_2023", 4, 5.49, 0.014, 2), ("Apr_2023", 6, 6.155, 0.045, 2), ("Apr_2023", 10, 6.15, 0.014, 2),
    ("May_2023", 0, 4.885, 0.206, 2), ("May_2023", 4, 5.475, 0.135, 2), ("May_2023", 6, 6.27, 0.170, 2), ("May_2023", 10, 6.04, 0.030, 2),
    ("June_2023", 0, 4.17, 0.130, 2), ("June_2023", 4, 5.16, 0.040, 2), ("June_2023", 6, 6.225, 0.055, 2), ("June_2023", 10, 6.40, 0.050, 2),
    ("Early_July_2023", 0, 7.34, 0.690, 2), ("Early_July_2023", 2, 12.66, 0.155, 2), ("Early_July_2023", 4, 15.05, 0.130, 2), ("Early_July_2023", 6, 16.74, 0.075, 2), ("Early_July_2023", 10, 23.79, 0.920, 2),
    ("Late_July_2023", 0, 11.92, 0.565, 2), ("Late_July_2023", 2, 12.38, 0.230, 2), ("Late_July_2023", 4, 12.82, 0.375, 2), ("Late_July_2023", 6, 12.00, 0.615, 2), ("Late_July_2023", 10, 13.80, 0.640, 2),
    ("Aug_2023", 0, 3.65, 0.050, 2), ("Aug_2023", 2, 3.55, 0.050, 2), ("Aug_2023", 4, 3.60, 0.100, 2), ("Aug_2023", 6, 3.70, 0.100, 2), ("Aug_2023", 10, 3.60, 0.000, 2),
]

CHLA_STATS = [
    ("Aug_2022", 0, 1.8796, 0.0410, 3), ("Aug_2022", 2, 1.9118, 0.1093, 3), ("Aug_2022", 4, 2.3266, 0.1390, 3), ("Aug_2022", 6, 1.9058, 0.0970, 3), ("Aug_2022", 10, 2.0122, 0.1086, 3),
    ("Nov_2022", 0, 1.5851, 0.0160, 3), ("Nov_2022", 2, 1.4462, 0.0624, 3), ("Nov_2022", 4, 0.7640, 0.0308, 3), ("Nov_2022", 6, 0.6724, 0.0793, 3), ("Nov_2022", 10, 0.5065, 0.0210, 3),
    ("Apr_2023", 2, 0.8172, 0.0266, 3), ("Apr_2023", 4, 0.1677, 0.0044, 3), ("Apr_2023", 6, 0.2329, 0.0095, 3), ("Apr_2023", 10, 0.1534, 0.0266, 3),
    ("May_2023", 2, 1.4062, 0.0957, 3), ("May_2023", 4, 1.2998, 0.0385, 3), ("May_2023", 6, 0.5073, 0.0501, 3), ("May_2023", 10, 0.3357, 0.0154, 3),
    ("June_2023", 2, 1.9442, 0.0457, 3), ("June_2023", 4, 2.4836, 0.0343, 3), ("June_2023", 6, 2.8101, 0.0691, 3), ("June_2023", 10, 1.7096, 0.1083, 3),
    ("Early_July_2023", 0, 1.0523, 0.1067, 3), ("Early_July_2023", 2, 1.4074, 0.0840, 3), ("Early_July_2023", 4, 2.9780, 0.2685, 3), ("Early_July_2023", 6, 6.2012, 0.2020, 3), ("Early_July_2023", 10, 11.2390, 1.3021, 3),
    ("Late_July_2023", 0, 0.7379, 0.0462, 3), ("Late_July_2023", 2, 0.8872, 0.1449, 3), ("Late_July_2023", 4, 1.5746, 0.0627, 3), ("Late_July_2023", 6, 2.4132, 0.0025, 3), ("Late_July_2023", 10, 2.5893, 0.1944, 3),
    ("Aug_2023", 0, 1.3585, 0.0411, 3), ("Aug_2023", 2, 1.3956, 0.0308, 3), ("Aug_2023", 4, 1.4522, 0.0556, 3), ("Aug_2023", 6, 1.5542, 0.0258, 3), ("Aug_2023", 10, 1.3234, 0.0142, 3),
]

def build_sem_lookup(stats_list):
    return {(m, d): float(s) for m, d, mn, s, n in stats_list if not np.isnan(s)}

SEM_LOOKUPS = {
    "DOC": build_sem_lookup(DOC_STATS),
    "Chlorophyll_a": build_sem_lookup(CHLA_STATS),
    "a440": {} 
}

# ============================================================
# 4) ICE & SNOW DATA
# ============================================================
ice_thickness_m = np.array([0, 0.55, 1.80, 1.88, 1.70, 0.70, 0, 0])
snow_thickness_m = np.array([0, 0.05, 0.30, 0.40, 0.05, 0, 0, 0])
x_months = np.arange(len(ice_thickness_m))

# ============================================================
# 5) MASTER PLOTTING FUNCTION
# ============================================================
panel_months = ["Aug_2022", "Nov_2022", "Apr_2023", "May_2023", "June_2023", "Early_July_2023", "Late_July_2023", "Aug_2023"]
panel_titles = ["Aug 2022", "Nov 2022", "Apr 2023", "May 2023", "Jun 2023", "Early July 2023", "Late July 2023", "Aug 2023"]
titles_wrapped = ["\n".join(textwrap.wrap(t, 10)) for t in panel_titles]
depths_sorted = [10, 6, 4, 2, 0]
y_positions = np.arange(len(depths_sorted))

param_colors = {"Chlorophyll_a": "#1c9112", "DOC": "#B25708", "a440": "#9C3F58"}

def plot_master_panel(params):
    fig = plt.figure(figsize=(12.0, 14.0))
    gs = fig.add_gridspec(4, 8, hspace=0.45, wspace=0.25, left=0.08, right=0.98, top=0.92, bottom=0.08, height_ratios=[2, 3, 3, 3])

    # --- ROW 0: ICE & SNOW BANNER ---
    ax_ice = fig.add_subplot(gs[0, :])
    ax_ice.fill_between(x_months, 0, snow_thickness_m, color="#f0f0f0", alpha=1.0, label="Snow", edgecolor="black")
    ax_ice.fill_between(x_months, 0, -ice_thickness_m, color="#3c9df2", alpha=0.7, label="Ice", edgecolor="black")
    ax_ice.axhline(y=0, color="black", linewidth=2.0)
    
    ax_ice.set_ylabel("Thick. (m)", fontweight="bold")
    ax_ice.set_yticks([-2.0, -1.0, 0, 0.5])
    ax_ice.set_yticklabels(["2.0", "1.0", "0", "0.5"]) 
    ax_ice.set_xticks(x_months)
    ax_ice.set_xticklabels([])
    ax_ice.spines[["top", "right", "bottom"]].set_visible(False)
    ax_ice.legend(loc="center left", bbox_to_anchor=(1.0, 0.5), frameon=False)
    ax_ice.set_title("Ice & Snow Dynamics", fontweight="bold", pad=20, loc="left")

    # --- ROWS 1-3: NUTRIENT/CDOM PANELS ---
    for row_idx, (col, label) in enumerate(params, start=1):
        g_max = df[col].max() * 1.15
        sem_map = SEM_LOOKUPS.get(col, {})
        
        for col_idx, (m_code, title) in enumerate(zip(panel_months, titles_wrapped)):
            ax = fig.add_subplot(gs[row_idx, col_idx])
            sub = df[df["Month_Year"] == m_code]
            
            means, errs = [], []
            for d in depths_sorted:
                sub_d = sub[sub["Depth_m"] == d]
                if not sub_d.empty and not pd.isna(sub_d[col].iloc[0]):
                    means.append(sub_d[col].iloc[0])
                    errs.append(sem_map.get((m_code, d), 0))
                else:
                    means.append(np.nan)
                    errs.append(0)
            
            current_errs = None if col == "a440" else errs
            
            bars = ax.barh(
                y_positions, np.nan_to_num(means), xerr=current_errs, color=param_colors[col], 
                edgecolor="black", error_kw=dict(linewidth=1.2, capsize=3, capthick=1.2)
            )
            
            for k, b in enumerate(bars):
                if np.isnan(means[k]):
                    b.set_alpha(0)

            ax.set_xlim(0, g_max)
            ax.xaxis.set_major_locator(MaxNLocator(3))
            
            if col_idx == 0:
                ax.set_yticks(y_positions)
                ax.set_yticklabels([str(d) for d in depths_sorted])
                ax.set_ylabel("Depth (m)", fontweight="bold")
            else:
                ax.set_yticklabels([])
            
            if row_idx == 1:
                ax.set_title(title, fontweight="bold", fontsize=14, pad=10)
            
            ax.spines[["top", "right"]].set_visible(False)
            ax.xaxis.grid(True, linestyle=":", alpha=0.7)

        fig.text(0.53, ax.get_position().y0 - 0.05, label, ha="center", fontweight="bold", fontsize=14)
    
    return fig

# ============================================================
# 6) EXECUTION & EXPORT
# ============================================================
combined_params = [
    ("Chlorophyll_a", r"Chl-$a$ ($\mu\mathrm{g}\ \mathrm{L}^{-1}$)"),
    ("DOC", r"DOC ($\mathrm{mg}\ \mathrm{L}^{-1}$)"),
    ("a440", r"$a_{440}$ ($\mathrm{m}^{-1}$)")
]

fig_obj = plot_master_panel(combined_params)

if DO_SAVE:
    png_out = SAVE_DIR / "nutrient_profiles_master_panel.png"
    fig_obj.savefig(png_out, dpi=600, bbox_inches="tight")
    print(f"✓ Saved: {png_out.name}")

    for dpi in SAVE_DPIS:
        tiff_out = SAVE_DIR / f"nutrient_profiles_master_panel_{dpi}dpi.tiff"
        fig_obj.savefig(
            tiff_out, 
            dpi=dpi, 
            format="tiff", 
            pil_kwargs={"compression": "tiff_lzw"}, 
            bbox_inches="tight"
        )
        print(f"✓ Saved: {tiff_out.name}")

plt.show()
plt.close(fig_obj)

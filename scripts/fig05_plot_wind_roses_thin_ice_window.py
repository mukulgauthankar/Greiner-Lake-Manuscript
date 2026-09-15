from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.patches import Patch
from windrose import WindroseAxes

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
# 1) GLOBAL FONT / STYLE
# ============================================================
BASE_FONT = 12

plt.rcParams.update({
    "font.family": "DejaVu Sans",
    "font.size": BASE_FONT,
    "axes.titlesize": BASE_FONT + 2,
    "axes.labelsize": BASE_FONT + 1,
    "xtick.labelsize": BASE_FONT - 1,
    "ytick.labelsize": BASE_FONT - 1,
    "legend.fontsize": BASE_FONT + 2,
    "axes.linewidth": 1.2,
})

# ============================================================
# 2) INPUT & DATA LOADING
# ============================================================
clean_path = DATA_DIR / "cambridge_bay_wind_clean_2017_2025.csv"
if not clean_path.exists():
    raise FileNotFoundError(f"Missing file: {clean_path.name}. Make sure it is placed in the data/ folder.")

SPEED_BINS = [0, 5, 10, 15, 20, 25, 30, 75]

ROSE_COLORS = [
    "#e0f3f8", "#91bfdb", "#4575b4",
    "#fee090", "#fdae61", "#f46d43",
    "#d73027", "#7f0000"
]

SPEED_LABELS = [
    "0–4", "5–9", "10–14", "15–19",
    "20–24", "25–29", "30–74", "≥75"
]

df = pd.read_csv(clean_path, parse_dates=["datetime"])
df = df.set_index("datetime").sort_index()

df["ws"] = pd.to_numeric(df["ws"], errors="coerce")
df["wd"] = pd.to_numeric(df["wd"], errors="coerce")
df = df.dropna(subset=["ws", "wd"])

# Keep valid directions
df = df[(df["wd"] >= 0) & (df["wd"] < 360)]

# ============================================================
# 3) THIN-ICE WINDOW: Nov–Feb + winter-year labels
# ============================================================
def winter_year_label(ts):
    y = ts.year
    return f"{y}-{y+1}" if ts.month in (11, 12) else f"{y-1}-{y}"

def prepare_nov_feb(df_in, drop_winters=("2016-2017", "2024-2025", "2025-2026")):
    sub = df_in[df_in.index.month.isin([11, 12, 1, 2])].copy()
    sub["winter_year"] = [winter_year_label(t) for t in sub.index]
    sub = sub[~sub["winter_year"].isin(drop_winters)].copy()
    return sub

df_nf = prepare_nov_feb(df, drop_winters=("2016-2017", "2024-2025", "2025-2026"))

# ============================================================
# 4) PLOT: WIND ROSES
# ============================================================
def plot_nov_feb_wind_roses_by_winter(df_nf_in):
    winters = sorted(df_nf_in["winter_year"].unique())
    if len(winters) == 0:
        print("No winters to plot.")
        return

    n_cols = 3
    n = len(winters)
    n_rows = (n + n_cols - 1) // n_cols

    fig = plt.figure(figsize=(14, 4.6 * n_rows))

    for i, wy in enumerate(winters, start=1):
        d = df_nf_in[df_nf_in["winter_year"] == wy]
        ax = fig.add_subplot(n_rows, n_cols, i, projection="windrose")

        if not d.empty:
            ax.bar(
                d["wd"], d["ws"],
                bins=SPEED_BINS,
                normed=True,
                opening=0.8,
                colors=ROSE_COLORS,
                edgecolor="none",
            )

        ax.set_title(f"Nov–Feb {wy}", pad=12, fontweight="bold")
        ax.tick_params(labelsize=BASE_FONT - 1)

    handles = [Patch(facecolor=c, edgecolor="none") for c in ROSE_COLORS]
    total_slots = n_rows * n_cols
    empty_slots = list(range(n + 1, total_slots + 1))

    if len(empty_slots) >= 1:
        leg_ax = fig.add_subplot(n_rows, n_cols, empty_slots[0])
        leg_ax.axis("off")
        leg = leg_ax.legend(
            handles,
            SPEED_LABELS,
            title="Wind speed (km/h)",
            loc="center left",
            frameon=False,
            ncol=1,
            handlelength=1.4,
            labelspacing=0.9,
            borderaxespad=0.0,
        )
        leg.get_title().set_fontsize(BASE_FONT + 2)
        leg.get_title().set_fontweight("bold")

    if len(empty_slots) >= 2:
        ax_off = fig.add_subplot(n_rows, n_cols, empty_slots[1])
        ax_off.axis("off")

    fig.suptitle(
        "Cambridge Bay Wind Roses (Nov–Feb only; thin-ice window)",
        fontsize=BASE_FONT + 4,
        fontweight="bold",
        y=0.985,
    )

    fig.subplots_adjust(
        left=0.05,
        right=0.98,
        top=0.86,
        bottom=0.06,
        wspace=0.12,
        hspace=0.55,
    )

    if DO_SAVE:
        png_out = SAVE_DIR / "wind_roses_Cambridge_Bay_Nov_Feb.png"
        fig.savefig(png_out, dpi=600, bbox_inches="tight")
        print(f"✓ Saved: {png_out.name}")

        for dpi_val in SAVE_DPIS:
            tiff_out = SAVE_DIR / f"wind_roses_Cambridge_Bay_Nov_Feb_{dpi_val}dpi.tiff"
            fig.savefig(tiff_out, dpi=dpi_val, bbox_inches="tight", format="tiff")
            print(f"✓ Saved: {tiff_out.name}")

    plt.show()
    plt.close(fig)

# ============================================================
# 5) EXECUTION
# ============================================================
plot_nov_feb_wind_roses_by_winter(df_nf)

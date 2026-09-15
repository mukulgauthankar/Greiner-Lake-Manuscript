import io
from pathlib import Path
import warnings
import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import pandas as pd

warnings.filterwarnings("ignore", category=UserWarning, module="openpyxl")

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
# 1) RC PARAMS / PLOT STYLING CONFIGURATION
# ============================================================
BASE_FONT = 17
plt.rcParams.update({
    "figure.facecolor": "white",
    "savefig.facecolor": "white",
    "axes.facecolor": "white",
    "font.family": "DejaVu Sans",
    "font.size": BASE_FONT,
    "axes.titlesize": BASE_FONT + 2,
    "axes.labelsize": BASE_FONT + 2,
    "xtick.labelsize": BASE_FONT,
    "ytick.labelsize": BASE_FONT,
    "legend.fontsize": BASE_FONT,
    "axes.linewidth": 1.8,
    "xtick.direction": "out",
    "ytick.direction": "out",
})

# ============================================================
# 2) FILE LOADING & DATA INGESTION
# ============================================================
file_path = DATA_DIR / "Greiner_Water_Levels for python.xlsx"
if not file_path.exists():
    raise FileNotFoundError(f"Missing file: {file_path.name}. Make sure it is placed in the data/ folder.")

with open(file_path, "rb") as f:
    excel_stream = io.BytesIO(f.read())

xl = pd.ExcelFile(excel_stream, engine="openpyxl")

# Detect sheets to plot (excluding readme/notes)
available_sheets = [
    s
    for s in xl.sheet_names
    if not any(
        k in s.lower()
        for k in ["readme", "read me", "info", "note", "metadata"]
    )
]
print(f"Detected {len(available_sheets)} sheets to plot: {available_sheets}")

# Color mapping
cmap = plt.get_cmap("tab10")
colors = [cmap(i % 10) for i in range(len(available_sheets))]

fig, ax = plt.subplots(figsize=(15, 7))

# Window setting: 168 hours = 7-day rolling average
SMOOTHING_WINDOW_HOURS = 168

# ============================================================
# 3) DATA PROCESSING & PLOTTING
# ============================================================
for sheet, color in zip(available_sheets, colors):
    df = xl.parse(sheet)

    time_col = [
        c
        for c in df.columns
        if any(k in str(c).lower() for k in ["time", "date", "timestamp"])
    ][0]
    level_col = [
        c
        for c in df.columns
        if any(
            k in str(c).lower()
            for k in ["mean water level", "level", "depth", "water"]
        )
    ][0]

    df[time_col] = pd.to_datetime(df[time_col], errors="coerce")
    df = df.dropna(subset=[time_col]).sort_values(time_col).reset_index(drop=True)

    # 7-day rolling average
    df["Smoothed_Level"] = (
        df[level_col]
        .rolling(window=SMOOTHING_WINDOW_HOURS, center=True, min_periods=1)
        .mean()
    )

    # Sequential seasonal alignment
    start_year = df[time_col].min().year

    def align_timestamp(dt):
        target_year = 2019 if dt.year == start_year else 2020
        if dt.month == 2 and dt.day == 29 and target_year == 2019:
            return dt.replace(year=target_year, day=28)
        return dt.replace(year=target_year)

    df["Aligned_Time"] = df[time_col].apply(align_timestamp)
    df = df.sort_values("Aligned_Time").reset_index(drop=True)

    ax.plot(
        df["Aligned_Time"],
        df["Smoothed_Level"],
        label=sheet,
        color=color,
        linewidth=2.5,
        alpha=0.9,
    )

# Formatting
ax.xaxis.set_major_locator(mdates.MonthLocator())
ax.xaxis.set_major_formatter(mdates.DateFormatter("%b"))
ax.set_xlim(pd.Timestamp("2019-08-01"), pd.Timestamp("2020-08-31"))

ax.axhline(0, color="black", linestyle="--", linewidth=1.2, alpha=0.6)
ax.set_xlabel("Month of Deployment (Aug → Aug)", fontweight="bold")
ax.set_ylabel("Water Level (cm)", fontweight="bold")

ax.legend(loc="upper left", bbox_to_anchor=(0.22, 0.92), frameon=False)
plt.tight_layout()

# ============================================================
# 4) EXPORT FIGURES
# ============================================================
if DO_SAVE:
    png_out = SAVE_DIR / "water_level_cycles_multiyear.png"
    fig.savefig(png_out, dpi=600, bbox_inches="tight")
    print(f"✓ Saved: {png_out.name}")

    for dpi in SAVE_DPIS:
        tiff_out = SAVE_DIR / f"water_level_cycles_multiyear_{dpi}dpi.tiff"
        fig.savefig(tiff_out, dpi=dpi, format="tiff", bbox_inches="tight")
        print(f"✓ Saved: {tiff_out.name}")

plt.show()
plt.close(fig)

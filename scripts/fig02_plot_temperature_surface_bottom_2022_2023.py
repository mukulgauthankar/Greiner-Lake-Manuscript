from pathlib import Path
import re
import warnings
import calendar
import pandas as pd
import matplotlib.pyplot as plt

warnings.filterwarnings("ignore", category=UserWarning, module="openpyxl")
warnings.filterwarnings("ignore", category=FutureWarning, module="pandas")

# ============================================================
# 0) REPOSITORY PATHS & SAVING SETUP
# ============================================================
# Resolves the repository root whether the script is run from repo root or inside scripts/
BASE_DIR = Path(__file__).resolve().parent.parent if Path(__file__).resolve().parent.name == "scripts" else Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
SAVE_DIR = BASE_DIR / "figures"
SAVE_DIR.mkdir(parents=True, exist_ok=True)

DO_SAVE = True
SAVE_DPIS = [600, 1200]
SAVE_FORMAT = "tiff"

def safe_fname(s: str) -> str:
    return re.sub(r"[^A-Za-z0-9]+", "_", str(s)).strip("_")

def next_available_path(path: Path) -> Path:
    if not path.exists():
        return path
    base = path.stem
    ext = path.suffix
    parent = path.parent
    k = 1
    while True:
        cand = parent / f"{base}_v{str(k).zfill(2)}{ext}"
        if not cand.exists():
            return cand
        k += 1

# ============================================================
# 1) STYLE
# ============================================================
BASE_FONT = 12
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
    "legend.title_fontsize": BASE_FONT,
    "axes.linewidth": 1.8,
    "xtick.major.width": 1.6,
    "ytick.major.width": 1.6,
    "xtick.major.size": 4.0,
    "ytick.major.size": 4.0,
    "xtick.direction": "out",
    "ytick.direction": "out",
    "axes.grid": False,
})
plt.rcParams["mathtext.fontset"] = "dejavusans"

# ============================================================
# 2) FILES (LOOKING IN data/ DIRECTORY)
# ============================================================
file_info = [
    (DATA_DIR / "Greiner Surface mooring 2022-2023.xlsx", "Surface", "2022-2023"),
    (DATA_DIR / "Greiner Bottom mooring 2022-2023.xlsx", "Bottom", "2022-2023"),
]

# ============================================================
# 3) TARGET SETTINGS
# ============================================================
TARGET_YEAR = "2022-2023"
PARAM = "Temperature"
UNIT = "°C"

param_axis_label = r"Temperature (°C)"
param_title_label = "Temperature"
TEMP_YLIM = (-2, 18)

# ============================================================
# 4) AUG → AUG AXIS SETTINGS
# ============================================================
ANCHOR_MONTH = 8
ANCHOR_DAY = 1

RESAMPLE_NONPAR = True
NONPAR_RESAMPLE_RULE = "1D"

KEEP_ONLY_MAIN_SEGMENT = True
MIN_MAIN_SEGMENT_DAYS = 60
GAP_MULTIPLIER = 6

# ============================================================
# 5) HELPERS
# ============================================================
def parse_year_window(year_label: str):
    y0, y1 = year_label.split("-")
    start = pd.Timestamp(int(y0), ANCHOR_MONTH, ANCHOR_DAY)
    end = pd.Timestamp(int(y1), ANCHOR_MONTH, ANCHOR_DAY)
    return start, end

def lake_doy(dt):
    if pd.isna(dt):
        return float("nan")
    anchor = pd.Timestamp(year=dt.year, month=ANCHOR_MONTH, day=ANCHOR_DAY)
    if dt < anchor:
        anchor = pd.Timestamp(year=dt.year - 1, month=ANCHOR_MONTH, day=ANCHOR_DAY)
    delta = dt - anchor
    return delta.days + delta.seconds / 86400.0

def lake_month_ticks(ref_year=2021):
    ticks, labels = [], []
    months = list(range(ANCHOR_MONTH, 13)) + list(range(1, ANCHOR_MONTH))
    years = [ref_year] * len(range(ANCHOR_MONTH, 13)) + [ref_year + 1] * len(range(1, ANCHOR_MONTH))
    for m, y in zip(months, years):
        dt0 = pd.Timestamp(y, m, 1)
        ticks.append(lake_doy(dt0))
        labels.append(calendar.month_abbr[m])
    return ticks, labels

def resample_if_needed(df_y, param):
    df_y = df_y.sort_values("Time").copy()
    yr = df_y["Year"].iloc[0]

    if RESAMPLE_NONPAR:
        out = (
            df_y.set_index("Time")[[param]]
            .resample(NONPAR_RESAMPLE_RULE).mean()
            .reset_index()
        )
        out["Year"] = yr
        return out

    return df_y

def adaptive_gap_hours(df_y):
    if df_y.shape[0] < 3:
        return None
    dt_hours = (df_y["Time"].sort_values().diff().dt.total_seconds().div(3600.0)).dropna()
    if dt_hours.empty:
        return None
    med = dt_hours.median()
    return max(3.0, GAP_MULTIPLIER * med)

def segment_filter(df_plot, param):
    df_plot = df_plot.sort_values(["Year", "Time"]).copy()

    th = adaptive_gap_hours(df_plot[["Time", param]].dropna())
    if th is not None:
        gap_hours = df_plot["Time"].diff().dt.total_seconds().div(3600.0)
        breaks = gap_hours > th
        df_plot.loc[breaks, param] = float("nan")

    return df_plot

def normalize_columns(df):
    df.columns = (
        df.columns.astype(str)
        .str.replace(r"\u202f|\xa0", " ", regex=True)
        .str.strip()
    )
    lower_map = {c.lower(): c for c in df.columns}
    if "time" in lower_map:
        df.rename(columns={lower_map["time"]: "Time"}, inplace=True)
    return df

# ============================================================
# 6) LOAD DATA
# ============================================================
compiled = []
for filepath, depth, year in file_info:
    try:
        if not filepath.exists():
            print(f"⚠️ Missing file: {filepath.name} — make sure it is placed in the data/ directory.")
            continue

        df = pd.read_excel(filepath, sheet_name="Data", header=1)
        df = normalize_columns(df)

        df["Time"] = pd.to_datetime(df["Time"], errors="coerce")
        df = df.dropna(subset=["Time"]).copy()

        start, end = parse_year_window(year)
        df = df[(df["Time"] >= start) & (df["Time"] < end)].copy()

        df["Depth"] = depth
        df["Year"] = year

        compiled.append(df)

    except Exception as e:
        print(f"⚠️ Skipping {filepath.name}: {e}")

if not compiled:
    raise FileNotFoundError("No mooring data loaded. Verify that the Excel files exist in data/.")

full_df = pd.concat(compiled, ignore_index=True)
surface_df = full_df[full_df["Depth"] == "Surface"].copy()
bottom_df = full_df[full_df["Depth"] == "Bottom"].copy()

# ============================================================
# 7) BUILD + PLOT (SURFACE VS BOTTOM OVERLAY)
# ============================================================
def build_lake_year_df(df, param):
    df_y = df.copy()
    df_y[param] = pd.to_numeric(df_y[param], errors="coerce")
    df_y = df_y.dropna(subset=["Time", param]).copy()
    if df_y.empty:
        return pd.DataFrame()

    df_y = resample_if_needed(df_y, param)
    df_y["LakeDOY"] = df_y["Time"].map(lake_doy)

    return df_y[["Time", "LakeDOY", "Year", param]].copy()

def plot_surface_vs_bottom(surface_df, bottom_df, param, unit):
    df_s = build_lake_year_df(surface_df, param)
    df_b = build_lake_year_df(bottom_df, param)

    df_s = df_s[df_s[param] <= 16.5]
    df_b = df_b[df_b[param] <= 16.5]

    df_s = segment_filter(df_s, param)
    df_b = segment_filter(df_b, param)

    fig, ax = plt.subplots(figsize=(12.0, 5.4))

    ax.plot(df_s["LakeDOY"], df_s[param], color="#d95f02", lw=2.8, label="Surface")
    ax.plot(df_b["LakeDOY"], df_b[param], color="#1f78b4", lw=2.8, label="Bottom")

    ax.set_title(f"{param_title_label} — Surface vs Bottom ({TARGET_YEAR})", fontweight="bold")
    ax.set_xlabel("Lake-year (Aug → Aug)", fontweight="bold")
    ax.set_ylabel(param_axis_label, fontweight="bold")
    ax.set_ylim(TEMP_YLIM)

    ticks, labels = lake_month_ticks()
    ax.set_xticks(ticks)
    ax.set_xticklabels(labels)

    ax.legend(frameon=False)
    fig.tight_layout()

    if DO_SAVE:
        base = safe_fname(f"Temperature_Surface_vs_Bottom_{TARGET_YEAR}_Aug_to_Aug")
        for dpi in SAVE_DPIS:
            target_path = SAVE_DIR / f"{base}_{dpi}dpi.{SAVE_FORMAT}"
            out = next_available_path(target_path)
            fig.savefig(out, dpi=dpi, format=SAVE_FORMAT, bbox_inches="tight")
            print(f"✓ Saved: {out}")

    plt.show()
    plt.close(fig)

# ============================================================
# 8) RUN
# ============================================================
plot_surface_vs_bottom(surface_df, bottom_df, PARAM, UNIT)

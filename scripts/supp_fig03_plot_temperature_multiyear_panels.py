import calendar
from pathlib import Path
import warnings
from matplotlib.lines import Line2D
import matplotlib.pyplot as plt
import pandas as pd

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
# 1) GLOBAL STYLE
# ============================================================
BASE_FONT = 11
X_TICK_ROT = 90

plt.rcParams.update({
    "figure.facecolor": "white",
    "savefig.facecolor": "white",
    "axes.facecolor": "white",
    "font.family": "DejaVu Sans",
    "font.size": BASE_FONT,
    "axes.titlesize": BASE_FONT + 1,
    "axes.labelsize": BASE_FONT + 2,
    "xtick.labelsize": BASE_FONT,
    "ytick.labelsize": BASE_FONT,
    "legend.fontsize": BASE_FONT,
    "legend.title_fontsize": BASE_FONT,
    "axes.linewidth": 1.4,
    "xtick.major.width": 1.2,
    "ytick.major.width": 1.2,
    "xtick.major.size": 3.5,
    "ytick.major.size": 3.5,
    "xtick.direction": "out",
    "ytick.direction": "out",
    "axes.grid": False,
})
plt.rcParams["mathtext.fontset"] = "dejavusans"

# ============================================================
# 2) DATA FILE REGISTRY
# ============================================================
file_info = [
    (DATA_DIR / "Greiner Surface mooring_2017-2018.xlsx", "Surface", "2017-2018"),
    (DATA_DIR / "Greiner Surface mooring_2018-2019.xlsx", "Surface", "2018-2019"),
    (DATA_DIR / "Greiner Surface mooring 2019-2020.xlsx", "Surface", "2019-2020"),
    (DATA_DIR / "Greiner Bottom mooring 2019-2020.xlsx", "Bottom", "2019-2020"),
    (DATA_DIR / "Greiner Surface mooring 2020-2021.xlsx", "Surface", "2020-2021"),
    (DATA_DIR / "Greiner Bottom mooring 2020-2021.xlsx", "Bottom", "2020-2021"),
    (DATA_DIR / "Greiner Surface mooring 2021-2022.xlsx", "Surface", "2021-2022"),
    (DATA_DIR / "Greiner Bottom mooring 2021-2022.xlsx", "Bottom", "2021-2022"),
    (DATA_DIR / "Greiner Surface mooring 2022-2023.xlsx", "Surface", "2022-2023"),
    (DATA_DIR / "Greiner Bottom mooring 2022-2023.xlsx", "Bottom", "2022-2023"),
    (DATA_DIR / "Greiner Surface mooring 2023-2024.xlsx", "Surface", "2023-2024"),
    (DATA_DIR / "Greiner Bottom mooring 2023-2024.xlsx", "Bottom", "2023-2024"),
]

# ============================================================
# 3) PARAMETERS & YEAR COLOR CONFIGURATION
# ============================================================
temp_variants = ["Temperature", "Temp", "temperature", "temp", "Temp (°C)"]

year_order = [
    "2017-2018", "2018-2019", "2019-2020", "2020-2021",
    "2021-2022", "2022-2023", "2023-2024"
]

year_color_map = {
    "2017-2018": "#1b9e77",
    "2018-2019": "#d95f02",
    "2019-2020": "#7570b3",
    "2020-2021": "#e7298a",
    "2021-2022": "#66a61e",
    "2022-2023": "#e6ab02",
    "2023-2024": "#a6761d",
}

ANCHOR_MONTH = 8
ANCHOR_DAY = 1
RESAMPLE_NONPAR = True
NONPAR_RESAMPLE_RULE = "1D"
KEEP_ONLY_MAIN_SEGMENT = True
MIN_MAIN_SEGMENT_DAYS = 60
GAP_MULTIPLIER = 6

# ============================================================
# 4) HELPER FUNCTIONS
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

def lake_doy_tick(dt, anchor_year):
    anchor = pd.Timestamp(anchor_year, ANCHOR_MONTH, ANCHOR_DAY)
    delta = dt - anchor
    return delta.days + delta.seconds / 86400.0

def lake_month_ticks(anchor_year=2021, include_end_aug=True):
    ticks, labels = [], []
    months = list(range(ANCHOR_MONTH, 13)) + list(range(1, ANCHOR_MONTH))
    years = [anchor_year] * len(range(ANCHOR_MONTH, 13)) + [anchor_year + 1] * len(range(1, ANCHOR_MONTH))
    for m, y in zip(months, years):
        dt0 = pd.Timestamp(y, m, 1)
        ticks.append(lake_doy_tick(dt0, anchor_year))
        labels.append(calendar.month_abbr[m])
    if include_end_aug:
        dt_end = pd.Timestamp(anchor_year + 1, ANCHOR_MONTH, 1)
        ticks.append(lake_doy_tick(dt_end, anchor_year))
        labels.append(calendar.month_abbr[ANCHOR_MONTH])
    return ticks, labels

def resample_if_needed(df_y, param):
    df_y = df_y.sort_values("Time").copy()
    if RESAMPLE_NONPAR:
        df_y = df_y.set_index("Time")[[param]].resample(NONPAR_RESAMPLE_RULE).mean().reset_index()
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
    gap_thresh_map = {}
    for yr in df_plot["Year"].unique():
        sub = df_plot[df_plot["Year"] == yr][["Time", param]].dropna().copy()
        th = adaptive_gap_hours(sub)
        if th is not None:
            gap_thresh_map[yr] = th

    gap_hours = df_plot.groupby("Year")["Time"].diff().dt.total_seconds().div(3600.0)
    new_seg = pd.Series(False, index=df_plot.index)
    for yr, th in gap_thresh_map.items():
        idx = df_plot["Year"] == yr
        new_seg.loc[idx] = gap_hours.loc[idx] > th

    df_plot["segment_id"] = new_seg.groupby(df_plot["Year"]).cumsum().fillna(0).astype(int)
    df_plot.loc[new_seg, param] = float("nan")

    if not KEEP_ONLY_MAIN_SEGMENT:
        return df_plot

    seg_stats = (
        df_plot.dropna(subset=[param])
        .groupby(["Year", "segment_id"])["Time"]
        .agg(["min", "max"])
    )
    if seg_stats.empty:
        return df_plot

    seg_stats["duration_days"] = (seg_stats["max"] - seg_stats["min"]).dt.total_seconds() / 86400.0
    keep_idx = seg_stats.groupby(level="Year")["duration_days"].idxmax()
    keep_set = set(keep_idx)

    idx_all = df_plot.set_index(["Year", "segment_id"]).index
    keep_mask = idx_all.isin(keep_set)
    df_plot.loc[~keep_mask, param] = float("nan")

    main_dur = seg_stats.loc[list(keep_set), "duration_days"]
    bad_years = set(main_dur[main_dur < MIN_MAIN_SEGMENT_DAYS].index.get_level_values(0))
    if bad_years:
        df_plot.loc[df_plot["Year"].isin(bad_years), param] = float("nan")

    return df_plot

def build_one_year_one_depth(df, year_label, param):
    df_y = df[df["Year"] == year_label].copy()
    if df_y.empty or param not in df_y.columns:
        return pd.DataFrame()

    df_y[param] = pd.to_numeric(df_y[param], errors="coerce")
    df_y = df_y.dropna(subset=["Time", param]).copy()
    if df_y.empty:
        return pd.DataFrame()

    # Apply sensor cap to remove atmospheric spikes during retrieval/deployment
    df_y = df_y[df_y[param] <= 16.5]

    df_y = resample_if_needed(df_y, param)
    df_y["LakeDOY"] = df_y["Time"].map(lake_doy)

    df_y = df_y[["Time", "LakeDOY", param]].dropna().sort_values("LakeDOY").copy()
    if df_y.empty:
        return pd.DataFrame()

    df_y["Year"] = year_label
    df_y = segment_filter(df_y[["Time", "LakeDOY", "Year", param]].copy(), param)
    return df_y.sort_values("LakeDOY").reset_index(drop=True)

# ============================================================
# 5) DATA INGESTION
# ============================================================
compiled = []
for file_path, depth, year in file_info:
    if not file_path.exists():
        # Handle alternate naming if needed for 2023-2024
        alt_names = [f for f in DATA_DIR.glob(f"*{year}*.xlsx") if depth.lower() in f.name.lower()]
        if alt_names:
            file_path = alt_names[0]
        else:
            print(f"⚠️ Warning: Missing file for {depth} {year}: {file_path.name}")
            continue

    try:
        df = pd.read_excel(file_path, sheet_name="Data", header=1)
        df.columns = (
            df.columns.astype(str)
            .str.replace(r"\u202f|\xa0", " ", regex=True)
            .str.strip()
        )

        lower_map = {c.lower(): c for c in df.columns}
        if "time" in lower_map:
            df.rename(columns={lower_map["time"]: "Time"}, inplace=True)

        df.rename(columns={col: "Temperature" for col in temp_variants if col in df.columns}, inplace=True)

        df["Time"] = pd.to_datetime(df["Time"], errors="coerce")
        df = df.dropna(subset=["Time"]).copy()

        start, end = parse_year_window(year)
        df = df[(df["Time"] >= start) & (df["Time"] < end)].copy()

        df["Depth"] = depth
        df["Year"] = year
        compiled.append(df)

    except Exception as e:
        print(f"⚠️ Skipping {file_path.name}: {e}")

if not compiled:
    raise ValueError("❌ No valid mooring data could be loaded.")

full_df = pd.concat(compiled, ignore_index=True)
surface_df = full_df[full_df["Depth"] == "Surface"].copy()
bottom_df = full_df[full_df["Depth"] == "Bottom"].copy()

# ============================================================
# 6) GLOBAL LIMITS
# ============================================================
def compute_global_lims(surface_df, bottom_df, param):
    vals = []
    for yr in year_order:
        s = build_one_year_one_depth(surface_df, yr, param)
        b = build_one_year_one_depth(bottom_df, yr, param)
        if not s.empty:
            vals.append(pd.to_numeric(s[param], errors="coerce"))
        if not b.empty:
            vals.append(pd.to_numeric(b[param], errors="coerce"))
    if not vals:
        return None
    allv = pd.concat(vals, ignore_index=True)
    allv = allv.replace([float("inf"), float("-inf")], pd.NA).dropna()
    if allv.empty:
        return None
    min_v, max_v = float(allv.min()), float(allv.max())
    pad = (max_v - min_v) * 0.05 if max_v != min_v else 1.0
    return (min_v - pad, max_v + pad)

# ============================================================
# 7) PLOT & EXPORT: 7 PANELS + 8TH OVERLAY PANEL
# ============================================================
def plot_param_year_panels(surface_df, bottom_df, param="Temperature", unit="°C"):
    panel_order = [
        "2017-2018", "2018-2019",
        "2019-2020", "2023-2024",
        "2020-2021", "2021-2022",
        "2022-2023",
    ]

    fig, axes = plt.subplots(4, 2, figsize=(8.6, 10.2), sharex=False, sharey=False)
    axes = axes.flatten()

    ticks, labels = lake_month_ticks(anchor_year=2021, include_end_aug=True)
    x_min, x_max = min(ticks), max(ticks)
    ylim = compute_global_lims(surface_df, bottom_df, param)

    for i, yr in enumerate(panel_order):
        ax = axes[i]
        col = year_color_map.get(yr, "black")

        s = build_one_year_one_depth(surface_df, yr, param)
        b = build_one_year_one_depth(bottom_df, yr, param)

        if not s.empty:
            ax.plot(s["LakeDOY"], s[param], color=col, lw=1.5, ls="-", solid_capstyle="round")
        if not b.empty:
            ax.plot(b["LakeDOY"], b[param], color=col, lw=1.5, ls="--", solid_capstyle="round")

        ax.set_title(yr, fontweight="bold", pad=6, fontsize=BASE_FONT + 1)
        ax.set_xticks(ticks)
        ax.set_xticklabels(labels, rotation=X_TICK_ROT)
        ax.set_xlim(x_min, x_max)

        if ylim is not None:
            ax.set_ylim(ylim)

        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)

        if s.empty and b.empty:
            ax.text(0.5, 0.5, "No data", transform=ax.transAxes, ha="center", va="center",
                    fontsize=BASE_FONT, alpha=0.6)

    # 8th panel: bottom overlay for all years
    ax_overlay = axes[7]
    for yr in year_order:
        col = year_color_map.get(yr, "black")
        b = build_one_year_one_depth(bottom_df, yr, param)
        if b.empty:
            continue
        ax_overlay.plot(b["LakeDOY"], b[param], color=col, lw=1.3, ls="-", solid_capstyle="round")

    ax_overlay.set_title("Bottom overlay (all years)", fontweight="bold", pad=6, fontsize=BASE_FONT + 1)
    ax_overlay.set_xticks(ticks)
    ax_overlay.set_xticklabels(labels, rotation=X_TICK_ROT)
    ax_overlay.set_xlim(x_min, x_max)
    if ylim is not None:
        ax_overlay.set_ylim(ylim)

    ax_overlay.spines["top"].set_visible(False)
    ax_overlay.spines["right"].set_visible(False)

    fig.text(0.03, 0.5, f"{param} ({unit})", va="center", ha="center",
             rotation="vertical", fontweight="bold", fontsize=BASE_FONT + 3)

    fig.text(0.5, 0.02, "Lake-year (Aug → Aug)", ha="center",
             fontweight="bold", fontsize=BASE_FONT + 1)

    legend_handles = [
        Line2D([0], [0], color="black", lw=1.8, ls="-", label="Surface"),
        Line2D([0], [0], color="black", lw=1.8, ls="--", label="Bottom"),
        Line2D([0], [0], color="black", lw=1.8, ls="-", label="Bottom overlay (panel only)"),
    ]
    fig.legend(handles=legend_handles, loc="upper center",
               bbox_to_anchor=(0.5, 0.985), ncol=3, frameon=False, handlelength=2.6)

    fig.tight_layout(rect=[0.06, 0.04, 1, 0.96])

    if DO_SAVE:
        png_out = SAVE_DIR / "supp_fig03_temperature_multiyear_7panels_overlay.png"
        fig.savefig(png_out, dpi=600, bbox_inches="tight")
        print(f"✓ Saved: {png_out.name}")

        for dpi in SAVE_DPIS:
            tiff_out = SAVE_DIR / f"supp_fig03_temperature_multiyear_7panels_overlay_{dpi}dpi.tiff"
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

# ============================================================
# 8) EXECUTION
# ============================================================
if "Temperature" in full_df.columns:
    plot_param_year_panels(surface_df, bottom_df, param="Temperature", unit="°C")

from pathlib import Path
import matplotlib.cm as cm
import matplotlib.colors as mcolors
from matplotlib.lines import Line2D
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy import stats

# ============================================================
# 0) REPOSITORY PATHS & SAVING SETUP
# ============================================================
BASE_DIR = Path(__file__).resolve().parent.parent if Path(__file__).resolve().parent.name == "scripts" else Path(__file__).resolve().parent
SAVE_DIR = BASE_DIR / "figures"
SAVE_DIR.mkdir(parents=True, exist_ok=True)

DO_SAVE = True
SAVE_DPIS = [600, 1200]

# ============================================================
# 1) GLOBAL STYLE
# ============================================================
BASE_FONT = 14
plt.rcParams.update({
    "font.family": "DejaVu Sans",
    "font.size": BASE_FONT,
    "axes.titlesize": BASE_FONT + 2,
    "axes.labelsize": BASE_FONT + 2,
    "xtick.labelsize": BASE_FONT,
    "ytick.labelsize": BASE_FONT,
    "axes.linewidth": 1.8,
    "xtick.major.width": 1.6,
    "ytick.major.width": 1.6,
    "xtick.direction": "out",
    "ytick.direction": "out",
    "figure.dpi": 150,
})

# ============================================================
# 2) LAKE DATA (MAY -> LATE JUL)
# ============================================================
lake_df = pd.DataFrame({
    "Sample": [
        "MAY23_0M", "MAY23_4M", "MAY23_6M", "MAY23_8M",
        "JUN23_0M", "JUN23_4M", "JUN23_6M", "JUN23_8M",
        "EJUL23_0M", "EJUL23_2M", "EJUL23_4M", "EJUL23_6M", "EJUL23_8M",
        "LJUL23_0M", "LJUL23_2M", "LJUL23_4M", "LJUL23_6M", "LJUL23_10M"
    ],
    "δ18O": [
        -19.110203, -19.4599, -19.979126, -20.09047,
        -20.445133, -19.487869, -19.894767, -19.894961,
        -17.970308, -19.52464, -19.62331, -19.780351, -19.79258,
        -19.038715, -17.866765, -18.709399, -18.602712, -18.599129
    ],
    "δ2H": [
        -150.04, -149.97, -153.14, -153.62,
        -157.59, -150.77, -153.82, -154.01,
        -142.33, -152.88, -153.44, -153.36, -153.57,
        -147.41, -144.81, -147.63, -147.67, -147.33
    ]
})

lake_df["Month"] = lake_df["Sample"].str.extract(r"([A-Z]+[0-9]{2})")[0]
lake_df["Depth"] = lake_df["Sample"].str.extract(r"_(\d+)M").astype(int)

month_order = ["MAY23", "JUN23", "EJUL23", "LJUL23"]
month_titles = {
    "MAY23":  "May",
    "JUN23":  "June",
    "EJUL23": "Early July",
    "LJUL23": "Late July",
}

# ============================================================
# 3) SOURCES (END-MEMBERS)
# ============================================================
source_data = pd.DataFrame({
    "Source": ["Lake ice", "Stream water", "New Snow"],
    "δ18O":   [-15.06, -20.34, -22.53],
    "δ2H":    [-131.20, -159.50, -171.53],
    "Marker": ["s", "v", "X"]
})

# ============================================================
# 4) REFERENCE LINES
# ============================================================
x_ref = np.linspace(-30, -10, 200)
gmwl = 8 * x_ref + 10
lmwl = 7.66 * x_ref + 0.83

slope, intercept, *_ = stats.linregress(lake_df["δ18O"], lake_df["δ2H"])
lel = slope * x_ref + intercept

# ============================================================
# 5) DATA PREPARATION (SURFACE VS DEPTH-AVERAGED)
# ============================================================
surface_4 = (
    lake_df.loc[(lake_df["Depth"] == 0) & (lake_df["Month"].isin(month_order))]
    .groupby("Month", as_index=False)
    .agg({"δ18O": "mean", "δ2H": "mean"})
)
surface_4["Month"] = pd.Categorical(surface_4["Month"], categories=month_order, ordered=True)
surface_4 = surface_4.sort_values("Month").reset_index(drop=True)

avg_depths = (
    lake_df.loc[(lake_df["Depth"] != 0) & (lake_df["Month"].isin(month_order))]
    .groupby("Depth", as_index=False)
    .agg({"δ18O": "mean", "δ2H": "mean"})
    .sort_values("Depth")
    .reset_index(drop=True)
)

# Discrete depth color scheme
INCLUDE_SURFACE_IN_CBAR = True
cbar_depths = [0] + avg_depths["Depth"].tolist() if INCLUDE_SURFACE_IN_CBAR else avg_depths["Depth"].tolist()
cbar_depths = sorted(list(dict.fromkeys(cbar_depths)))

depth_to_code = {d: i for i, d in enumerate(cbar_depths)}
avg_depths["_code"] = avg_depths["Depth"].map(depth_to_code).astype(int)

depth_colors = cm.viridis_r(np.linspace(0.0, 1.0, len(cbar_depths)))
depth_cmap = mcolors.ListedColormap(depth_colors)
depth_norm = mcolors.BoundaryNorm(np.arange(-0.5, len(cbar_depths) + 0.5, 1), depth_cmap.N)

# ============================================================
# 6) PLOT & EXPORT
# ============================================================
def plot_fused(surface_4, avg_depths, source_data,
               xlim=(-24.5, -12), ylim=(-190, -110),
               figsize=(7.5, 6.5)):

    fig, ax = plt.subplots(figsize=figsize)
    fig.subplots_adjust(left=0.12, right=0.82, top=0.78, bottom=0.12)

    # Reference lines
    ax.plot(x_ref, gmwl, color="gray",  lw=2, alpha=0.6)
    ax.plot(x_ref, lmwl, color="gray",  lw=2, ls="--", alpha=0.6)
    ax.plot(x_ref, lel,  color="black", lw=2.5, ls=":", alpha=0.9)

    # Source end-members
    for _, s in source_data.iterrows():
        ax.scatter(s["δ18O"], s["δ2H"], marker=s["Marker"], s=220,
                   facecolor="lightgray", edgecolor="black", zorder=6)
        ax.text(s["δ18O"], s["δ2H"] - 3, s["Source"],
                ha="center", va="top", fontsize=10, fontweight="bold")

    # Depth-averaged points (2–10 m)
    sc = ax.scatter(
        avg_depths["δ18O"], avg_depths["δ2H"],
        c=avg_depths["_code"],
        cmap=depth_cmap, norm=depth_norm,
        s=280, edgecolor="black", zorder=10
    )

    # Surface points by month
    label_style = dict(fontsize=10, fontweight="bold", color="black", zorder=21)
    label_pos = {
        "EJUL23": dict(dx=+0.40, dy=+0.12, ha="left",   va="center"),
        "LJUL23": dict(dx=-0.25, dy=+0.10, ha="right",  va="center"),
        "MAY23":  dict(dx= 0.45, dy=-1.20, ha="center", va="top"),
        "JUN23":  dict(dx=-0.40, dy=+0.95, ha="center", va="bottom"),
    }

    for _, r in surface_4.iterrows():
        m = str(r["Month"])
        x, y = float(r["δ18O"]), float(r["δ2H"])

        ax.scatter(
            x, y, s=360, marker="o",
            facecolor="#FFD400", edgecolor="black", linewidth=1.2, zorder=20
        )
        p = label_pos.get(m, dict(dx=+0.20, dy=+0.20, ha="left", va="bottom"))
        ax.text(x + p["dx"], y + p["dy"], month_titles[m], ha=p["ha"], va=p["va"], **label_style)

    ax.set_xlabel(r"$\delta^{18}\mathrm{O}$ (‰)")
    ax.set_ylabel(r"$\delta^2\mathrm{H}$ (‰)")
    ax.set_xlim(*xlim)
    ax.set_ylim(*ylim)
    ax.grid(True, linestyle=":", alpha=0.22)
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)

    # Reference Line Legend
    ref_handles = [
        Line2D([0], [0], color="gray",  lw=2,   ls="-",  label=r"GMWL: $\delta^2\mathrm{H} = 8\delta^{18}\mathrm{O} + 10$"),
        Line2D([0], [0], color="gray",  lw=2,   ls="--", label=r"LMWL: $\delta^2\mathrm{H} = 7.66\delta^{18}\mathrm{O} + 0.83$"),
        Line2D([0], [0], color="black", lw=2.5, ls=":",  label=rf"LEL: $\delta^2\mathrm{{H}} = {slope:.2f}\delta^{{18}}\mathrm{{O}} {intercept:+.2f}$"),
    ]
    leg1 = ax.legend(
        handles=ref_handles,
        title="Reference Lines",
        loc="lower left",
        bbox_to_anchor=(0.00, 1.12),
        frameon=False,
        handlelength=2.8,
        labelspacing=0.6,
        borderaxespad=0.0
    )
    leg1.get_title().set_fontweight("bold")
    ax.add_artist(leg1)

    # Water Sources Legend
    water_handles = [
        Line2D([0], [0], marker=row["Marker"], linestyle="None", color="black",
               markerfacecolor="lightgray", markeredgecolor="black",
               markersize=10, label=row["Source"])
        for _, row in source_data.iterrows()
    ]
    leg2 = ax.legend(
        handles=water_handles,
        title="Water Sources",
        loc="lower left",
        bbox_to_anchor=(0.75, 1.12),
        frameon=False,
        labelspacing=0.6,
        borderaxespad=0.0
    )
    leg2.get_title().set_fontweight("bold")

    # Discrete Colorbar
    cax = fig.add_axes([0.86, 0.18, 0.04, 0.60])
    cb = fig.colorbar(sc, cax=cax, orientation="vertical")
    cb.set_label("Depth (m)", fontsize=BASE_FONT + 1, fontweight="bold")
    cb.ax.tick_params(labelsize=BASE_FONT)
    cb.set_ticks(list(depth_to_code.values()))
    cb.set_ticklabels([str(d) for d in cbar_depths])
    cb.ax.invert_yaxis()

    if DO_SAVE:
        png_out = SAVE_DIR / "stable_isotopes_water_sources_lel.png"
        fig.savefig(png_out, dpi=600, bbox_inches="tight")
        print(f"✓ Saved: {png_out.name}")

        for dpi in SAVE_DPIS:
            tiff_out = SAVE_DIR / f"stable_isotopes_water_sources_lel_{dpi}dpi.tiff"
            fig.savefig(tiff_out, dpi=dpi, bbox_inches="tight", format="tiff")
            print(f"✓ Saved: {tiff_out.name}")

    plt.show()
    plt.close(fig)

plot_fused(surface_4, avg_depths, source_data)

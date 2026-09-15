from pathlib import Path
import warnings
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec

# 1. Suppress warnings
warnings.filterwarnings('ignore', category=UserWarning, module='openpyxl')

# =============================================================================
# REPOSITORY PATHS & SAVING SETUP
# =============================================================================
BASE_DIR = Path(__file__).resolve().parent.parent if Path(__file__).resolve().parent.name == "scripts" else Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
SAVE_DIR = BASE_DIR / "figures"
SAVE_DIR.mkdir(parents=True, exist_ok=True)

# 2. Path to your file in data/
file_path = DATA_DIR / "GRL deep and shallow DO profiles in winter.xlsx"
if not file_path.exists():
    raise FileNotFoundError(f"Missing file: {file_path.name}. Make sure it is placed in the data/ folder.")

df = pd.read_excel(file_path, skiprows=4)

# --- MASTER STYLE CONTROL ---
BASE_FONT = 14
plt.rcParams.update({
    "font.family": "DejaVu Sans",
    "font.size": BASE_FONT,
    "axes.titlesize": BASE_FONT + 2,
    "axes.labelsize": BASE_FONT + 1,
    "xtick.labelsize": BASE_FONT - 1,
    "ytick.labelsize": BASE_FONT - 1,
    "axes.linewidth": 1.2,
})

# 3. Setup Figure - 12x8
fig = plt.figure(figsize=(12, 8))

# Master grid: wspace=0.15 for spacing between sections
master_gs = gridspec.GridSpec(1, 2, width_ratios=[1, 2.5], wspace=0.15)

# =============================================================================
# LEFT SECTION: FIGURE A (PELAGIC)
# =============================================================================
ax_a = fig.add_subplot(master_gs[0])

pelagic_configs = [
    ('Nov', 2, 4, 'blue', 2.5, (100, 120)),
    ('Jan', 26, 28, 'salmon', 3.0, (80, 100)),
    ('Apr', 14, 16, 'gold', 3.5, (0, 60))
]

for month, d_idx, do_idx, color, y_label_pos, (ice_xmin, ice_xmax) in pelagic_configs:
    depth_m = pd.to_numeric(df.iloc[:, d_idx], errors='coerce')
    do_vals = pd.to_numeric(df.iloc[:, do_idx], errors='coerce')
    mask = depth_m.notna() & do_vals.notna()
    d_clean, do_clean = depth_m[mask], do_vals[mask]
    
    if not d_clean.empty:
        ax_a.plot(do_clean, d_clean, color=color, linewidth=2.5)
        # Ice Line
        first_depth = d_clean.iloc[0]
        ax_a.hlines(y=first_depth, xmin=ice_xmin, xmax=ice_xmax, color='black', linestyle='--', linewidth=1.5)
        ax_a.text((ice_xmin + ice_xmax)/2, first_depth - 0.05, 'Ice', color='black', 
                  ha='center', va='bottom', fontweight='bold', fontsize=BASE_FONT - 2)
        
        # Color-matched Month Labels
        idx = (d_clean - y_label_pos).abs().idxmin()
        lx, ly = do_clean.iloc[idx], d_clean.iloc[idx]
        ha_val = 'right' if month == 'Jan' else 'left'
        offset = -3 if month == 'Jan' else 3
        ax_a.text(lx + offset, ly, month, color=color, fontweight='bold', va='center', ha=ha_val)

ax_a.set_ylim(10, 0)
ax_a.set_xlim(0, 120)
ax_a.xaxis.set_label_position('top')
ax_a.xaxis.tick_top()
ax_a.set_xlabel('DO (%)', fontweight='bold', labelpad=25)
ax_a.set_ylabel('Depth (m)', fontweight='bold')
ax_a.text(0.0, 1.22, 'a) Pelagic', transform=ax_a.transAxes, fontweight='bold', fontsize=BASE_FONT + 6)
ax_a.grid(True, linestyle=':', alpha=0.5)

# =============================================================================
# RIGHT SECTION: FIGURE B (LITTORAL)
# =============================================================================
gs_b = gridspec.GridSpecFromSubplotSpec(10, 3, subplot_spec=master_gs[1], wspace=0.29)

ax_nov = fig.add_subplot(gs_b[0:2, 0]) 
ax_jan = fig.add_subplot(gs_b[0:4, 1])
ax_apr = fig.add_subplot(gs_b[0:4, 2])
litt_axes = [ax_nov, ax_jan, ax_apr]

litt_configs = [
    {'name': 'Nov', 'd_idx': 8, 'do_idx': 10, 'color': 'blue', 'xlim': (105, 111), 'xticks': [106, 108, 110], 'ice': 0.55, 'ylim': (2.2, 0)},
    {'name': 'Jan', 'd_idx': 32, 'do_idx': 34, 'color': 'salmon', 'xlim': (80, 105), 'xticks': [85, 90, 95, 100, 105], 'ice': 1.27, 'ylim': (4.2, 0)},
    {'name': 'Apr', 'd_idx': 20, 'do_idx': 22, 'color': 'gold', 'xlim': (60, 80), 'xticks': [65, 70, 75, 80], 'ice': 1.80, 'ylim': (4.2, 0)}
]

for i, cfg in enumerate(litt_configs):
    ax = litt_axes[i]
    depth_m = pd.to_numeric(df.iloc[:, cfg['d_idx']], errors='coerce')
    do_vals = pd.to_numeric(df.iloc[:, cfg['do_idx']], errors='coerce')
    mask = depth_m.notna() & do_vals.notna()
    ax.plot(do_vals[mask], depth_m[mask], color=cfg['color'], linewidth=2.5)
    ax.axhline(y=cfg['ice'], color='black', linestyle='--', linewidth=1.5)
    
    # Centered Ice Label
    xc, yc = (cfg['xlim'][0] + cfg['xlim'][1]) / 2, cfg['ice'] / 2
    ax.text(xc, yc, 'Ice', color='black', ha='center', va='center', fontweight='bold', fontsize=BASE_FONT-2)
    
    # Color-matched Annotations
    if cfg['name'] == 'Nov':
        ax.text(110.5, 1.0, 'Nov', color=cfg['color'], ha='right', fontweight='bold')
    elif cfg['name'] == 'Jan':
        ax.text(86, 1.8, 'Jan', color=cfg['color'], ha='left', fontweight='bold')
    elif cfg['name'] == 'Apr':
        ax.text(79, 2.5, 'Apr', color=cfg['color'], ha='right', fontweight='bold')

    ax.set_ylim(cfg['ylim'])
    ax.set_xlim(cfg['xlim'])
    ax.set_xticks(cfg['xticks'])
    ax.set_yticks([0, 1, 2, 3, 4] if cfg['ylim'][0] > 3 else [0, 1, 2])
    
    ax.xaxis.set_label_position('top')
    ax.xaxis.tick_top()
    ax.set_xlabel('DO (%)', fontweight='bold', labelpad=25)
    ax.grid(True, linestyle=':', alpha=0.5)

for ax in litt_axes: 
    ax.tick_params(labelleft=True)

# Subplot ID B
ax_nov.text(0.0, 2.14, 'b) Littoral', transform=ax_nov.transAxes, fontweight='bold', fontsize=BASE_FONT + 6)

plt.subplots_adjust(top=0.78, bottom=0.1, left=0.08, right=0.97)

# =============================================================================
# EXPORT FIGURES
# =============================================================================
png_out = SAVE_DIR / 'GRL_DO_profiles_pelagic_littoral_winter.png'
plt.savefig(png_out, dpi=900)
print(f"✓ Saved: {png_out.name}")

for dpi in [600, 1200]:
    tiff_out = SAVE_DIR / f'GRL_DO_profiles_pelagic_littoral_winter_{dpi}dpi.tiff'
    plt.savefig(tiff_out, dpi=dpi)
    print(f"✓ Saved: {tiff_out.name}")

plt.show()

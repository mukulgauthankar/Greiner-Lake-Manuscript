# Data and Code: Under-Ice Regimes and Oxygen Dynamics in Greiner Lake

This repository provides the processed datasets and Python workflows to reproduce the figures and analyses presented in the manuscript on Greiner Lake (Cambridge Bay, Nunavut).

---

## Directory Overview

- `data/`: Processed limnological, mooring, CTD profile, and meteorological datasets.
- `scripts/`: Standalone Python scripts for analytical processing and figure generation.
- `figures/`: Target directory where generated publication-ready figures (PNG and 600/1200 DPI TIFF) are exported.
- `requirements.txt`: Python package dependencies required to reproduce the environment.
- `CITATION.cff`: Machine-readable metadata for citing this repository and dataset.
- `LICENSE.md`: Dual licensing terms (MIT License for code; CC-BY 4.0 for data).

---

## Computational Environment Setup

Clone this repository, install dependencies, and reproduce all figures sequentially:

```bash
git clone https://github.com/mukulgauthankar/Greiner-Lake-Manuscript.git
cd Greiner-Lake-Manuscript
pip install -r requirements.txt

# Reproduce Main Figures
python scripts/fig02_plot_temperature_surface_bottom_2022_2023.py
python scripts/fig03_plot_do_saturation_multiyear.py
python scripts/fig04_plot_do_profiles_pelagic_littoral_winter.py
python scripts/fig05_plot_wind_roses_thin_ice_window.py
python scripts/fig06_plot_water_level_cycles_multiyear.py
python scripts/fig07_plot_stable_isotopes_water_sources.py
python scripts/fig08_plot_nutrient_profiles_master_panel.py

# Reproduce Supplementary Figures
python scripts/supp_fig01_plot_precipitation_heatmap_cambridge_bay.py
python scripts/supp_fig03_plot_temperature_multiyear_panels.py
python scripts/supp_fig05_plot_chla_profiles_snow_ice.py
python scripts/supp_fig06_plot_ghg_vertical_profiles_2023.py

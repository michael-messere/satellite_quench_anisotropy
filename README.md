# Satellite Quenching Anisotropy: TNG100 vs SAGA / ELVES

Code and data for *The Anisotropic Quenching of Satellites in Milky Way-mass Halos*
(Garcia, Messere, Putman & Zhu). We measure the anisotropic satellite-galaxy quenching (ASGQ)
signal — the dependence of satellite quenching and number count on azimuthal angle relative to
the host's projected major axis — in Milky Way-mass halos, comparing the IllustrisTNG (TNG100-1)
simulation to the SAGA and ELVES surveys.

Related work reproduced / compared against:
[Karp+ 2023](https://iopscience.iop.org/article/10.3847/2041-8213/acd3e9),
[Martín-Navarro+ 2021](https://www.nature.com/articles/s41586-021-03545-9),
[Zakharova+ 2025](https://www.aanda.org/articles/aa/full_html/2025/01/aa52296-24/aa52296-24.html).

## Layout

```
satellite_quench_anisotropy/
├── requirements.txt
├── docs/conventions.md          # little-h, angle convention, quench definition — READ THIS
├── data/
│   ├── saga/                     # SAGA DR3 host (C1) + satellite (C3) tables, host compre csv
│   ├── elves/                    # Carlsten+ 2022 ELVES host + confirmed-satellite tables
│   ├── tng100/{z0,z0p05}/        # per-satellite catalogs written by notebook 01 (regenerate!)
│   └── tng50/{z0,z0p05}/         # same, for TNG50-1 (SIM = 'TNG50')
└── notebooks/
    ├── tng_utils.py                     # shared TNG loading / host-selection / angle / quench logic
    ├── 01_tng_generate_catalogs.ipynb   # TNG100 → per-satellite CSVs (run on Binder)
    ├── 02_tng_reproduce_karp.ipynb      # sanity check: reproduce Karp+ 2023 in h^-1 units
    ├── 03_analysis.ipynb                # main analysis: SAGA + ELVES + TNG → paper Figure 1
    ├── 04_quench_fraction_vs_angle.ipynb     # f_q vs angle (0-90 & 0-180), MW-mass hosts, 7 sat cuts
    └── 05_quench_fraction_vs_halomass.ipynb  # f_q vs angle while growing the host mass range 12→14
```

`notebooks/tng_utils.py` is the single source of truth for the little-h convention, host
selection, both azimuthal-angle foldings ([0,90] and [0,180]) and the quench definition; notebooks
01/04/05 use it so the analysis cannot silently diverge.

## Choosing the simulation and redshift

Every TNG notebook has two one-line switches near the top:

* **`SIM = 'TNG100'`** or `'TNG50'` — the two boxes differ only in the directory name
  (`L75n1820TNG` vs `L35n2160TNG`) and box size (75 vs 35 Mpc/h).
* **`REDSHIFT = 'z0'`** or `'z0p05'` — z=0 (snapshot 99) or z=0.05 (snapshot 98). The SDSS-SKIRT
  mocks (needed for the host major-axis orientation) exist at both redshifts for TNG50-1/TNG100-1.

little-h and the catalog/morphology layout are identical across all of these, so flipping a switch
and re-running reproduces the whole analysis for that (sim, redshift). The registries live in
`notebooks/tng_utils.py` (`SIMS`, `REDSHIFTS`) — edit `sim_dir` there if your Binder mounts the data
under a different name. Notebook 01 writes to `data/<sim>/<redshift>/` (e.g. `data/tng100/z0/`) and
notebook 03 reads from the matching folder. To redo everything in, say, TNG50 at z=0.05: set
`SIM='TNG50'`, `REDSHIFT='z0p05'` in 01 and run it, then the same in 03/04/05 (and 02 for the Karp
check).

## Run order

1. **`01_tng_generate_catalogs.ipynb`** *(Binder only)* — reads the raw TNG100-1 group/subhalo
   catalogs, SKIRT SDSS morphologies and StarFormationRates HDF5 files, and writes
   `data/tng100/tng100_satellites_{1e6,1e7,1e8}.csv`. Requires `illustris_python` + `h5py`.
   **Set `TNG_ROOT` in the config cell to the absolute path of your `L75n1820TNG` directory**
   (default `~/SimulationData/L75n1820TNG`, i.e. `/home/jovyan/SimulationData/L75n1820TNG` on
   Binder — use an absolute path so it doesn't get mis-joined onto the home dir). The self-check
   cells print host/satellite counts and the overall quenched fraction (Karp's ref f_q ≈ 0.615).

2. **`02_tng_reproduce_karp.ipynb`** *(Binder only, optional)* — reproduces Karp+ 2023 Figure 1
   (quenched fraction vs host halo mass, and satellite count vs azimuthal angle) using **h^-1
   masses** so the cuts match Karp exactly. Overplots Karp's digitized points; this is the direct
   "do my masses match Karp" test.

3. **`03_analysis.ipynb`** *(laptop or Binder)* — loads the SAGA and ELVES catalogs plus the TNG
   CSVs from step 1, computes azimuthal angles, runs the one- and two-sample KS tests, fits the
   quench fraction vs angle with a sinusoid via MCMC, compares sinusoid vs constant with BIC/AIC,
   and produces the paper's Figure 1. Needs internet (SIMBAD lookup of ELVES host PAs).

4. **`04_quench_fraction_vs_angle.ipynb`** *(Binder only)* — quenched fraction vs azimuthal angle
   ([0,90]) for MW-mass hosts (12.0–12.5) and the seven half-dex satellite cuts. Reads raw TNG via
   `tng_utils`.

5. **`05_quench_fraction_vs_halomass.ipynb`** *(Binder only)* — host halo-mass dependence two ways:
   a **cumulative sweep** (12–12.25, … 12–14.0) and **disjoint bins** (default 12–13, 13–14, 14+,
   set by `HOST_LOGM_BIN_EDGES`). Plots f_q vs angle with the fitted sinusoid + uncertainty band
   overlaid, and summarizes the amplitude `b` (with errors, significance-flagged) vs halo mass.
   `FIT_METHOD = 'lsq'` or `'mcmc'`.

## Data provenance

| File | Source |
|------|--------|
| `data/saga/saga-dr3-tableC1.txt` | SAGA DR3 (Mao+ 2024) machine-readable Table C1 — hosts |
| `data/saga/saga-dr3-tableC3.txt` | SAGA DR3 Table C3 — confirmed satellites |
| `data/saga/saga_host_compre.csv` | compiled SAGA host properties |
| `data/elves/Carlsten22_ELVES_host.csv` | ELVES hosts (Carlsten+ 2022) |
| `data/elves/Carlsten22_ELVES_confirmed_sats.csv` | ELVES confirmed satellites (Carlsten+ 2022) |
| `data/tng100/tng100_satellites_*.csv` | generated by `01_tng_generate_catalogs.ipynb` |

## The little-h gotcha (why earlier TNG masses didn't match Karp+)

Karp+ select halos/satellites in **h^-1 M_sun**; TNG mass fields are already in `10^10 h^-1 M_sun`,
so matching them means multiplying by `1e10` and **not** dividing by `h`. Dividing by `h` lowers
log-mass by 0.17 dex and breaks the reproduction. Notebook 02 stays in h^-1; notebook 01 stores
both conventions and uses physical M_sun for the fiducial SAGA/ELVES comparison. Full details in
[`docs/conventions.md`](docs/conventions.md).

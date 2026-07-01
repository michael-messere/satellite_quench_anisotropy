# notebooks2 — clean-start anisotropy pipeline

1. **`01_generate_catalogs.ipynb`** (Binder only): for TNG100 & TNG50 at z=0 and z=0.05, computes
   each satellite's azimuthal angle and 3D distance from its central, for **MW-mass hosts**
   (`12.0 < log10 M200c < 12.5`) and satellites `M* > 1e7`, **no radius cut**. Writes to
   `../data2/<sim>/<z>/tng_satellites_hostlogM12.0-12.5_logM7.00.csv`.

2. **`02_anisotropy_fits_tng100_tng50.ipynb`**: fits `p(theta) ~ 1 + A cos 2theta` and plots
   TNG100 (`M* > 1e8`) and TNG50 (`M* > 1e7`), each at z=0 and z=0.05. `RADIUS_CUT` toggles a
   `d_r200_3d < R200C_FACTOR` cut (default off = all radii).

Note: "z = 0.5" is interpreted as z = 0.05 (snap 98, the redshift with SDSS-SKIRT mocks).

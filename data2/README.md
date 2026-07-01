# data2 — all-central satellite catalogs (clean start)

Per-satellite catalogs produced by `../notebooks2/01_generate_allcentral_catalogs.ipynb`
(run on Binder, where the raw TNG data is mounted). **Not committed** — regenerate as needed.

Layout (one file per simulation and redshift):

```
tng100/z0/tng_satellites_allcentrals_logM7.00.csv
tng100/z0p05/tng_satellites_allcentrals_logM7.00.csv
tng50/z0/tng_satellites_allcentrals_logM7.00.csv
tng50/z0p05/tng_satellites_allcentrals_logM7.00.csv
```

Selection: **all centrals** (no halo-mass window) with reliable g+i SDSS-Sersic morphology and
central `M* > 1e7`; satellites with `M*_sat > 1e7`; **no radius cut** (all radii kept, with
`d_3d_kpc` and `d_r200_3d` stored so a radius cut can be applied downstream).

`notebooks2/02_anisotropy_fits_tng100_tng50.ipynb` reads these, sub-selects `M* > 1e8` for TNG100
and `M* > 1e7` for TNG50, and fits `p(theta) ~ 1 + A cos 2theta`, with a `RADIUS_CUT` toggle.

Columns: `host_id, mstar_phys, mstar_hinv, host_mstar_phys, host_m200_phys, host_m200_hinv, sfr,
alpha, d_3d_kpc, d_proj_kpc, d_r200_3d, d_r200_proj, quenched`. Masses are log10 physical M_sun.

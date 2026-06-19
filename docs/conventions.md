# Conventions

This file documents the three conventions that matter for reproducing the analysis and for
comparing TNG100 to the SAGA/ELVES surveys. **Read this before changing any mass cut.**

---

## 0. Simulation and redshift (TNG100 / TNG50; z=0 / z=0.05)

The notebooks run on either **TNG100-1** (`L75n1820TNG`, 75 Mpc/h) or **TNG50-1**
(`L35n2160TNG`, 35 Mpc/h) via the `SIM` switch, and at either **z=0** (snapshot 99) or
**z=0.05** (snapshot 98, z=0.0485) via the `REDSHIFT` switch (`'z0'` / `'z0p05'`), at the top of
each TNG notebook. Registries: `SIMS` and `REDSHIFTS` in `notebooks/tng_utils.py`. All combinations
share `h = 0.6774` and the same group-catalog + SDSS-SKIRT morphology layout — only the directory
name, the box size (periodic-wrap), and the snapshot number differ. The SDSS-SKIRT mocks (host
major-axis orientation) are available at both redshifts for TNG50-1 and TNG100-1 (TNG data spec,
sec 5k). Everything below applies identically to all combinations.

## 1. Little-h and mass units (this is what made the masses not match Karp+)

IllustrisTNG uses `h = 0.6774` (Planck 2015). The raw group-catalog mass fields are stored in
**code units of `10^10 h^-1 M_sun`**:

| Field | Raw units | Physical mass (M_sun) | h^-1 mass (h^-1 M_sun) |
|-------|-----------|------------------------|-------------------------|
| `Group_M_Crit200`   | `10^10 h^-1 M_sun` | `* 1e10 / h` | `* 1e10` |
| `SubhaloMassType[:,4]` (stars) | `10^10 h^-1 M_sun` | `* 1e10 / h` | `* 1e10` |

Converting between the two shifts log-mass by a constant:

```
log10(M_phys) - log10(M_hinv) = log10(1/h) = log10(1/0.6774) = -0.1694 dex
```

So a "physical" mass is **0.17 dex lower** than the same object's "h^-1" mass.

### Which convention each notebook uses, and why

- **`02_tng_reproduce_karp.ipynb` → h^-1 M_sun (multiply by 1e10, do NOT divide by h).**
  Karp, Lange & Wechsler (2023, ApJL 949, L13) select
  `M_200c > 10^12 h^-1 M_sun` and `M*,sat >= 10^8 h^-1 M_sun`.
  To land on their selection you must stay in h^-1 units. Dividing by h here is exactly the
  bug that offset the masses by +0.17 dex and made the reproduction disagree.

- **`01_tng_generate_catalogs.ipynb` → stores BOTH, fiducial science uses physical M_sun.**
  Our science question (MW-mass hosts vs SAGA/ELVES) compares against survey masses that are
  in physical M_sun (Behroozi SMHM for the hosts, observed M* for the satellites). So the
  fiducial host selection is `12.0 < log10(M_200c_phys) < 12.5` and the satellite cuts are
  `M*,sat_phys > 10^{6,7,8} M_sun`. Each output row also carries the h^-1 columns so you can
  switch conventions without re-running.

### Output CSV columns (`data/tng100/tng100_satellites_<cut>.csv`)

One row per selected satellite:

| column | meaning |
|--------|---------|
| `host_id`          | index of the host halo (group), for jackknife-by-host |
| `mstar_phys`       | log10 satellite stellar mass, physical M_sun (`*1e10/h`) |
| `mstar_hinv`       | log10 satellite stellar mass, h^-1 M_sun (`*1e10`) |
| `host_m200_phys`   | log10 host M_200c, physical M_sun |
| `host_m200_hinv`   | log10 host M_200c, h^-1 M_sun |
| `sfr`              | instantaneous `SubhaloSFR` [M_sun/yr] |
| `alpha`            | projected angle from host major axis, degrees in [0, 90] |
| `quenched`         | 1 = quenched, 0 = star-forming (see §3) |

> **Important:** the older `satellite_1e6/1e7/1e8/*.csv` files in the original `satellite_quench`
> repo were written with an *inconsistent* mix of `/h` and no-`/h` (the two SFMS notebooks
> disagreed). Do not reuse them — regenerate with `01_tng_generate_catalogs.ipynb`.

---

## 2. Azimuthal angle (theta / alpha)

Orientation convention (matches the draft and Martín-Navarro et al. 2021):

- **0° = host projected MAJOR axis**, **90° = host projected MINOR axis.**
- All angles are folded into `[0, 90]` via the four-fold symmetry of an ellipse
  (`map_to_0_90`), since the major axis points in two directions and the disk is symmetric.

Per dataset:

- **SAGA:** host position angle `PA` from the SAGA DR3 host table; satellite position angle
  from `SkyCoord.position_angle`; folded to [0,90].
- **ELVES:** host PA from SIMBAD (`galdim_angle`); satellites likewise. (The local
  `Carlsten22_ELVES_host.csv` also has a `Position_angle` column as a fallback.)
- **TNG:** host major-axis angle = mean of the SDSS g- and i-band 2D Sérsic `sersic_theta`
  (Rodriguez-Gomez et al. 2019 SKIRT images); satellite azimuth = `arctan2(dy, dx)` of the
  projected (x,y) separation with periodic boundary wrapping; `angle_diff` → [0,90].

---

## 3. Quenched definition (TNG)

Following Martín-Navarro et al. (2021), a satellite is **quenched** if its instantaneous SFR
sits at least 1 dex below the SDSS star-forming main sequence (SFMS) fit:

```
log10(SFR_MS)        = 0.75 * log10(M*/M_sun) - 7.5      # SFMS
quenched  if  SFR  <  SFR_MS / 10                         # 1 dex below
```

`SFR` is `SubhaloSFR` (sum of per-cell SFR in the subhalo). The SFMS fit uses the **physical**
stellar mass. (SAGA and ELVES use their own observational quench definitions — Hα + NUV sSFR
for SAGA; early-type morphology for ELVES — taken directly from the published catalogs.)

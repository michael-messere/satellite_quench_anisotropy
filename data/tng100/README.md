# TNG100 catalogs

Generated per-satellite catalogs (not committed), organized by redshift:

```
z0/     tng100_satellites_logM6.00.csv ... logM9.00.csv   # z = 0   (snapshot 99)
z0p05/  tng100_satellites_logM6.00.csv ... logM9.00.csv   # z = 0.05 (snapshot 98)
```

Produce them by running [`../../notebooks/01_tng_generate_catalogs.ipynb`](../../notebooks/01_tng_generate_catalogs.ipynb)
with `SIM = 'TNG100'` and the chosen `REDSHIFT` on the Binder instance where the TNG100-1 data is
mounted. `03_analysis.ipynb` reads them from the matching `SIM`/`REDSHIFT` subdirectory. See
[`../../docs/conventions.md`](../../docs/conventions.md) for column definitions and the little-h
convention.

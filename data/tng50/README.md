# TNG50 catalogs

Same as `../tng100/` but for TNG50-1 (`L35n2160TNG`, 35 Mpc/h box). Generated, not committed,
organized by redshift:

```
z0/     tng100_satellites_logM6.00.csv ... logM9.00.csv   # z = 0    (snapshot 99)
z0p05/  tng100_satellites_logM6.00.csv ... logM9.00.csv   # z = 0.05 (snapshot 98)
```

(The file *names* keep the `tng100_satellites_` prefix from the generator; the TNG50 vs TNG100 and
z0 vs z0.05 distinctions are the **directory** path — `data/<sim>/<redshift>/`.)

Produce them by running [`../../notebooks/01_tng_generate_catalogs.ipynb`](../../notebooks/01_tng_generate_catalogs.ipynb)
with `SIM = 'TNG50'` and the chosen `REDSHIFT` on Binder, then run `03_analysis.ipynb` with the
matching `SIM`/`REDSHIFT`.

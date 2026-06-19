"""Shared TNG100-1 helpers for the satellite-quenching-anisotropy notebooks.

Single source of truth for the things that must be identical across notebooks so the analysis
cannot silently diverge (this kind of drift is exactly what caused the earlier mass mismatch):

* the little-h convention (TNG masses are 10^10 h^-1 M_sun; physical = *1e10/h, h^-1 = *1e10),
* Milky-Way-mass host selection on physical M_200c,
* the projected azimuthal angle in BOTH foldings: alpha90 in [0, 90] and alpha180 in [0, 180),
* the quenched definition (1 dex below the Martin-Navarro+ 2021 SFMS).

Heavy imports (`illustris_python`, `h5py`) are deferred into `compute_satellite_catalog` so this
module can be imported — and its pure helpers unit-tested — on a machine without the TNG data.

See ../docs/conventions.md for the full description.
"""
import os
import numpy as np
import pandas as pd

H = 0.6774                 # IllustrisTNG little-h (Planck 2015), same for TNG50/100/300

# Per-simulation settings. `sim_dir` is the simulation's output directory name; `lbox_mpc_h`
# is the box side in Mpc/h (used for the periodic minimum-image wrap). Same SDSS-SKIRT
# morphology + group-catalog layout for all boxes; only the directory name and box size differ.
SIMS = {
    'TNG100': dict(sim_dir='L75n1820TNG', lbox_mpc_h=75.0),
    'TNG50':  dict(sim_dir='L35n2160TNG', lbox_mpc_h=35.0),
    'TNG300': dict(sim_dir='L205n2500TNG', lbox_mpc_h=205.0),
}

# SDSS-SKIRT mocks are available at z=0 and z=0.05 (TNG data spec, sec 5k) for TNG50-1, TNG100-1,
# Illustris-1. In TNG the z=0.05 mocks live at snapshot 98 (z=0.0485); z=0 is snapshot 99.
REDSHIFTS = {
    'z0':    dict(snap=99, z=0.0),
    'z0p05': dict(snap=98, z=0.0485),
}


def snap_for(redshift):
    """Snapshot number for a redshift tag ('z0' -> 99, 'z0p05' -> 98)."""
    return REDSHIFTS[redshift]['snap']


def sim_root(sim, parent='~/SimulationData'):
    """Default absolute path to a simulation's directory, e.g. ~/SimulationData/L35n2160TNG."""
    return os.path.expanduser(os.path.join(parent, SIMS[sim]['sim_dir']))


def lbox_kpc(sim):
    """Box side in physical kpc for the periodic wrap."""
    return SIMS[sim]['lbox_mpc_h'] * 1000.0 / H


def tng_paths(tng_root, snap=99):
    """Absolute paths to the catalogs/post-processing under a TNG100-1 root directory."""
    sp = f'snapnum_{snap:03d}'
    return dict(
        basePath=os.path.join(tng_root, 'output'),
        morph_g=os.path.join(tng_root, f'postprocessing/skirt_images/sdss/{sp}/morphs_g.hdf5'),
        morph_i=os.path.join(tng_root, f'postprocessing/skirt_images/sdss/{sp}/morphs_i.hdf5'),
        subfind_ids=os.path.join(tng_root, f'postprocessing/skirt_images/sdss/{sp}/subfind_ids.txt'),
    )


# --------------------------------------------------------------------------- pure helpers


def quenched_flag(logmstar_phys, sfr):
    """1 if a satellite sits >= 1 dex below the SFMS, else 0.

    SFMS (Martin-Navarro+ 2021): log10(SFR_MS) = 0.75*log10(M*/Msun) - 7.5, using the PHYSICAL
    stellar mass; quenched if SFR < SFR_MS / 10.
    """
    sfr_ms = 10.0 ** (0.75 * np.asarray(logmstar_phys) - 7.5)
    return (np.asarray(sfr) < sfr_ms / 10.0).astype(int)


def fold_angles(phi_deg, pa_host_deg):
    """Project the satellite azimuth onto the host major axis.

    Returns (alpha90, alpha180):
      * alpha180 in [0, 180): angle from the major-axis LINE (PA is degenerate mod 180);
        0 (and ->180) = major axis, 90 = minor axis.
      * alpha90 in [0, 90]: alpha180 folded by the additional mirror symmetry,
        i.e. the angular distance to the nearest major-axis direction.
    """
    alpha180 = np.mod(np.asarray(phi_deg) - np.asarray(pa_host_deg), 180.0)
    alpha90 = np.minimum(alpha180, 180.0 - alpha180)
    return alpha90, alpha180


def fq_vs_angle(angle, quenched, nbins, amax):
    """Quenched fraction per angle bin with binomial errors.

    Parameters
    ----------
    angle : array      satellite angles (deg), in [0, amax]
    quenched : array   1 = quenched, 0 = star-forming
    nbins : int        number of equal-width bins over [0, amax]
    amax : float       upper edge (90 or 180)

    Returns
    -------
    centers, fq, err, counts  (fq is NaN in empty bins)
    """
    angle = np.asarray(angle)
    quenched = np.asarray(quenched, dtype=float)
    edges = np.linspace(0, amax, nbins + 1)
    centers = 0.5 * (edges[:-1] + edges[1:])
    fq = np.full(nbins, np.nan)
    err = np.full(nbins, np.nan)
    counts = np.zeros(nbins, dtype=int)
    for j in range(nbins):
        m = (angle >= edges[j]) & (angle < edges[j + 1])
        nj = int(m.sum())
        counts[j] = nj
        if nj > 0:
            f = quenched[m].mean()
            fq[j] = f
            err[j] = np.sqrt(f * (1 - f) / nj)
    return centers, fq, err, counts


# --------------------------------------------------------------------------- catalog builder


def _host_morph_to_satellites(sdss, first_sub, n_subs, subfind_ids, n_sub, sn_min):
    """Broadcast each selected host's SDSS Sersic morphology/quality to its satellites."""
    theta = np.zeros(n_sub)
    flag = np.zeros(n_sub)
    sflag = np.zeros(n_sub)
    sn = np.zeros(n_sub)
    theta_all = np.asarray(sdss['sersic_theta']) * 180.0 / np.pi
    flag_all = np.asarray(sdss['flag'])
    sflag_all = np.asarray(sdss['flag_sersic'])
    sn_all = np.asarray(sdss['sn_per_pixel'])
    for k in range(len(first_sub)):
        c = first_sub[k]
        row = np.where(subfind_ids == c)[0]
        if row.size == 0:                       # host has no morphology entry -> mark unreliable
            flag[c + 1:c + n_subs[k]] = 1
            continue
        r = row[0]
        sl = slice(c + 1, c + n_subs[k])
        theta[sl] = theta_all[r]
        flag[sl] = flag_all[r]
        sflag[sl] = sflag_all[r]
        sn[sl] = sn_all[r]
    return theta, flag, sflag, sn


def compute_satellite_catalog(tng_root, host_logm_min, host_logm_max, sim='TNG100', snap=99, sn_min=2.5):
    """Per-satellite catalog for hosts with host_logm_min < log10(M200c, physical) < host_logm_max.

    `sim` ('TNG100' or 'TNG50') sets the box size used for the periodic wrap; `tng_root` is the
    absolute path to that simulation's directory (see `sim_root`). Only satellites of hosts with
    reliable g+i Sersic fits are returned; apply the satellite-mass cut in the notebook via
    `mstar_phys`.

    Returns a DataFrame with columns:
      host_id, host_m200_phys, host_m200_hinv, mstar_phys, mstar_hinv, sfr, alpha, quenched
    where `alpha` is the projected angle from the host major axis folded into [0, 90].
    """
    import h5py
    import illustris_python as il

    box_kpc = lbox_kpc(sim)
    p = tng_paths(tng_root, snap)
    groups = il.groupcat.loadHalos(
        p['basePath'], snap,
        fields=['GroupFirstSub', 'Group_M_Crit200', 'Group_R_Crit200', 'GroupNsubs'])
    subhalos = il.groupcat.loadSubhalos(
        p['basePath'], snap,
        fields=['SubhaloGrNr', 'SubhaloMassType', 'SubhaloCM', 'SubhaloSFR'])
    n_sub = len(subhalos['SubhaloGrNr'])

    sdss_g = h5py.File(p['morph_g'], 'r')
    sdss_i = h5py.File(p['morph_i'], 'r')
    subfind_ids = np.loadtxt(p['subfind_ids'])

    # ---- host selection on PHYSICAL M_200c ----
    host_logm200_phys = np.log10(groups['Group_M_Crit200'] * 1e10 / H)
    host_sel = (host_logm200_phys > host_logm_min) & (host_logm200_phys < host_logm_max)
    first_sub = groups['GroupFirstSub'][host_sel]
    n_subs = groups['GroupNsubs'][host_sel]
    m200_phys_sel = host_logm200_phys[host_sel]
    m200_hinv_sel = np.log10(groups['Group_M_Crit200'][host_sel] * 1e10)   # no /h

    sat_mask = np.zeros(n_sub, dtype=bool)
    host_id_arr = np.full(n_sub, -1, dtype=int)
    host_center = np.zeros((n_sub, 3))
    host_m200_phys = np.zeros(n_sub)
    host_m200_hinv = np.zeros(n_sub)
    for k in range(len(first_sub)):
        c = first_sub[k]
        sl = slice(c + 1, c + n_subs[k])
        sat_mask[sl] = True
        host_id_arr[sl] = k
        host_center[sl] = subhalos['SubhaloCM'][c] / H
        host_m200_phys[sl] = m200_phys_sel[k]
        host_m200_hinv[sl] = m200_hinv_sel[k]

    # ---- host orientation + quality ----
    tg, fg, sfg, sng = _host_morph_to_satellites(sdss_g, first_sub, n_subs, subfind_ids, n_sub, sn_min)
    ti, fi, sfi, sni = _host_morph_to_satellites(sdss_i, first_sub, n_subs, subfind_ids, n_sub, sn_min)
    host_theta = 0.5 * (tg + ti)
    host_good = ((fg == 0) & (sfg == 0) & (sng > sn_min) &
                 (fi == 0) & (sfi == 0) & (sni > sn_min))

    # ---- projected azimuthal angle (both foldings) ----
    rel = subhalos['SubhaloCM'] / H - host_center
    rel = rel - box_kpc * np.round(rel / box_kpc)               # periodic minimum image
    phi = np.degrees(np.arctan2(rel[:, 1], rel[:, 0]))
    alpha90, _ = fold_angles(phi, host_theta)          # [0, 90] fold (analysis is 0-90 only)

    # ---- masses, SFR, quench ----
    mstar_phys = np.log10(subhalos['SubhaloMassType'][:, 4] * 1e10 / H)
    mstar_hinv = np.log10(subhalos['SubhaloMassType'][:, 4] * 1e10)
    sfr = np.asarray(subhalos['SubhaloSFR'])

    sel = sat_mask & host_good
    df = pd.DataFrame({
        'host_id': host_id_arr[sel],
        'host_m200_phys': host_m200_phys[sel],
        'host_m200_hinv': host_m200_hinv[sel],
        'mstar_phys': mstar_phys[sel],
        'mstar_hinv': mstar_hinv[sel],
        'sfr': sfr[sel],
        'alpha': alpha90[sel],
        'quenched': quenched_flag(mstar_phys[sel], sfr[sel]),
    })
    return df

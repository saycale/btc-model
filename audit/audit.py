#!/usr/bin/env python3
"""Independent, deterministic checks for the btc-model browser implementation.

The script intentionally reads the embedded arrays from index.html, then
reimplements the mathematical core in Python.  It uses only NumPy and SciPy and
does not import or execute the JavaScript being audited.
"""

from __future__ import annotations

import json
import math
import re
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
from scipy import optimize, stats


ROOT = Path(__file__).resolve().parents[1]
HTML = (ROOT / "index.html").read_text(encoding="utf-8")
DATA = (ROOT / "data" / "observations.js").read_text(encoding="utf-8")
DAY = 86_400_000.0
GENESIS = datetime(2009, 1, 3, tzinfo=timezone.utc)


def extract_array(name: str, source: str = HTML) -> np.ndarray:
    match = re.search(rf"(?:const\s+{name}\s*=|{name}:)\s*\[(.*?)\]", source, re.S)
    if not match:
        raise RuntimeError(f"array {name!r} not found")
    body = re.sub(r"/\*.*?\*/|//.*?$", "", match.group(1), flags=re.S | re.M)
    return np.asarray([float(x) for x in body.replace("\n", " ").split(",") if x.strip()])


OBS = extract_array("OBS", DATA)
ADR = extract_array("ADR")
_last_date = re.search(r"OBS_LAST_DATE:\s*\[(\d+),(\d+),(\d+)\]", DATA)
if not _last_date:
    raise RuntimeError("OBS_LAST_DATE not found")
OBS_LAST_DATE = tuple(map(int, _last_date.groups()))


def month_range(year: int, month: int, count: int) -> list[tuple[int, int]]:
    out = []
    for _ in range(count):
        out.append((year, month))
        month += 1
        if month == 13:
            year += 1
            month = 1
    return out


OBS_MONTHS = month_range(2010, 7, len(OBS))
ADR_MONTHS = month_range(2010, 1, len(ADR))
ADR_BY_MONTH = dict(zip(ADR_MONTHS, ADR, strict=True))


def age_days(month: tuple[int, int], day: int = 15, origin: datetime = GENESIS) -> float:
    dt = datetime(month[0], month[1], day, tzinfo=timezone.utc)
    return (dt - origin).total_seconds() / 86_400.0


def month_end_age(month: tuple[int, int]) -> float:
    year, mon = month
    nxt = datetime(year + (mon == 12), 1 if mon == 12 else mon + 1, 1, tzinfo=timezone.utc)
    return (nxt - GENESIS).total_seconds() / 86_400.0 - 1.0


def observed_age(month: tuple[int, int], origin: datetime = GENESIS) -> float:
    if month == OBS_MONTHS[-1]:
        dt = datetime(*OBS_LAST_DATE, tzinfo=timezone.utc)
        return (dt - origin).total_seconds() / 86_400.0
    year, mon = month
    nxt = datetime(year + (mon == 12), 1 if mon == 12 else mon + 1, 1, tzinfo=timezone.utc)
    return (nxt - origin).total_seconds() / 86_400.0 - 1.0


def ols(x: np.ndarray, y: np.ndarray) -> dict[str, float]:
    X = np.column_stack((np.ones(len(x)), x))
    coef, *_ = np.linalg.lstsq(X, y, rcond=None)
    fitted = X @ coef
    resid = y - fitted
    sse = float(resid @ resid)
    syy = float(((y - y.mean()) ** 2).sum())
    sigma2 = sse / (len(y) - 2)
    cov = sigma2 * np.linalg.inv(X.T @ X)
    # Newey-West/HAC covariance with a 12-month bandwidth.  This does not solve
    # non-stationarity, but it demonstrates how much the iid standard error
    # understates uncertainty when neighbouring monthly residuals are similar.
    bread = np.linalg.inv(X.T @ X)
    meat = np.zeros((2, 2))
    for i in range(len(y)):
        meat += resid[i] ** 2 * np.outer(X[i], X[i])
    hac_lags = min(12, len(y) - 1)
    for lag in range(1, hac_lags + 1):
        weight = 1.0 - lag / (hac_lags + 1.0)
        cross = np.zeros((2, 2))
        for i in range(lag, len(y)):
            cross += resid[i] * resid[i - lag] * np.outer(X[i], X[i - lag])
        meat += weight * (cross + cross.T)
    hac_cov = bread @ meat @ bread
    return {
        "intercept": float(coef[0]),
        "slope": float(coef[1]),
        "r2": 1.0 - sse / syy,
        "se_slope_iid": float(math.sqrt(cov[1, 1])),
        "se_slope_hac12": float(math.sqrt(max(hac_cov[1, 1], 0.0))),
        "rmse": float(math.sqrt(np.mean(resid**2))),
        "sse": sse,
        "resid": resid,
    }


def autocorr(x: np.ndarray, lag: int) -> float:
    return float(np.corrcoef(x[:-lag], x[lag:])[0, 1])


def ljung_box_q(x: np.ndarray, lags: int) -> tuple[float, float]:
    n = len(x)
    q = n * (n + 2) * sum(autocorr(x, k) ** 2 / (n - k) for k in range(1, lags + 1))
    return float(q), float(stats.chi2.sf(q, lags))


def power_fit(prices: np.ndarray, months: list[tuple[int, int]], origin: datetime = GENESIS) -> dict[str, float]:
    x = np.log10([observed_age(m, origin=origin) for m in months])
    return ols(x, np.log10(prices))


REFERENCE_FIT = power_fit(OBS, OBS_MONTHS)
_REFERENCE_X = np.log10([observed_age(m) for m in OBS_MONTHS])
T_PIV = 10.0 ** float(_REFERENCE_X.mean())
LOGP_PIV = float(np.log10(OBS).mean())
B_REF = REFERENCE_FIT["slope"] / 3.0


def pure(month: tuple[int, int], beta: float = B_REF) -> float:
    q = 3.0 * beta
    intercept = LOGP_PIV - q * math.log10(T_PIV)
    return 10.0 ** (intercept + q * math.log10(age_days(month)))


S_TERM = 20.7e6
W_REF = 1610e6
L_REF = 657_000.0
HOLD = L_REF * S_TERM / W_REF


def plateau(owner_ceiling_m: float) -> float:
    return owner_ceiling_m * 1e6 * HOLD / S_TERM


def saturation(p: float | np.ndarray, level: float, softness: float = 3.0):
    p = np.asarray(p)
    return p * level / (p**softness + level**softness) ** (1.0 / softness)


EPOCHS = [
    ("H0", (2009, 1), (2011, 6), (2011, 11), 0.96, -0.19),
    ("H1", (2012, 11), (2013, 12), (2015, 1), 1.03, -0.28),
    ("H2", (2016, 7), (2017, 12), (2018, 12), 0.81, -0.24),
    ("H3", (2020, 5), (2021, 11), (2022, 11), 0.46, -0.38),
    ("H4", (2024, 4), (2025, 10), (2026, 6), 0.06, -0.37),
    ("H5", (2028, 4), (2029, 10), (2030, 9), None, None),
    ("H6", (2032, 4), (2033, 10), (2034, 9), None, None),
    ("H7", (2036, 4), (2037, 10), (2038, 9), None, None),
    ("H8", (2040, 4), (2041, 10), (2042, 9), None, None),
]


def mnum(month: tuple[int, int]) -> int:
    return month[0] * 12 + month[1]


def smoothstep(x: float) -> float:
    x = min(max(x, 0.0), 1.0)
    return 0.5 - 0.5 * math.cos(math.pi * x)


def phi_at(month: tuple[int, int], owner_ceiling_m: float, beta: float) -> float:
    dt = datetime(month[0], month[1], 15, tzinfo=timezone.utc)
    level = plateau(owner_ceiling_m)
    vals = []
    for delta_days in (-30, 30):
        shifted = dt.timestamp() + delta_days * 86_400
        tdays = (datetime.fromtimestamp(shifted, tz=timezone.utc) - GENESIS).total_seconds() / 86_400
        q = 3.0 * beta
        intercept = LOGP_PIV - q * math.log10(T_PIV)
        p = 10.0 ** (intercept + q * math.log10(tdays))
        vals.append((p, float(saturation(p, level))))
    return (math.log(vals[1][1]) - math.log(vals[0][1])) / (math.log(vals[1][0]) - math.log(vals[0][0]))


def amplitudes(de: float, dp: float, owner_ceiling_m: float, beta: float) -> list[tuple[float, float]]:
    r_a = 0.50 + 0.17 * de
    r_b = 1.0 - 0.5 * dp
    projected = []
    for i in range(4):
        if i == 0:
            projected.append((0.030 + de * (0.207 - 0.030), 0.37 * r_b))
        else:
            projected.append((projected[-1][0] * r_a, projected[-1][1] * r_b))
    out = []
    for i, epoch in enumerate(EPOCHS):
        if i <= 4:
            out.append((float(epoch[4]), float(epoch[5])))
        else:
            zeta = de + (1.0 - de) * phi_at(epoch[2], owner_ceiling_m, beta)
            a, b = projected[i - 5]
            out.append((a * zeta, -b * zeta))
    return out


def cycle_overlay(month: tuple[int, int], amps: list[tuple[float, float]]) -> float:
    cur = mnum(month)
    k = max((i for i, e in enumerate(EPOCHS) if cur >= mnum(e[1])), default=-1)
    if k < 0:
        return 0.0
    epoch = EPOCHS[k]
    a, b = amps[k]
    h, peak, trough = map(mnum, epoch[1:4])
    next_halving = mnum(EPOCHS[k + 1][1]) if k + 1 < len(EPOCHS) else h + 48
    if cur <= peak:
        return a * smoothstep((cur - h) / (peak - h))
    if cur <= trough:
        return a + (b - a) * smoothstep((cur - peak) / (trough - peak))
    return b + (0.0 - b) * smoothstep((cur - trough) / max(next_halving - trough, 1))


def expanding_forecasts() -> list[dict[str, float | str | int]]:
    rows = []
    y = np.log10(OBS)
    all_age = np.log10([age_days(m) for m in OBS_MONTHS])
    all_time = np.arange(len(OBS), dtype=float)
    for cutoff in ((2016, 12), (2020, 12), (2022, 12), (2024, 12)):
        n = OBS_MONTHS.index(cutoff) + 1
        test = slice(n, len(y))
        pp = ols(all_age[:n], y[:n])
        pred_power = pp["intercept"] + pp["slope"] * all_age[test]
        lt = ols(all_time[:n], y[:n])
        pred_loglinear = lt["intercept"] + lt["slope"] * all_time[test]
        pred_naive = np.full(len(y[test]), y[n - 1])
        rows.append({
            "cutoff": f"{cutoff[0]}-{cutoff[1]:02d}",
            "test_months": len(y[test]),
            "fitted_power_slope": pp["slope"],
            "rmse_power_dex": float(np.sqrt(np.mean((y[test] - pred_power) ** 2))),
            "rmse_loglinear_dex": float(np.sqrt(np.mean((y[test] - pred_loglinear) ** 2))),
            "rmse_last_price_dex": float(np.sqrt(np.mean((y[test] - pred_naive) ** 2))),
        })
    return rows


def walk_forward_by_horizon() -> list[dict[str, float | int]]:
    """Yearly-cutoff forecast comparison, following the cited paper's design."""
    y = np.log10(OBS)
    ages = np.log10([age_days(m) for m in OBS_MONTHS])
    errors: dict[int, dict[str, list[float]]] = {
        h: {"power": [], "naive": []} for h in (1, 3, 6, 12, 18, 24)
    }
    for year in range(2014, 2025):
        cutoff_month = (year, 1)
        if cutoff_month not in OBS_MONTHS:
            continue
        n = OBS_MONTHS.index(cutoff_month)  # train strictly before 1 January
        fit = ols(ages[:n], y[:n])
        for horizon in errors:
            target = n + horizon - 1
            if target >= len(y):
                continue
            pred_power = fit["intercept"] + fit["slope"] * ages[target]
            pred_naive = y[n - 1]
            errors[horizon]["power"].append(float(y[target] - pred_power))
            errors[horizon]["naive"].append(float(y[target] - pred_naive))
    rows = []
    for horizon, vals in errors.items():
        rows.append({
            "horizon_months": horizon,
            "cutoffs": len(vals["power"]),
            "rmse_power_dex": float(np.sqrt(np.mean(np.asarray(vals["power"]) ** 2))),
            "rmse_naive_dex": float(np.sqrt(np.mean(np.asarray(vals["naive"]) ** 2))),
        })
    return rows


def origin_sensitivity() -> list[dict[str, float | str]]:
    rows = []
    for origin in (
        datetime(2008, 1, 3, tzinfo=timezone.utc),
        datetime(2009, 1, 3, tzinfo=timezone.utc),
        datetime(2009, 7, 3, tzinfo=timezone.utc),
        datetime(2010, 1, 3, tzinfo=timezone.utc),
    ):
        fit = power_fit(OBS, OBS_MONTHS, origin)
        rows.append({"origin": origin.date().isoformat(), "slope": fit["slope"], "r2": fit["r2"]})
    return rows


def saturation_profile() -> list[dict[str, float]]:
    y = np.log10(OBS)
    x = np.log10([age_days(m) for m in OBS_MONTHS])
    rows = []
    for level in np.geomspace(150_000, 100_000_000, 25):
        def objective(params):
            intercept, slope = params
            p = 10.0 ** (intercept + slope * x)
            pred = np.log10(saturation(p, level))
            return float(np.mean((y - pred) ** 2))
        base = ols(x, y)
        fit = optimize.minimize(objective, [base["intercept"], base["slope"]], method="Nelder-Mead")
        rows.append({"level": float(level), "rmse_dex": math.sqrt(float(fit.fun)), "slope": float(fit.x[1])})
    return rows


def cycle_checks() -> dict[str, object]:
    level = plateau(1610)
    amps = amplitudes(0.15, 0.50, 1610, B_REF)
    trend = np.asarray([float(saturation(pure(m), level)) for m in OBS_MONTHS])
    overlay = np.asarray([cycle_overlay(m, amps) for m in OBS_MONTHS])
    residual_trend = np.log10(OBS / trend)
    residual_model = residual_trend - overlay
    peaks = np.asarray([1.03, 0.81, 0.46, 0.06])
    peak_fit = ols(np.arange(4, dtype=float), np.log(peaks))
    df = 2
    tcrit = stats.t.ppf(0.975, df)
    lo = peak_fit["slope"] - tcrit * peak_fit["se_slope_iid"]
    hi = peak_fit["slope"] + tcrit * peak_fit["se_slope_iid"]
    return {
        "trend_rmse_dex": float(np.sqrt(np.mean(residual_trend**2))),
        "cycle_model_rmse_dex": float(np.sqrt(np.mean(residual_model**2))),
        "cycle_model_mean_error_dex": float(residual_model.mean()),
        "cycle_model_lag1_autocorrelation": autocorr(residual_model, 1),
        "cycle_model_ljung_box_12": dict(zip(("Q", "p_iid_reference"), ljung_box_q(residual_model, 12), strict=True)),
        "peak_log_decay_per_cycle": peak_fit["slope"],
        "peak_decay_ratio": float(math.exp(peak_fit["slope"])),
        "peak_decay_ratio_95pct_iid": [float(math.exp(lo)), float(math.exp(hi))],
        "probability_of_strict_monotone_order_under_exchangeability": 1.0 / math.factorial(4),
        "panic_values_dex": [-0.28, -0.24, -0.38, -0.37],
    }


def main() -> None:
    age_fit = power_fit(OBS, OBS_MONTHS)
    common_months = [m for m in OBS_MONTHS if m in ADR_BY_MONTH]
    prices = np.asarray([OBS[OBS_MONTHS.index(m)] for m in common_months])
    addresses = np.asarray([ADR_BY_MONTH[m] for m in common_months])
    beta_fit = ols(np.log10(addresses), np.log10(prices))
    alpha_fit = ols(
        np.log10([month_end_age(m) for m in common_months]),
        np.log10(addresses),
    )
    direct_fit = ols(
        np.log10([month_end_age(m) for m in common_months]),
        np.log10(prices),
    )
    q12, p12 = ljung_box_q(age_fit["resid"], 12)
    profile = saturation_profile()
    best_profile = min(profile, key=lambda r: r["rmse_dex"])
    highest = profile[-1]
    result = {
        "source_revision_audited": "6827439d34570254eb220fcd51d37f2511956e35",
        "data_as_of": "2026-09-09 provisional spot",
        "sample": {"observations": len(OBS), "addresses": len(ADR), "common": len(common_months)},
        "reproduction": {
            "holding_usd_per_owner": HOLD,
            "plateau_usd": plateau(1610),
            "reference_price_slope": REFERENCE_FIT["slope"],
            "reference_beta_coordinate": B_REF,
            "base_amplitudes_h5_h7": [amplitudes(0.15, 0.50, 1610, B_REF)[i] for i in range(5, 8)],
            "base_zeta_h5_h7": [0.15 + 0.85 * phi_at(EPOCHS[i][2], 1610, B_REF) for i in range(5, 8)],
        },
        "power_law_full_sample": {
            k: v for k, v in age_fit.items() if k != "resid"
        } | {
            "lag1_residual_autocorrelation": autocorr(age_fit["resid"], 1),
            "ljung_box_12_Q": q12,
            "ljung_box_12_p_iid_reference": p12,
        },
        "metcalfe_decomposition": {
            "beta_price_on_addresses": {k: v for k, v in beta_fit.items() if k != "resid"},
            "alpha_addresses_on_age": {k: v for k, v in alpha_fit.items() if k != "resid"},
            "direct_price_on_age": {k: v for k, v in direct_fit.items() if k != "resid"},
            "alpha_times_beta": alpha_fit["slope"] * beta_fit["slope"],
            "note": "All three regressions reuse the same trending series; this is not independent validation.",
        },
        "origin_date_sensitivity": origin_sensitivity(),
        "expanding_window_forecasts": expanding_forecasts(),
        "walk_forward_by_horizon": walk_forward_by_horizon(),
        "saturation_profile": {
            "best_in_grid": best_profile,
            "at_100m_level": highest,
            "all": profile,
        },
        "cycles": cycle_checks(),
    }
    out = ROOT / "audit" / "results.json"
    out.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()

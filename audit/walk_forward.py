#!/usr/bin/env python3
"""Past-only baseline comparison on the repository's approximate monthly closes.

No imports from audit.py: its full-sample calibration must not enter this test.
Run with --write to refresh the summary; --details emits each forecast to stdout.
"""
import argparse
import calendar
import hashlib
import json
import re
from datetime import date
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
HORIZONS = (1, 3, 6, 12, 24)
MIN_TRAIN = 60
MODELS = ("last_price", "log_drift", "log_linear", "power_expanding", "power_60m")


def load_monthly(source):
    raw = re.search(r"window.BTC_MODEL_DATA\s*=\s*(\{.*\});", source, re.S).group(1)
    data = json.loads(re.sub(r"\b(OBS\w*)\s*:", r'"\1":', raw))
    prices = np.asarray(data["OBS"], dtype=float)
    year, month = data["OBS_START"]
    dates = []
    for i in range(len(prices)):
        y, m0 = divmod(year * 12 + month - 1 + i, 12)
        dates.append(date(y, m0 + 1, calendar.monthrange(y, m0 + 1)[1]))
    if data["OBS_LAST_PROVISIONAL"]:
        dates, prices = dates[:-1], prices[:-1]
    elif dates[-1] != date(*data["OBS_LAST_DATE"]):
        raise ValueError("Non-provisional last observation must be month-end")
    if len(prices) <= MIN_TRAIN or not np.all(np.isfinite(prices) & (prices > 0)):
        raise ValueError("Need positive finite prices and more than 60 months")
    ages = np.asarray([(d - date(2009, 1, 3)).days for d in dates], dtype=float)
    return dates, prices, ages


def predict(train_y, train_age, target_age, horizon):
    """Inputs contain training prices only; age is a known calendar covariate."""
    y, age = np.asarray(train_y), np.asarray(train_age)
    n = len(y)
    if n < MIN_TRAIN or len(age) != n or horizon < 1:
        raise ValueError("Invalid training window or horizon")

    def line(x, values, target):
        # Centre covariates for stable least-squares extrapolation.
        centred = x - x.mean()
        slope = np.dot(centred, values - values.mean()) / np.dot(centred, centred)
        return float(values.mean() + slope * (target - x.mean()))

    return {
        "last_price": float(y[-1]),
        "log_drift": float(y[-1] + horizon * (y[-1] - y[0]) / (n - 1)),
        "log_linear": line(np.arange(n, dtype=float), y, n - 1 + horizon),
        "power_expanding": line(np.log10(age), y, np.log10(target_age)),
        "power_60m": line(np.log10(age[-60:]), y[-60:], np.log10(target_age)),
    }


def forecasts(prices, ages, horizons=HORIZONS):
    y = np.log10(prices)
    records = []
    for n in range(MIN_TRAIN, len(y)):
        for h in horizons:
            target = n - 1 + h
            if target >= len(y):
                continue
            records.append({"origin_index": n - 1, "target_index": target,
                            "horizon_months": h, "actual_log10": float(y[target]),
                            "predicted_log10": predict(y[:n], ages[:n], ages[target], h)})
    return records


def summarise(records):
    rows = []
    for h in sorted({r["horizon_months"] for r in records}):
        selected = [r for r in records if r["horizon_months"] == h]
        errors = {m: np.asarray([r["predicted_log10"][m] - r["actual_log10"]
                                for r in selected]) for m in MODELS}
        mse_naive = float(np.mean(errors["last_price"] ** 2))
        for model, e in errors.items():
            mse = float(np.mean(e ** 2))
            rows.append({"horizon_months": h, "model": model, "n_origins": len(e),
                         "rmse_dex": float(np.sqrt(mse)), "mae_dex": float(np.mean(abs(e))),
                         "bias_dex": float(e.mean()),
                         "mse_skill_vs_last_price": 1 - mse / mse_naive if mse_naive > 0 else None})
    return rows


def run():
    source = (ROOT / "data/observations.js").read_bytes()
    dates, prices, ages = load_monthly(source.decode())
    records = forecasts(prices, ages)
    summary = {
        "protocol_version": 1,
        "source_sha256": hashlib.sha256(source).hexdigest(),
        "first_month_end": dates[0].isoformat(), "last_month_end": dates[-1].isoformat(),
        "n_closed_months": len(prices), "min_training_months": MIN_TRAIN,
        "origin_stride_months": 1, "horizons_months": list(HORIZONS),
        "limitations": [
            "Retrospective pseudo-out-of-sample exercise, not a preregistered experiment.",
            "Approximate current-vintage prices; not a verified point-in-time dataset.",
            "Overlapping errors and shared training samples: counts are not independent trials.",
            "No significance claim or confidence interval; no model selected for deployment.",
            "Full cross-scale model excluded: historical cycle nodes and ceiling are not past-only fitted.",
        ],
        "metrics": summarise(records),
    }
    return summary, records


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--details", action="store_true")
    args = parser.parse_args()
    summary, records = run()
    if args.write:
        (ROOT / "audit/walk_forward_results.json").write_text(
            json.dumps(summary, indent=2, allow_nan=False) + "\n", encoding="utf-8")
    print(json.dumps(records if args.details else summary, indent=2, allow_nan=False))

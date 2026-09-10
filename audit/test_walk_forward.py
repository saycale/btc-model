import json
import unittest
import numpy as np
from walk_forward import ROOT, forecasts, load_monthly, predict, run


class WalkForwardTests(unittest.TestCase):
    def test_exact_power_law(self):
        ages = np.arange(1, 81, dtype=float) * 30 + 500
        y = -4 + 3 * np.log10(ages)
        result = predict(y[:60], ages[:60], ages[71], 12)
        for model in ("power_expanding", "power_60m"):
            self.assertAlmostEqual(result[model], y[71], places=11)

    def test_future_prices_cannot_change_forecasts_at_same_origin(self):
        ages = np.arange(1, 91, dtype=float) * 30 + 500
        prices = ages ** 2
        before = forecasts(prices, ages)
        prices[65:] *= 100
        after = forecasts(prices, ages)
        for a, b in zip(before, after, strict=True):
            if a["origin_index"] < 65:
                self.assertEqual(a["predicted_log10"], b["predicted_log10"])

    def test_constant_prices_and_horizon_alignment(self):
        ages = np.arange(1, 91, dtype=float) * 30 + 500
        rows = forecasts(np.full(90, 100.0), ages)
        for row in rows:
            self.assertEqual(row["target_index"] - row["origin_index"], row["horizon_months"])
            self.assertTrue(all(v == 2 for v in row["predicted_log10"].values()))
        self.assertEqual(sum(r["horizon_months"] == 24 for r in rows), 7)

    def test_provisional_month_excluded(self):
        source = (ROOT / "data/observations.js").read_text()
        dates, prices, ages = load_monthly(source)
        self.assertEqual(dates[-1].isoformat(), "2026-08-31")
        self.assertEqual(len(prices), 194)

    def test_saved_results_reproduce(self):
        expected = json.loads((ROOT / "audit/walk_forward_results.json").read_text())
        actual, _ = run()
        metrics = expected.pop("metrics")
        calculated = actual.pop("metrics")
        self.assertEqual(expected, actual)
        for a, b in zip(metrics, calculated, strict=True):
            self.assertEqual(a.keys(), b.keys())
            for key in a:
                if isinstance(a[key], float):
                    self.assertAlmostEqual(a[key], b[key], places=10)
                else:
                    self.assertEqual(a[key], b[key])

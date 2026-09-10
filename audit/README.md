# Reproducible audit

Run from the repository root:

```bash
python3 audit/audit.py
```

The script extracts `OBS` from `data/observations.js` and `ADR` from `index.html`, independently
reimplements the mathematical core, and writes `audit/results.json`.

Requirements: Python 3.10+, NumPy, SciPy.

The written audit is pinned to commit
`6827439d34570254eb220fcd51d37f2511956e35`. The reproducer reads the current
embedded sample; `results.json` therefore also records its data date and the
current dynamically estimated reference slope.

## Monthly walk-forward comparison

```bash
python3 audit/walk_forward.py --write
python3 audit/walk_forward.py --details
python3 -m unittest discover -s audit -v
```

The first command regenerates `audit/walk_forward_results.json`; the second
prints all origin/target indices, actual log prices and model predictions.
Indices refer to the closed-month series beginning in July 2010.
See [protocol and findings](WALK_FORWARD.ru.md).

This separate protocol uses month-end dates and excludes the provisional month.
After 60 training months, every monthly origin produces 1/3/6/12/24-month
forecasts wherever the target is observed. Each model sees the same targets.
The expanding fits, drift and last-price baseline use only prices at or before
the origin; `power_60m` uses the latest 60 available months. No current fitted
reference or historical cycle nodes are imported from the browser/audit core.
The earlier `audit.py` comparisons are retained as legacy diagnostics; the
new file is the reference for this protocol.

Results are retrospective and descriptive: approximate current-vintage prices,
overlapping forecast errors, no significance or independent-trial claim.
The full cross-scale model is **not** backtested here: it still needs a defined
past-only cycle/ceiling calibration rule. No winner automatically changes the UI.

The browser's selectable deviation threshold is a separate in-sample diagnostic.
`test_diagnostics.js` verifies that changing it does not change MAE/RMSE.

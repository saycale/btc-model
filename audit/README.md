# Reproducible audit

Run from the repository root:

```bash
python3 audit/audit.py
```

The script extracts `OBS` and `ADR` from `index.html`, independently
reimplements the mathematical core, and writes `audit/results.json`.

Requirements: Python 3.10+, NumPy, SciPy.

The written audit is pinned to commit
`6827439d34570254eb220fcd51d37f2511956e35`. The reproducer reads the current
embedded sample; `results.json` therefore also records its data date and the
current dynamically estimated reference slope.

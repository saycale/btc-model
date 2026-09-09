# Reproducible audit

Run from the repository root:

```bash
python3 audit/audit.py
```

The script extracts `OBS` and `ADR` from `index.html`, independently
reimplements the mathematical core, and writes `audit/results.json`.

Requirements: Python 3.10+, NumPy, SciPy.

The audit is pinned to commit
`6827439d34570254eb220fcd51d37f2511956e35`.

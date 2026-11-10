# CIS*4150 Term Project: Staged CI/CT Pipeline for python-tabulate

Fork of [astanin/python-tabulate](https://github.com/astanin/python-tabulate) used to measure
which CI stage catches which kind of planted bug, and what each stage costs in run time.

## Pipeline (`.github/workflows/ci.yml`)

All stages are independent jobs, so every PR gets a result from every stage.

| Stage | Job | What it checks | Fails when |
|---|---|---|---|
| S1 | lint | `ruff check`, `ruff format --check` (ruff 0.15.4) | any lint/format violation |
| S2 | tests | pytest on Python 3.13, no optional libraries ("tests alone") | any test fails |
| S3 | coverage | pytest without, then with numpy/pandas/wcwidth; coverage combined | a test fails or combined branch coverage < 93% |
| S4 | matrix | pytest on 3.10 / 3.12 / 3.14, with and without optional libraries | any test fails in any environment |
| S5 | mutation | mutmut over `tabulate/` | mutation score < 80% (baseline 80.61%, 2195/2723 mutants killed) |

The upstream workflows (`lint.yml`, `tabulate.yml`) are kept for comparison but only run manually.

## Baseline (clean `master`, measured locally on Python 3.13, Windows)

| Setup | Tests | Branch coverage |
|---|---|---|
| No optional libraries | 323 passed, 60 skipped | 90% |
| numpy + pandas + wcwidth | 382 passed, 1 skipped | 92% |
| Combined | n/a | 93.05% |

## Running locally

```bash
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements/ci.txt                    # test.txt alone is enough for plain pytest

ruff check && ruff format --check                    # S1
python -m pytest                                      # S2
pip install -r requirements/extras.txt && python -m pytest   # with optional libraries
mutmut run && mutmut export-cicd-stats && python scripts/check_mutation.py 80  # S5 (Linux/macOS only)
```

## Reproducibility

- Tool versions pinned in `requirements/ci.txt`; optional libraries pinned in `requirements/extras.txt`.
- `PYTHONHASHSEED=0` in CI.
- Pinned numpy 2.5.4 / pandas 3.1.1 require Python >= 3.12, so the 3.10 matrix entry runs without extras.

## Planted-bug procedure

1. `git checkout master && git checkout -b bug-NN-short-name`
2. Make one change (code bug, regression, optional-library bug, or test weakening).
3. Push and open a PR **against this fork's `master`** (not upstream).
4. Record each stage's pass/fail and duration in the bug log. Close the PR without merging.

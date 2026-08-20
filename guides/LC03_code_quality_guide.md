# LC3 follow-along guide — Code quality and error handling

*EG2140 · Lecturecise 3 hands-on, ~45 min. Companion files: [lc03_before.py](companions/lc03_before.py) (what we start from) and [lc03_after.py](companions/lc03_after.py) (where we end) — download both from the course material's `guides/companions/` folder and put them in your toolbox repo root; the files use its `data/svedala/` folder.*

## Part A — Live refactor (25 min, work along)

Run the starting point and confirm it *works*:

```bash
python lc03_before.py
```

Working is not the same as good. We refactor together, in this order — after each step, run it again (the four zone totals must not change; how they are printed may improve along the way):

1. **Name things.** `f` → `zone_load_totals`, `d`/`d2` → `loads`/`buses`, `r` → `totals`, `x` → `scaling`. Rename the call at the bottom too — `f(1)` must become `zone_load_totals(1)` or the run dies with a `NameError`. Names are the cheapest documentation there is.
2. **Kill the top-level call.** `zone_load_totals(1)` at module bottom runs on *import* — move it under `if __name__ == "__main__":`. A module you cannot import without side effects cannot be tested.
3. **Lift the magic.** The hard-coded path becomes a `DATA_DIR` constant and a function parameter with a default. (The after-file uses `pathlib.Path` — standard-library path objects, where `/` joins path pieces; a plain string works here too.)
4. **Replace the loop with the idea.** Row-by-row dictionary building is pandas written as C. `loads["bus"].map(buses[...])` then `groupby().sum()` says *what* is computed, not *how*. **The old print loop goes with it**: iterating a pandas Series yields values, not keys, so `for k in totals: print(k, totals[k])` now dies with a cryptic `KeyError` — print the returned Series under `__main__` instead (`print(zone_load_totals().round(0))`).
5. **Docstring:** one sentence of what, one of what it raises. Comments explain *why*; the code now explains *what*.

Compare your end state with `lc03_after.py`. Not identical is fine — *reviewable* is the bar.

## Part B — Error handling (15 min)

The original has `except: pass`. What was it hiding? Not crashes — a load row referencing a bus that does not exist would simply be **dropped from the totals**: wrong answer, delivered confidently, four plausible numbers with a hole in one of them. That is what a bare except buys you. The refactored version raises instead — try it by asking for a data folder that is not there:

```bash
python -c "from lc03_after import zone_load_totals; zone_load_totals(data_dir='wrong/path')"
```

A clean `FileNotFoundError` with the path in it. The rules we now apply everywhere:

- **Fail loudly.** No bare `except:`, ever. Catch the *specific* exception you can actually handle; let the rest crash with a good message.
- **Validate at the boundary.** `zone_load_totals` rejects `scaling <= 0` with a `ValueError` *saying what it got*. Garbage stopped at the door beats garbage in the results.
- **Raise with information.** Compare `raise KeyError(f"loads reference buses without a zone: {missing}")` with `raise KeyError`. Same line count; one is a bug report, the other a shrug.
- **Log, don't print.** Prints inside functions pollute every caller. Return values; let `__main__` do the printing. When a function does need to say something, that is what `logging` is for.

### B4. One line of logging (3 min)

The lecture covered `logging`: a module asks for a logger named after itself and never configures anything; the program that runs it decides where messages go. Do it once here, so the idea is in your fingers before Lab 2.

Add at the top of `lc03_after.py`:

```python
import logging

log = logging.getLogger(__name__)
```

Add one line inside `zone_load_totals`, just before the `return`:

```python
    log.debug("zone totals computed for %d loads, scaling=%s", len(loads), scaling)
```

Then run it twice — once as it is, once asking to see debug messages:

```bash
python lc03_after.py
python -c "import logging; logging.basicConfig(level=logging.DEBUG); import lc03_after; print(lc03_after.zone_load_totals().round(0))"
```

**Checkpoint:** the first run prints only the report; the second also prints the debug line, with no change to the function itself. That separation — the module produces messages, the program decides what to show — is the whole point.

## Part C — Notebooks vs modules (5 min)

The LC1 warm-up was a notebook; Lab 1 turned it into a module. That is the pattern for the whole course: **notebooks are for exploring and explaining; anything you keep becomes a module.** If a notebook cell gets copy-pasted twice, it wants to be a function in `src/`.

One piece of hygiene before tomorrow: `lc03_before.py` and `lc03_after.py` are scratch, not toolbox — delete them from your repo (or add them to `.gitignore`) now, or Lab 1's `git add -A` habit will quietly commit them into the history that Lab 2's pod check reviews.

## Self-check

1. Your refactor still prints the same four zone totals as the original (you refactored your copy in place — the untouched original is `guides/companions/lc03_before.py` in the course material)
2. You can say, in one sentence each, why `except: pass` and top-level calls are dangerous
3. Tomorrow's lab: the same treatment, on a 70-line screener, for keeps

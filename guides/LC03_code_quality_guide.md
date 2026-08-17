# LC3 follow-along guide — Code quality and error handling

*EG2140 · Lecturecise 3 hands-on, ~45 min. Companion files: `lc03_before.py` (what we start from) and `lc03_after.py` (where we end). Run from your toolbox repo root — the files use its `data/svedala/` folder.*

## Part A — Live refactor (25 min, work along)

Run the starting point and confirm it *works*:

```bash
python lc03_before.py
```

Working is not the same as good. We refactor together, in this order — after each step, run it again (behaviour must not change):

1. **Name things.** `f` → `zone_load_totals`, `d`/`d2` → `loads`/`buses`, `r` → `totals`, `x` → `scaling`. Names are the cheapest documentation there is.
2. **Kill the top-level call.** `f(1)` at module bottom runs on *import* — move it under `if __name__ == "__main__":`. A module you cannot import without side effects cannot be tested.
3. **Lift the magic.** The hard-coded path becomes a `DATA_DIR` constant and a function parameter with a default.
4. **Replace the loop with the idea.** Row-by-row dictionary building is pandas written as C. `loads["bus"].map(buses[...])` then `groupby().sum()` says *what* is computed, not *how*.
5. **Docstring:** one sentence of what, one of what it raises. Comments explain *why*; the code now explains *what*.

Compare your end state with `lc03_after.py`. Not identical is fine — *reviewable* is the bar.

## Part B — Error handling (15 min)

The original has `except: pass`. Delete it and see what it was hiding:

```bash
python -c "from lc03_after import zone_load_totals; zone_load_totals(data_dir='wrong/path')"
```

A clean `FileNotFoundError` with the path in it. The bare except would have printed *an empty report* instead — wrong answer, delivered confidently. The rules we now apply everywhere:

- **Fail loudly.** No bare `except:`, ever. Catch the *specific* exception you can actually handle; let the rest crash with a good message.
- **Validate at the boundary.** `zone_load_totals` rejects `scaling <= 0` with a `ValueError` *saying what it got*. Garbage stopped at the door beats garbage in the results.
- **Raise with information.** Compare `raise KeyError(f"loads reference buses without a zone: {missing}")` with `raise KeyError`. Same line count; one is a bug report, the other a shrug.
- **Log, don't print.** Prints inside functions pollute every caller. Return values; let `__main__` do the printing. (Proper `logging` arrives with the project.)

## Part C — Notebooks vs modules (5 min)

The L1 warm-up was a notebook; Lab 1 turned it into a module. That is the pattern for the whole course: **notebooks are for exploring and explaining; anything you keep becomes a module.** If a notebook cell gets copy-pasted twice, it wants to be a function in `src/`.

## Self-check

1. Your refactor still prints the same four zone totals as `lc03_before.py`
2. You can say, in one sentence each, why `except: pass` and top-level calls are dangerous
3. Tomorrow's lab: the same treatment, on a 70-line screener, for keeps

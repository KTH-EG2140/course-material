# Lab 5 — Acquire, clean, store: a data pipeline in the toolbox

*EG2140 · **self-paced** — do it with your lab partner during the week; your pod is first support (partner → pod → Discussions → the TA sessions) · ~110 min · host repo: the partner whose name comes LAST alphabetically in today's pair. Quiz 2 at its sitting reads Lecturecises 6–7 and this lab's working method; the room then stays open as a TA session. No AI tools.*

Lecturecises 6 and 7 did this in a notebook. A notebook is where analysis is *found*; the toolbox is where it goes to *live*. This lab moves the pattern into `svedala_toolbox` as tested, rerunnable code.

## 0. Setup (10 min)

Every workbook was created from the same template, so the two stubs are already in your host repo: `src/svedala_toolbox/pipeline.py` (three functions with TODO docstrings — read them, they carry the specification) and `tests/test_pipeline.py` (two placeholders). Confirm, with the venv active:

```bash
git switch main && git pull
pytest tests/test_pipeline.py -q
```

```
ss                                                                       [100%]
2 skipped in 0.17s
```

Two `s` for two `pytest.skip(...)` placeholders — the tests you replace today. Decide the split of work in the pair: one drives the fetch/cache side, one the clean/store side, then swap for review.

**About the token.** A real ENTSO-E fetch needs the API token LC6 showed you how to request. It goes in the environment variable `ENTSOE_TOKEN` or in a file `entsoe_token.txt` in the repo root — and that file goes into `.gitignore` *before* it exists (`echo "entsoe_token.txt" >> .gitignore`), because every student can read every workbook repo. Nothing in this lab requires a token to *pass*: the tests read a cached sample by design, and a pair without a token can use the course sample in section 1.

## 1. Fetch with cache and provenance (~30 min)

Implement `fetch_load(zone, start, end, cache_dir)` in `pipeline.py` following the LC6 pattern:

- **Cache first.** The key is `f"load_{zone}_{start}_{end}"`; the Parquet file `cache_dir / f"{key}.parquet"`. If it exists, read it and return the `load_mw` column — no token needed, no network touched.
- **On a miss**, fetch with entsoe-py exactly as LC6's `cached_load` did, resample to hourly, convert the index to UTC, write the Parquet, and write the JSON sidecar next to it (source, zone, period, `retrieved_utc`, unit). Put `from entsoe import EntsoePandasClient` *inside* the function, as LC6 did: an import inside a function runs only when that function reaches it, so a machine that only ever hits the cache never needs the library to work.
- **Token order**: environment variable, then the file, and if neither exists raise a `RuntimeError` that says so. On the reference solution a cache miss without a token stops with:

```
RuntimeError: no ENTSO-E token: set ENTSOE_TOKEN or create entsoe_token.txt (never commit it)
```

One label on the stub's default: `cache_dir="data_cache"` is a path *relative to where you run* — fine for a command started from the repo root, the same run-from-root condition as LC3's demo. The tests do not rely on it; they pass an explicit folder built from `__file__`, the way `loader.py` builds `DATA_DIR`. Start the function with `cache_dir = Path(cache_dir)` so a plain string works too.

**The test must pass without a token.** That means a small cached sample committed under `tests/data/load_cache/`: one week of one zone, two files (`.parquet` + `.json`). Either fetch a week once with a token and copy the two files from `data_cache/` there, or — if nobody in the pair has a token yet — download the course sample, [load_SE_3_2025-01-01_2025-01-08.parquet](lab5-cache-sample/load_SE_3_2025-01-01_2025-01-08.parquet) and [load_SE_3_2025-01-01_2025-01-08.json](lab5-cache-sample/load_SE_3_2025-01-01_2025-01-08.json), into that folder (its sidecar says honestly where it came from). Then replace the first placeholder in `tests/test_pipeline.py`:

```python
from pathlib import Path

from svedala_toolbox.pipeline import fetch_load

# The committed sample lives next to the tests, found from this file's own location.
CACHE = Path(__file__).parent / "data" / "load_cache"


def test_fetch_uses_cache_without_token(monkeypatch):
    # monkeypatch.delenv removes the variable for this test only - no token, no network.
    monkeypatch.delenv("ENTSOE_TOKEN", raising=False)
    s = fetch_load("SE_3", "2025-01-01", "2025-01-08", cache_dir=CACHE)
    assert len(s) == 168, f"one week of hours expected, got {len(s)}"
    assert str(s.index.tz) == "UTC"
```

`monkeypatch` is a pytest fixture (LC5): it changes something for the duration of one test and undoes it afterwards — here it makes sure the test cannot accidentally use your token. Match the zone and dates to your sample's file name.

**Checkpoint:** `pytest tests/test_pipeline.py -q` → `1 passed, 1 skipped`. Commit — the two sample files included, `data_cache/` itself not (add `data_cache/` to `.gitignore`).

## 2. Clean, with a repairs log (~40 min)

Implement `clean_load(series) -> (series, repairs)` doing, in order: UTC index enforcement, de-duplication, impossible-value removal (negative values, and spikes further than 4 standard deviations from a 49-hour centred rolling median — the LC7 rule), interpolation of gaps ≤ 3 h. `repairs` is a list of human sentences — the LC7 habit. Name the rules as constants at the top of the module (`SPIKE_WINDOW_H = 49`, `SPIKE_SIGMAS = 4.0`, `MAX_GAP_H = 3`) so the log can quote them.

- **UTC**: a tz-aware index gets `tz_convert("UTC")`; a naive one is LC7's case — Swedish local time — so `tz_localize("Europe/Stockholm", ambiguous="infer", nonexistent="shift_forward")` first, and a log sentence saying you assumed that.
- **Duplicates**: `s.index.duplicated()` marks the repeats; keep the first, log how many went.
- **Impossible values**: the LC7 lines, on a Series instead of a DataFrame column. Set them to NaN — you do not know the true value, so say so.
- **Gaps — the trap of this lab.** `s.interpolate(limit=3)` does *not* mean "bridge gaps up to 3 hours". It means "fill at most 3 consecutive missing values", so it fills the **first three hours of every gap, however long** — a 72-hour outage comes back with its first three hours invented and the rest missing. Measure each gap before deciding:

```python
gap_id = s.notna().cumsum()                          # same number for every hour of one gap
gap_len = s.isna().groupby(gap_id).transform("sum")  # that gap's length, written on each of its hours
short_gap = s.isna() & (gap_len <= MAX_GAP_H)
s[short_gap] = s.interpolate(limit_area="inside")[short_gap]
```

  `cumsum()` on the True/False of `notna()` increases by one at every real value and stays flat across a gap, so all hours of one gap share a number; grouping on that number and summing `isna()` gives each gap its length. **Decide and document**: what does your function do with a 72-hour gap, and why? The reference leaves it as NaN — inventing three days of load would be a forecast, not a repair — and says so in the docstring and the log.

Replace the second placeholder. The hard part of testing a cleaner is having something dirty; build it by hand, small, so you know exactly what is wrong with it:

```python
import pandas as pd


def dirty_series() -> pd.Series:
    """200 hours of flat load with one duplicate hour, one negative, one spike, a 2 h gap and a 6 h gap."""
    idx = pd.date_range("2025-03-01", periods=200, freq="h", tz="UTC")
    s = pd.Series(3000.0, index=idx)
    s.iloc[10] = -5.0                       # impossible
    s.iloc[50] = 30000.0                    # spike, ten times the level
    s.iloc[100:102] = float("nan")          # 2 h gap  -> interpolated
    s.iloc[150:156] = float("nan")          # 6 h gap  -> left as NaN
    s = pd.concat([s, s.iloc[[20]]]).sort_index()   # duplicated timestamp
    return s
```

Then the asserts are yours: no duplicated index entries, nothing negative among the remaining values, the spike gone, hours 100–101 filled, hours 150–155 still NaN, and the log a list of sentences. On the reference solution the log for this series reads:

```
1 duplicated timestamps dropped (first occurrence kept).
1 negative and 1 spike values (> 4 std from the 49 h rolling median) set to NaN.
4 of 10 missing hours interpolated (gaps <= 3 h); 6 left as NaN.
```

(The ten missing hours are the negative, the spike, and the two gaps; the four interpolated are those two plus the 2-hour gap.) Write your interpolate line the naive way first, `s.interpolate(limit=3)`, and watch this test fail on the 6-hour gap — that red run is the lesson; then put the gap-length version in.

**Checkpoint:** `pytest tests/test_pipeline.py -q` → `2 passed`. Commit and push.

## 3. Store and query (~25 min)

`store(series, db_path)` writes Parquet next to `db_path` (`db_path.with_suffix(".parquet")`) and registers it in a DuckDB database:

```python
import duckdb                          # inside store(): only this function needs it
con = duckdb.connect(str(db_path))
con.execute(f"CREATE OR REPLACE TABLE {table} AS SELECT * FROM read_parquet('{parquet_path.as_posix()}')")
con.close()
```

`CREATE OR REPLACE` makes a rerun harmless — LC7's rule that a pipeline must be safe to run twice. Write the Series as a two-column table (`series.rename("load_mw").to_frame().reset_index()`), so the timestamp is a column DuckDB can query, not an index it cannot see.

Add one query function the pair designs itself — daily peaks, morning ramp, weekend/weekday means, your choice — and use it in a short demo in your README. The reference's `daily_peaks(db_path)` on the sample week:

```
         day  peak_mw
0 2025-01-01   3927.5
1 2025-01-02   4375.7
2 2025-01-03   4630.2
```

A third test, with pytest's `tmp_path` fixture (a fresh empty folder that pytest creates for the test and deletes afterwards, so no database file is left in your repo): clean the dirty series, `store` it into `tmp_path / "test.duckdb"`, open the database read-only and `SELECT count(*) FROM hourly` — 200 rows. Add `*.duckdb` and `*.parquet` at the repo root to `.gitignore` — the committed sample under `tests/data/` is the one Parquet that belongs in the history.

**Checkpoint:** `pytest tests/ -q`. On the reference solution:

```
11 passed, 5 skipped in 4.78s
```

Your count: Lab 2's count plus three; the five `s` are Labs 6–8 waiting. Commit, push, CI green — without a token, on a machine that has never seen ENTSO-E.

## 4. Pod check (15 min)

The other pair reads your `pipeline.py`, its tests, and your repairs-log design. Three sentences as an Issue in the host repo (**Issues** tab → **New issue**, titled "Lab 5 pod check"): one thing done well, one improvement, one question. Nothing handed in, nothing graded.

## Done when

Tests green in CI without a token, provenance sidecar written on a real fetch (whoever in the pod has a token — the sidecar is the proof the fetch path works), pod check written and received — before the Quiz 2 sitting, whose questions build on this material.

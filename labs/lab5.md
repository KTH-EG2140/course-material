# Lab 5 — Acquire, clean, store: a data pipeline in the toolbox

*EG2140 · **self-paced** — do it with your lab partner during the week; your pod is first support (partner → pod → Discussions → the TA sessions) · ~110 min · host repo: alternate as usual. Quiz 2 at its sitting reads Lecturecises 6–7 and this lab's working method. No AI tools.*

Lecturecises 6 and 7 did this in a notebook. A notebook is where analysis is *found*; the toolbox is where it goes to *live*. This lab moves the pattern into `svedala_toolbox` as tested, rerunnable code.

## 0. Setup
Pull the latest template stubs if your repo predates them (`src/svedala_toolbox/pipeline.py`, `tests/test_pipeline.py`). Decide the split of work in the pair — one drives the fetch/cache side, one the clean/store side, then swap for review.

## 1. Fetch with cache and provenance (~30 min)
Implement `fetch_load(zone, start, end, cache_dir)` in `pipeline.py` following the LC6 pattern: Parquet cache, JSON provenance sidecar, token from file/env — never from source code. Your test must pass **without** a token (cache a small sample and commit it under `tests/data/`; the test reads the cache).

## 2. Clean, with a repairs log (~40 min)
Implement `clean_load(series) -> (series, repairs)` doing, in order: UTC index enforcement, de-duplication, impossible-value removal (negative values, and spikes further than 4 standard deviations from a 49-hour centred rolling median — the LC7 rule), interpolation of gaps ≤ 3 h. `repairs` is a list of human sentences — the LC7 habit. **Decide and document**: what does your function do with a 72-hour gap, and why?

## 3. Store and query (~25 min)
`store(series, db_path)` writes Parquet and registers it in a DuckDB database. Add one query function the pair designs itself (daily peaks, morning ramp, weekend/weekday means — your choice) and use it in a short demo in your README.

## 4. Pod check (15 min)
The other pair reads your `pipeline.py`, its tests, and your repairs-log design. Three sentences as an issue ("Lab 5 pod check"): one thing done well, one improvement, one question. Nothing handed in, nothing graded.

## Done when
Tests green in CI without a token, provenance sidecar written on a real fetch, pod check written and received — before the Quiz 2 sitting, whose questions build on this material.

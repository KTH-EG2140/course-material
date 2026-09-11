# Lab 8 — Classify N-1 security: milliseconds instead of minutes

*EG2140 · **self-paced** — do it with your lab partner during the week; your pod is first support (partner → pod → Discussions → the TA sessions) · ~110 min · host repo: the partner whose name comes LAST alphabetically in today's pair. Quiz 4 at its sitting covers Lecturecises 10–12. No AI tools.*

Your screener answers "is this operating point N-1 secure?" with a minute of power flows. An operator screening thousands of scenarios wants the answer in milliseconds. This lab trains classifiers to approximate your screener — and, more importantly, teaches you to decide **when to trust which**.

**Before you start.** The host repo needs Lab 1 (loader) and Lab 2 (screener) — `build_security_dataset` calls both. Walk LC11 and LC12 first: the classifier twins of LC11's models and LC12's three-way split are what you use here. The stub is `src/svedala_toolbox/security.py`; the year is your course-material clone's `data/svedala-year/svedala_hourly.parquet` (`CM = "<cm>"` as in Labs 6–7).

## 1. Build the labelled dataset (~35 min)

Implement `build_security_dataset(net_loader, year_parquet, n_hours=250, seed=7)` in `security.py`. `net_loader` is a *function* — pass `load_svedala` itself, without parentheses, and the function calls it to get a fresh network; `seed` pins the random sample of hours so a rerun gives the same table. Four steps per sampled hour:

1. **Sample** `n_hours` timestamps from the year: `rng = np.random.default_rng(seed)` then `rng.choice(year.index, size=n_hours, replace=False)` (`replace=False` = no hour twice; `sorted(...)` puts them in time order).
2. **Scale the loads** to the hour, zone by zone: the base network's MW per zone is `net.load["p_mw"].groupby(zone_of_each_load).sum()` — the zone of a load is the zone of its bus, `net.bus.loc[net.load["bus"], "zone"]` (your Lab 1 loader put the `ZON_*` name there) — and each load is multiplied by *that hour's zone MW ÷ base zone MW*. Keep copies of the base `p_mw` and `q_mvar` and scale both from the copies every hour, never from the previous hour.
3. **Scale the generation too** — the trap of this lab. Loads on a June afternoon are 45 % of the base case; leave the generators at base and the slack bus must absorb the other 55 %, and the power flow stops converging — every hour comes out "insecure" and the dataset is worthless. Multiply every *non-slack* generator's `p_mw` (`~net.gen["slack"]`) by the total factor, this hour's total load ÷ base total load. (On the reference solution, without this step: 250 of 250 hours insecure; with it: 71.)
4. **Label** with the screener's criterion: run the base case, then the outages, and call the hour insecure the moment any case overloads a line or fails to converge (line loadings only, as in Lab 2 — transformer ratings are placeholders). The features are the hour's four zone loads and three temperatures — what an operator knows *before* any power flow — plus the boolean `insecure`. Restore the base loads and generation before returning.

**The speed-up, and what it costs.** The stub calls full 52-outage labelling slow; measure it before believing that. On the reference laptop the full screening of 250 hours takes about **two minutes** (most hours are secure and every outage must be checked; an insecure hour stops at its first violation). A documented shortcut: screen each hour against only the **12 severest outages of the base-case ranking** — your Lab 2 table, sorted by `max_loading_percent` — and the build takes 23 seconds. What it can miss: an outage that is harmless at the base case but becomes the critical one under a different load pattern would leave the hour labelled secure. On a 60-hour check the reference shortcut agreed with the full screening on all 60 (21 insecure); say in the docstring which policy you chose and, if you took the shortcut, that number. Either policy is acceptable; an undocumented one is not.

**Checkpoint** on the reference solution, in a scratch notebook `notebooks/lab8_explore.ipynb` (committed):

```python
import pandas as pd
from svedala_toolbox.loader import load_svedala
from svedala_toolbox.security import build_security_dataset
ds = build_security_dataset(load_svedala, f"{CM}/data/svedala-year/svedala_hourly.parquet", n_hours=250, seed=7)
print(ds.shape, "| insecure share", round(ds["insecure"].mean(), 2))
print(ds.head(2).round(1))
```

```
(250, 8) | insecure share 0.28
                           ZON_NORR  ZON_MITT  ZON_SYDVÄST  ZON_EXTERN  temp_north  temp_mid  temp_south  insecure
timestamp
2025-01-02 08:00:00+00:00     791.5    4159.4        956.8      1372.4       -17.1      -6.8         0.4      True
2025-01-02 20:00:00+00:00     736.3    4107.6        863.0      1352.5       -16.7      -6.9         1.5      True
```

About one hour in four insecure, as the year was built to be. Commit the table: `ds.to_csv("tests/data/security_dataset.csv")` — 18 kB, expensive to rebuild, and the test below reads it. Two tests in `tests/test_security.py` (replace the placeholder, keep its name, add one): the committed table holds both classes and its columns are exactly the seven features plus `insecure`; and a live build with `n_hours=3` and a fixed seed gives three rows twice, the same hours both times (four seconds — the base screening dominates). **Checkpoint:** `pytest tests/test_security.py -q` → `2 passed`; `pytest -q` → Lab 7's count plus two (`16 passed` on the reference solution — its last placeholder is gone now). Commit `security.py`, the tests and the table; push.

## 2. Train and compare (~30 min)

Split **temporally** — hours before 1 October train, October onward test (`ds.index < pd.Timestamp("2025-10-01", tz="UTC")`; the index is UTC, so the cut-off must be too). Three classifiers, the `fit`/`predict` contract from LC10: `LogisticRegression` inside `make_pipeline(StandardScaler(), ...)` (a linear model that outputs a probability — scale it, as LC12 taught), `DecisionTreeClassifier(max_depth=3)` (LC11's readable tree), `HistGradientBoostingClassifier` (LC11's winner). Score with `accuracy_score`, `precision_score` and `recall_score` from `sklearn.metrics`, the last two for the insecure class (`True` is the positive class by default).

On the reference solution (180 training hours, 24 % insecure; 70 test hours, 36 % insecure):

```
logistic  accuracy 0.94  precision(insecure) 0.89  recall(insecure) 0.96
tree      accuracy 0.96  precision(insecure) 0.89  recall(insecure) 1.00
gbdt      accuracy 0.96  precision(insecure) 0.89  recall(insecure) 1.00
```

Accuracy is the WRONG headline here: the classes are imbalanced, and a model that called every hour secure would score 64 % while missing every dangerous hour. Read precision and recall for the insecure class instead — recall 1.00 means the tree missed no insecure hour; precision 0.89 means one flag in nine was a false alarm.

## 3. The engineering question (~30 min)

A false negative (calling an insecure hour secure) risks the grid; a false positive wastes an engineer's check. `predict` uses a probability threshold of 0.5; `m.predict_proba(X)[:, 1]` gives the probability itself, and `proba >= threshold` is your own decision rule. Sweep it:

```
gbdt threshold 0.5: precision 0.89  recall 1.00  flagged 0.40
gbdt threshold 0.3: precision 0.83  recall 1.00  flagged 0.43
gbdt threshold 0.1: precision 0.76  recall 1.00  flagged 0.47
```

On the reference table recall is already 1.00 at 0.5 — this problem is easy, because the load level almost decides it — and lowering the threshold only buys false alarms. Your table will differ; the reasoning does not. **Choose an operating threshold** and defend it in one paragraph in the README: what miss rate do you accept, what does a miss cost, what does a false alarm cost? This paragraph is the deliverable — the models are interchangeable, the judgment is not.

## 4. Pod check (15 min)

Three sentences as an Issue in the other pair's host repo (**Issues** tab → **New issue**), titled "Lab 8 pod check" — at least one about their threshold argument. Nothing handed in, nothing graded.

## Done when

Dataset committed with its labelling policy documented in the docstring, three models compared on precision and recall, threshold argued in the README, pod check exchanged — before the Quiz 4 sitting.

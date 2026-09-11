# Lab 8 — Classify N-1 security: milliseconds instead of minutes

*EG2140 · **self-paced** — do it with your lab partner during the week; your pod is first support (partner → pod → Discussions → the TA sessions) · ~110 min · host repo: the partner whose name comes LAST alphabetically in today's pair. Quiz 4 at its sitting covers Lecturecises 10–12. No AI tools.*

Your screener answers "is this operating point N-1 secure?" with a minute of power flows. An operator screening thousands of scenarios wants the answer in milliseconds. This lab trains classifiers to approximate your screener — and, more importantly, teaches you to decide **when to trust which**.

**Before you start.** The host repo needs Lab 1 (loader) and Lab 2 (screener): the dataset builder calls your loader for the network and your screener once, for the base-case ranking, and reuses the screener's *criterion* for every hour. Walk LC11 and LC12 first: the classifier twins of LC11's models and LC12's discipline about never choosing on the test set are what you use here. The stub is `src/svedala_toolbox/security.py`. The year of hourly data comes into the workbook, as the EQ file did in Lab 6, because the tests read it and CI sees only your repo:

```bash
mkdir -p data/svedala-year notebooks
cp <cm>/data/svedala-year/svedala_hourly.parquet data/svedala-year/     # 286 kB, committed
git add data/svedala-year/svedala_hourly.parquet && git commit -m "Add the hourly year for the Lab 8 dataset"
```

## 1. Build the labelled dataset (~35 min)

Implement `build_security_dataset(net_loader, year_parquet, n_hours=250, seed=7)` in `security.py`. `net_loader` is a *function* — pass `load_svedala` itself, without parentheses, and the function calls it to get a fresh network; `seed` pins the random sample of hours so a rerun gives the same table. Four steps per sampled hour:

1. **Sample** `n_hours` timestamps from the year: `rng = np.random.default_rng(seed)` then `rng.choice(year.index, size=n_hours, replace=False)` (`replace=False` = no hour twice; `sorted(...)` puts them in time order).
2. **Scale the loads** to the hour, zone by zone. First the zone of every load, which is the zone of its bus (your Lab 1 loader put the `ZON_*` name there):

   ```python
   zone_of_load = pd.Series(net.bus.loc[net.load["bus"], "zone"].values, index=net.load.index)
   ```

   The `.values` matters: the lookup comes back labelled by *bus* numbers, and several loads share a bus, so pandas refuses to line it up (`ValueError: cannot reindex on an axis with duplicate labels`); taking the bare values and re-labelling them by load index sidesteps that. Then the base network's MW per zone, `base_p.groupby(zone_of_load).sum()` (with `base_p = net.load["p_mw"].copy()`, kept for the whole build), and for each hour a factor per zone, `factors = {z: hour_mw[z] / base_zone_mw[z] for z in ZONES}`, turned into a factor per load with `zone_of_load.map(factors)` — `.map` with a dictionary replaces every zone name by its factor. `net.load["p_mw"] = base_p * factor_per_load`, the same for `q_mvar` from its own copy — always from the base copies, never from the previous hour.
3. **Scale the generation too** — the trap of this lab. Loads on a June afternoon are 45 % of the base case; leave the generators at base and the slack bus must absorb the other 55 %, and the power flow stops converging — every hour comes out "insecure" and the dataset is worthless. Multiply every *non-slack* generator's `p_mw` by the total factor, this hour's total load ÷ base total load: `nonslack = ~net.gen["slack"]` (`~` is *not*, as in Lab 7's de-duplication), `net.gen.loc[nonslack, "p_mw"] = base_gp[nonslack] * total_factor`, with `base_gp` a copy like the others. (On the reference solution, without this step: 250 of 250 hours insecure; with it: about 70.)
4. **Label** with the screener's criterion, in a loop of your own — `screen_n1` always runs all 52 outages and returns a table, which is right for Lab 2 and wasteful here, so `security.py` gets a small helper `hour_is_insecure(net, outages)` in the screener's own shape (Lab 2's `try` / `except pp.LoadflowNotConverged` / `finally` restore): run the base case first, then each outage in turn, and `return True` the moment any case overloads a line or fails to converge — line loadings only, as in Lab 2, transformer ratings are placeholders — `return False` after the last one. `outages` is the list of line indices to try. The features are the hour's four zone loads and three temperatures — what an operator knows *before* any power flow — plus the boolean `insecure`. Restore the base loads and generation before returning.

**The speed-up, and what it costs.** With `outages = list(net.line.index[net.line.in_service])`, all 52, the build of 250 hours takes about **two minutes** on the reference laptop — most hours are secure and every outage must be checked; an insecure hour stops at its first violation. The documented shortcut: `outages` = the **12 severest outages of the base-case ranking**, `screen_n1(net)` once, sorted by `max_loading_percent` descending, the first twelve `outage_idx` values — and the build takes 23 seconds. What it can miss: an outage that is harmless at the base case but becomes the critical one under a different load pattern would leave the hour labelled secure. On a 60-hour check the reference shortcut agreed with the full screening on all 60 (21 insecure); say in the docstring which policy you chose and, if you took the shortcut, that number. Either policy is acceptable; an undocumented one is not. Build once and save; later cells reload the CSV rather than rebuild.

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

About one hour in four insecure, as the year was built to be (69 of 250 with the full policy, 71 with the shortcut). Commit the table: from the notebook in `notebooks/`, `ds.to_csv("../tests/data/security_dataset.csv")` — the `../` because the notebook sits one folder down; 18 kB, expensive to rebuild, and the test below reads it. Two tests in `tests/test_security.py` (replace the placeholder, keep its name, add one): the committed table holds both classes and its columns are exactly the seven features plus `insecure`; and a live build with `n_hours=3` and a fixed seed gives three rows twice, the same hours both times (about five seconds — the base screening dominates). Paths from `__file__` as always: the table at `Path(__file__).parent / "data" / "security_dataset.csv"`, the year at `Path(__file__).resolve().parents[1] / "data" / "svedala-year" / "svedala_hourly.parquet"` — inside the workbook, which is why you committed it. **Checkpoint:** `pytest tests/test_security.py -q` → `2 passed`; `pytest -q` → Lab 7's count plus two (`16 passed` on the reference solution — its last placeholder is gone now). Commit `security.py`, the tests and the table; push; CI green.

## 2. Train and compare (~30 min)

Split **temporally** — hours before 1 October train, October onward test (`ds.index < pd.Timestamp("2025-10-01", tz="UTC")`; the index is UTC, so the cut-off must be too). Three classifiers, the `fit`/`predict` contract from LC10: `LogisticRegression` inside `make_pipeline(StandardScaler(), ...)` (a linear model that outputs a probability — scale it, as LC12 taught), `DecisionTreeClassifier(max_depth=3)` (LC11's readable tree), `HistGradientBoostingClassifier` (LC11's winner). Score with `accuracy_score`, `precision_score` and `recall_score` from `sklearn.metrics`, the last two for the insecure class (`True` is the positive class by default).

The test set is looked at once, at the end (LC12). Everything you compare and choose on must come from the training hours — and a plain validation slice does not work here: the insecure hours are winter hours, so August–September holds none and there is nothing to choose on. The honest tool is `cross_val_predict(model, Xtr, ytr, cv=5)` from `sklearn.model_selection`: it splits the training hours into five parts and predicts each part with a model fitted on the other four, so every training hour gets a prediction from a model that never saw it — *out-of-sample* predictions without touching the test set. Score those. On the reference solution (180 training hours, 24 % insecure):

```
logistic  accuracy 0.93  precision(insecure) 0.80  recall(insecure) 0.98
tree      accuracy 0.94  precision(insecure) 0.83  recall(insecure) 0.98
gbdt      accuracy 0.94  precision(insecure) 0.82  recall(insecure) 0.95
```

Accuracy is the WRONG headline here: the classes are imbalanced, and a model that called every hour secure would score 76 % while missing every dangerous hour. Read precision and recall for the insecure class instead — recall 0.98 means the tree missed one insecure hour in fifty; precision 0.83 means one flag in six was a false alarm. Pin `random_state=0` on the tree and the boosting model, as LC11 did, so a rerun gives the same numbers.

## 3. The engineering question (~30 min)

A false negative (calling an insecure hour secure) risks the grid; a false positive wastes an engineer's check. `predict` uses a probability threshold of 0.5; `predict_proba` gives the probability itself — one row per hour, two columns (secure, insecure), so `[:, 1]` takes every row's second column — and `proba >= threshold` is your own decision rule. Get the out-of-sample probabilities the same way, `cross_val_predict(..., method="predict_proba")[:, 1]`, and sweep the threshold on them. Use logistic regression for the sweep: the boosted model's probabilities sit almost all at 0 or 1, so its sweep is flat, while the logistic model's spread out and show the trade-off. On the reference training hours:

```
threshold 0.7: precision 0.85  recall 0.93  flagged 0.27
threshold 0.5: precision 0.80  recall 0.98  flagged 0.30
threshold 0.3: precision 0.77  recall 1.00  flagged 0.32
threshold 0.1: precision 0.70  recall 1.00  flagged 0.35
```

Every step down catches more insecure hours and raises more false alarms — that is the trade. **Choose an operating threshold** on this table and defend it in one paragraph in the README: what miss rate do you accept, what does a miss cost, what does a false alarm cost? This paragraph is the deliverable — the models are interchangeable, the judgment is not. Then, and only then, the one look at the test set: fit the model on all training hours, apply your threshold to `predict_proba` on the 70 test hours, and report precision and recall there (the reference at 0.3: precision 0.83, recall 1.00). If the test number disagrees with the training table, say so — that sentence is worth more than a good number.

## 4. Pod check (15 min)

Three sentences as an Issue in the other pair's host repo (**Issues** tab → **New issue**), titled "Lab 8 pod check" — at least one about their threshold argument. Nothing handed in, nothing graded.

## Done when

Dataset committed with its labelling policy documented in the docstring, three models compared on precision and recall, threshold argued in the README, pod check exchanged — before the Quiz 4 sitting.

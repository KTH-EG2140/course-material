# Lab 9 — Forecast method comparison: the class tournament

*EG2140 · **self-paced** — do it with your lab partner during the week; your pod is first support (partner → pod → Discussions → the TA sessions) · ~90 min + Quiz 4 at its sitting · host repo: the partner whose name comes FIRST alphabetically in today's pair. No AI tools — this is the last lab of the AI-free period; savour it.*

Module 3 gave you learners, quantiles, trees, networks and — above all — the evaluation discipline. This lab pools the class: each pair implements **one** challenger method against its own Lab 7 SARIMA baseline, on the **same harness**, and posts the result to the shared table. At the start of Lecturecise 14 we read the table together: what did each step of sophistication buy, and what did it cost?

**Before you start.** The host repo needs Lab 7 (`walk_forward` and the baselines in `evaluation.py`) and the series and held-out week you used there — on the fallback series that is `ZON_MITT` and 16–22 February. Your pod is four people, two pairs; the two pairs claim different methods.

## 1. Choose your challenger (~10 min)

The claims thread ("Lab 9 — method claims") is opened by the teacher in the course-material **Discussions** before the Quiz 4 sitting. Reply with one line — your two names and the method — and **first claim wins**. Across the class all three taught families must be covered — linear regression on the LC10 features, gradient boosting with temperature, and the MLP — so before doubling up on a claimed family, take an uncovered one. Once the three are covered, further options: quantile GBM (report pinball + coverage), SARIMA with temperature as exogenous input, or a method of your own (clear it in the thread first).

## 2. Run the tournament (~60 min)

Your Lab 7 `walk_forward` harness, **unchanged**: same series, same test week, same horizon, same metrics. The work is in `notebooks/lab9_<method>.ipynb` in the host repo, committed — that file is what your table row links to, so it must run top to bottom from a fresh clone.

A learner needs the LC10 feature table, built on **your** series: the two lags, temperature and the clock columns, exactly as LC10 section 1.1, joined to the target and `dropna()`'d. Then a `model_fn` that fits on the training window it is handed and predicts the next day — the shape every challenger takes:

```python
def learner_fn(train, horizon):
    rows = table.loc[:train.index[-1]]                          # feature rows up to the last training hour
    model = make_pipeline(StandardScaler(), YourModel()).fit(rows.drop(columns="target"), rows["target"])
    future = table.loc[train.index[-1] + pd.Timedelta(hours=1):].iloc[:horizon]   # the next day's feature rows
    return model.predict(future.drop(columns="target"))
```

Two honesty points inside those four lines: the features of the day being forecast use only lags of 24 hours or more, so the "future" rows contain nothing the operator would not know the evening before (a `lag1` column would be leakage — LC12's gallery, item 3); and the scaler sits inside the pipeline, refitted per day on the training rows only (item 2). Run `walk_forward(y, learner_fn, test_start, test_end)` exactly as in Lab 7 — one line per day if you kept the progress print — and compute the same three numbers: MAE, the two baselines' MAEs on the same hours, skill against the better baseline. Your Lab 7 SARIMA number comes along as the reference row.

If your challenger loses to SARIMA — post it anyway; a table of only victories is marketing, not engineering.

## 3. Post to the pooled table (~10 min)

One row in the Discussions table, in the thread's format: method · MAE (MW) · skill vs the better baseline · one sentence of interpretation · a link to your notebook on GitHub (open the file in your host repo on GitHub and copy the address bar). Rows without a reproducible link do not count.

## 4. Pod check (10 min)

Three sentences as an Issue in the other pair's host repo (**Issues** tab → **New issue**), titled "Lab 9 pod check" — is their comparison actually like-for-like: same series, same week, same horizon, baselines on the same hours? Nothing handed in, nothing graded.

## Done when

Your row is in the table with a working link, pod check exchanged. The table is discussed at Lecturecise 14 — arrive having read all of it.

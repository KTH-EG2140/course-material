# Lab 9 — Forecast method comparison: the class tournament

*EG2140 · **self-paced** — do it with your lab partner during the week; your pod is first support (partner → pod → Discussions → the TA sessions) · ~90 min + Quiz 4 at its sitting · host repo: the repo that holds your Lab 7 harness — if today's pair is a new one and neither of you hosted Lab 7, copy `src/svedala_toolbox/evaluation.py` and `tests/test_evaluation.py` from the Lab 7 host into today's host first; they are toolbox code and travel unchanged. No AI tools — this is the last lab of the AI-free period; savour it.*

Module 3 gave you learners, quantiles, trees, networks and — above all — the evaluation discipline. This lab pools the class: each pair implements **one** challenger method against its own Lab 7 SARIMA baseline, on the **same harness**, and posts the result to the shared table. At the start of Lecturecise 14 we read the table together: what did each step of sophistication buy, and what did it cost?

**Before you start.** The host repo needs Lab 7's `walk_forward` and baselines in `evaluation.py` (see the header) and the series and held-out week you used there — on the fallback series that is `ZON_MITT` and 16–22 February. On your own Lab 6 series there is no temperature column: take it from the course parquet's `temp_mid` (or the `temp_*` column nearest your zone) on the same timestamps — the SSH week carries loads only. Your pod is four people, two pairs; the two pairs claim different methods.

## 1. Choose your challenger (~10 min)

The claims thread ("Lab 9 — method claims") is opened by the teacher in the course-material **Discussions** before the Quiz 4 sitting. Reply with one line — your two names and the method — and **first claim wins**. Across the class all three taught families must be covered — linear regression on the LC10 features, gradient boosting with temperature, and the MLP — so before doubling up on a claimed family, take an uncovered one. Once the three are covered, further options: quantile GBM (report pinball + coverage), SARIMA with temperature as exogenous input, or a method of your own (clear it in the thread first).

## 2. Run the tournament (~60 min)

Your Lab 7 `walk_forward` harness, **unchanged**: same series, same test week, same horizon, same metrics. The work is in `notebooks/lab9_<method>.ipynb` in the host repo — `lab9_linear.ipynb`, `lab9_gbdt.ipynb`, `lab9_mlp.ipynb` — committed: that file is what your table row links to. *Reproducible* means the other pair can run it top to bottom from a fresh clone of your host repo plus their own course-material clone; so the first cell sets `CM = "<cm>"` (Labs 6–8's convention) and everything else reads through it, and the row states the series and the week.

A learner needs the LC10 feature table, built on **your** series: the two lags, temperature and the four clock columns (`hour_sin`, `hour_cos`, `dow`, `workday`), exactly as LC10 section 1.1, joined to the target and `dropna()`'d — LC10 calls that table `data`; call it `table` here. Then a `model_fn` that fits on the training window it is handed and predicts the next day — the shape every challenger takes, with the imports it needs (`StandardScaler` and `make_pipeline` are LC12's; the model is your claim's):

```python
from sklearn.linear_model import LinearRegression          # or your claimed model
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

def learner_fn(train, horizon):
    rows = table.loc[:train.index[-1]]                          # feature rows up to the last training hour
    model = make_pipeline(StandardScaler(), YourModel()).fit(rows.drop(columns="target"), rows["target"])
    future = table.loc[train.index[-1] + pd.Timedelta(hours=1):].iloc[:horizon]   # the next day's feature rows
    return model.predict(future.drop(columns="target"))
```

Three honesty points inside those four lines: the features of the day being forecast use only lags of 24 hours or more, so the "future" rows contain nothing the operator would not know the evening before (a `lag1` column would be leakage — LC12's gallery, item 3); those rows still carry the day's real `target` column, and `.drop(columns="target")` is what keeps the answer out of `predict`; and the scaler sits inside the pipeline, refitted per day on the training rows only (item 2). Run `walk_forward(y, learner_fn, test_start, test_end)` exactly as in Lab 7 — a learner fits in milliseconds, so the seven days go by in a blink; the progress print is for the slow methods — and compute the same three numbers: MAE, the two persistence baselines' MAEs on the same hours (`persistence(y).loc[out.index]`, as Lab 7 section 3), and skill against the *better of the two baselines*, Lab 7's definition. SARIMA is not a baseline: it is the reference row your challenger is compared with, and every row on the table uses the same skill definition so the table stays like-for-like. Your Lab 7 SARIMA number comes along as that reference row.

If your challenger loses to SARIMA — post it anyway; a table of only victories is marketing, not engineering.

## 3. Post to the pooled table (~10 min)

One row in the Discussions table, in the thread's format: method · series and week · MAE (MW) · skill vs the better persistence baseline · your SARIMA reference MAE · one sentence of interpretation · a link to your notebook on GitHub (open the file in your host repo on GitHub and copy the address bar). Rows without a reproducible link do not count.

## 4. Pod check (10 min)

Three sentences as an Issue in the other pair's host repo (**Issues** tab → **New issue**), titled "Lab 9 pod check" — is their comparison actually like-for-like: same series, same week, same horizon, baselines on the same hours? Nothing handed in, nothing graded.

## Done when

Your row is in the table with a working link, pod check exchanged. The table is discussed at Lecturecise 14 — arrive having read all of it.

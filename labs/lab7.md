# Lab 7 — A SARIMA baseline for Svedala

*EG2140 · **self-paced** — do it with your lab partner during the week; your pod is first support (partner → pod → Discussions → the TA sessions) · ~110 min · host repo: the partner whose name comes FIRST alphabetically in today's pair. Quiz 3 at its sitting covers Lecturecises 8–9. No AI tools.*

Lecturecise 9 built the baseline on the course series; this lab makes it **yours**: same working method, your own Lab 6 series (fall back to the course parquet if your Lab 6 series has gaps — say so in the README). This baseline is the bar that every learner in Module 3 must clear, so treat the evaluation as the deliverable.

**Before you start.** Walk the LC9 notebook first — section 3.1 is the loop you turn into a function here, and its closing section names the three functions. The stubs are in `src/svedala_toolbox/evaluation.py`; `statsmodels` is already in your venv.

## 1. Persistence first (~20 min)

Implement `persistence(y, horizon=24)` and `seasonal_persistence(y, horizon=24, season=168)`. Each is one line: `y.shift(n)` moves every value `n` hours later, so the value at hour *t* is what the series showed at *t − n* — `y.shift(horizon)` is "tomorrow = today", `y.shift(season)` is "this Tuesday = last Tuesday". The seasonal one does not use `horizon` at all; it keeps the parameter so that every baseline has the same signature and the harness can call them alike — leave it unused and say so in a comment. The first `horizon` hours of the result are `NaN`, because there is nothing to shift in; that is correct, not a bug.

One honesty note the stub also carries: the weekly baseline is *often* the harder one to beat, not always — on the course series' test week it loses to plain persistence (283 MW against 203 MW), because the weather moved more from one week to the next than the weekly shape is worth. Which of the two wins on **your** week is a finding you report, not something you assume.

Then `walk_forward(y, model_fn, test_start, test_end, horizon=24)`. Its contract: for each day from `test_start` to `test_end`, the training data is everything **strictly before** that day, `model_fn(train, horizon)` returns the next `horizon` values, and the day's actual values are then revealed for the next iteration. It returns one DataFrame with the columns `actual` and `forecast`, one row per test hour. The shape, in plain steps:

- `pd.date_range(test_start, test_end, freq=f"{horizon}h")` steps through the test days.
- `train = y.loc[:day - pd.Timedelta(hours=1)]` is everything up to the hour before the day — the *strictly before* is the whole point.
- `actual = y.loc[day : day + pd.Timedelta(hours=horizon - 1)]` is the day itself.
- `pd.Series(list(model_fn(train, horizon))[:len(actual)], index=actual.index)` puts the forecast on the same hours, so the two columns line up; `pd.DataFrame({"actual": actual, "forecast": forecast})` is one day's block, and `pd.concat(blocks)` stacks the days.
- `model_fn` is a *function passed as an argument* — the harness never knows which model it is judging; that is what makes it reusable in Lab 9.
- The course series and your Lab 6 series carry a time zone on their index (`y.index.tz` prints `UTC`) — a *tz-aware* index. A plain date string has none, and pandas refuses to compare the two inside one slice (`ValueError: Both dates must have the same UTC offset`). So the first thing `walk_forward` does is convert its two dates: `test_start = pd.Timestamp(test_start, tz=y.index.tz)`, same for `test_end` — inside the function, so callers and tests can pass plain strings.

**Test the harness on a toy series where you know the answer**, before any model touches it — replace the two placeholders in `tests/test_evaluation.py`, keep their names. The file needs these at the top (the stub only imports `pytest`), and one helper that builds the toy series — its value *is* the hour number, so `persistence(y, 2).iloc[5] == y.iloc[3]` is a fact you can assert:

```python
import pandas as pd

from svedala_toolbox.evaluation import persistence, seasonal_persistence, walk_forward


def toy(n=24 * 10):
    idx = pd.date_range("2025-03-01", periods=n, freq="h", tz="UTC")
    return pd.Series(range(n), index=idx, dtype=float)      # 0, 1, 2, ... one per hour
```

For the harness, the test that matters records what the model was shown:

```python
def test_walk_forward_never_sees_future():
    y = toy()
    seen = []
    def model_fn(train, horizon):
        seen.append(train.index[-1])          # the last hour the model was shown
        return [train.iloc[-1]] * horizon     # forecast: repeat the last value
    out = walk_forward(y, model_fn, "2025-03-08", "2025-03-10", horizon=24)
    assert list(out.columns) == ["actual", "forecast"] and len(out) == 72
    for last_seen, day in zip(seen, pd.date_range("2025-03-08", "2025-03-10", tz="UTC")):
        assert last_seen < day, "the model saw data from the day it was asked to forecast"
```

A function defined inside a test (`model_fn`) can append to a list defined next to it — that is how the test *sees* what the harness fed the model. Then make it earn its place: change the training slice in `walk_forward` to include the day (`day + pd.Timedelta(hours=23)`), run `pytest tests/test_evaluation.py -q`, and read the red run on the reference solution:

```
E           AssertionError: the model saw data from the day it was asked to forecast
E           assert Timestamp('2025-03-08 23:00:00+0000', tz='UTC') < Timestamp('2025-03-08 00:00:00+0000', tz='UTC')
1 failed, 1 passed
```

Put the slice back: `2 passed`. That red run is the only proof the harness cannot cheat. Commit `evaluation.py` and the tests.

## 2. Fit and choose (~40 min)

Explore ACF/PACF on your series in a notebook — `notebooks/lab7_explore.ipynb` in the host repo, committed, because exploration is notebook work and the *harness* is toolbox work. Your series is your Lab 6 week if it has no gaps, otherwise the course parquet's `ZON_MITT`, prepared as LC9 section 0.2 does (`interpolate(limit=3).dropna().asfreq("h")`). Pick **one held-out week** now and write it down — on the course series use 16–22 February, so your numbers can be checked against the reference; on your own series, the last full week you have. LC9 section 1.1 shows how to read the ACF; `plot_pacf` sits next to `plot_acf` in the same module and shows the *partial* autocorrelation — the correlation at lag *k* with the shorter lags' influence removed. The usual reading: the lag where the PACF bars drop to nothing suggests *p*, the lag where the ACF bars drop suggests *q*; on load data both readings are rough, which is why the harness has the last word.

Fit at least two SARIMA candidates — LC9's `(1,0,1)(1,1,1,24)` is a fair first one; change one order at a time — and compare them with the harness, not with the summary table: the AIC in `fit.summary()` says how well a model fits the *training* data, the harness says how it forecasts. Pick one **with a reasoned sentence per rejected candidate** in the README.

Wrap a candidate as a `model_fn` for the harness — a function that fits on the training window it is handed and returns the forecast:

```python
def sarima_fn(train, horizon):
    train = train.loc["2025-01-06":]             # six weeks is enough; refitting on a year is slow
    fit = SARIMAX(train, order=(1, 0, 1), seasonal_order=(1, 1, 1, 24),
                  enforce_stationarity=False, enforce_invertibility=False).fit(disp=False)
    return fit.forecast(horizon).values
```

The harness **refits** the model every day on the growing window — that is honest and slow: about two seconds per fit, so about 15 seconds for a test week on the reference laptop, during which the cell shows nothing. Put `print(train.index[-1])` as the first line of your `model_fn` and you see one line per day go by. If a day takes longer than a minute, the fit is struggling with that order: interrupt the kernel (the stop button) and try a smaller order — a candidate that needs twenty minutes has already told you something. Two slices inside `model_fn` are the safe form: `train.loc["2025-01-06":]` on its own, never a string and a tz-aware timestamp in the same `.loc[a:b]` (the `ValueError` from section 1). LC9's `state.append` reveals days without refitting, a fast approximation: on the course week the two agree to within a megawatt (155 refit against 156), on other series they can differ more. Yours is the refit number.

## 3. The number (~30 min)

Run your chosen model, `persistence` and `seasonal_persistence` through `walk_forward` on a held-out week. The two baselines fit the harness as `model_fn`s too — persistence is "repeat the last 24 hours": `lambda train, h: train.iloc[-24:].values` (a `lambda` is a one-line unnamed function, handy exactly here); seasonal persistence is `train.iloc[-168:-144].values` — the 24 hours that started one week before the day being forecast, counted from the end of the training window. Report all three MAEs — `(out.forecast - out.actual).abs().mean()` on each result — and the skill percentage **against the better baseline**, `100 * (1 - mae_model / min(mae_persistence, mae_seasonal))`: beating plain persistence while losing to last-Tuesday is not a win.

On the reference solution, course series, test week 16–22 February, refit harness:

```
SARIMA 155 MW | persistence 203 MW | seasonal persistence 283 MW | skill vs better baseline +24%
```

On the course series with that week you should reproduce these numbers; on your own Lab 6 series they differ, and the shape of the sentence does not. If SARIMA loses to a baseline, that is a *finding*, not a failure — explain it.

**Checkpoint:** `pytest -q` → Lab 6's count plus two (`14 passed, 1 skipped` on the reference solution). Commit, push, CI green.

## 4. Pod check (15 min)

Three sentences as an Issue in the other pair's host repo (**Issues** tab → **New issue**), titled "Lab 7 pod check" — at least one about their evaluation setup (which week, which baseline, does the harness refit), not their model. Nothing handed in, nothing graded.

## Done when

`walk_forward` tested (the red run seen), one skill number with an honest sentence around it in the README, pod check exchanged — before the Quiz 4 sitting. Lab 9 will reuse your harness unchanged: every challenger method fights on this exact battlefield.

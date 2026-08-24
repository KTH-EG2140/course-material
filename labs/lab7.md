# Lab 7 — A SARIMA baseline for Svedala

*EG2140 · **self-paced** — with your lab partner during the week; pod as first support · ~110 min. Quiz 3 at its sitting covers Lecturecises 8–9. No AI tools.*

Lecturecise 9 built the baseline on the course series; this lab makes it **yours**: same working method, your own Lab 6 series (fall back to the course parquet if your Lab 6 series has gaps — say so in the README). This baseline is the bar that every learner in Module 3 must clear, so treat the evaluation as the deliverable.

## 1. Persistence first (~20 min)
Implement `persistence(y, horizon=24)`, `seasonal_persistence(y, horizon=24, season=168)` and `walk_forward(y, model_fn, test_start, test_end, horizon=24)` in `evaluation.py` (stubs provided). The seasonal one is the lecture's harder-to-beat baseline — last Tuesday predicts this Tuesday. Walk-forward means: forecast a day, reveal it, continue — never refit on the future. Test the harness on a toy series where you know the answer.

## 2. Fit and choose (~40 min)
Explore ACF/PACF on your series in a notebook (exploration is notebook work — the *harness* is toolbox work). Fit at least two SARIMA candidates; pick one **with a reasoned sentence per rejected candidate** in the README.

## 3. The number (~30 min)
Run your chosen model, `persistence` and `seasonal_persistence` through `walk_forward` on a held-out week. Report all three MAEs and the skill percentage **against the better baseline** — beating plain persistence while losing to last-Tuesday is not a win. If SARIMA loses to a baseline, that is a *finding*, not a failure — explain it.

## 4. Pod check (15 min)
Three sentences in the other pair's repo ("Lab 7 pod check") — at least one about their evaluation setup, not their model. Nothing handed in, nothing graded.

## Done when
`walk_forward` tested, one skill number with an honest sentence around it in the README, pod check exchanged — before the Quiz 4 sitting. Lab 9 will reuse your harness unchanged: every challenger method fights on this exact battlefield.

# Lab 9 — Forecast method comparison: the class tournament

*EG2140 · **self-paced** — with your lab partner during the week; pod as first support · ~90 min + Quiz 4 at its sitting. No AI tools — this is the last lab of the AI-free period; savour it.*

Module 3 gave you learners, quantiles, trees, networks and — above all — the evaluation discipline. This lab pools the class: each pair implements **one** challenger method against its own Lab 7 SARIMA baseline, on the **same harness**, and posts the result to the shared table. At the start of Lecturecise 14 we read the table together: what did each step of sophistication buy, and what did it cost?

## 1. Choose your challenger (~10 min)
The claims thread ("Lab 9 — method claims") is opened by the teacher in Discussions before the Quiz 4 sitting. One method per pair, **first claim wins**. Across the class all three taught families must be covered — linear regression on the LC10 features, gradient boosting with temperature, and the MLP — so before doubling up on a claimed family, take an uncovered one. Once the three are covered, further options: quantile GBM (report pinball + coverage), SARIMA with temperature as exogenous input, or a method of your own (clear it in the thread).

## 2. Run the tournament (~60 min)
Your Lab 7 `walk_forward` harness, **unchanged**: same test week, same horizon, same metrics. Persistence and your SARIMA numbers come along as the reference row. If your challenger loses to SARIMA — post it anyway; a table of only victories is marketing, not engineering.

## 3. Post to the pooled table (~10 min)
One row in the Discussions table: method, MAE, skill vs persistence, one sentence of interpretation, link to the notebook/code in your repo. Rows without a reproducible link do not count.

## 4. Pod check (10 min)
Three sentences on the other pair's row ("Lab 9 pod check") — is the comparison actually like-for-like? Nothing handed in, nothing graded.

## Done when
Your row is in the table with a working link, pod check exchanged. The table is discussed at Lecturecise 14 — arrive having read all of it.

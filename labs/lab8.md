# Lab 8 — Classify N-1 security: milliseconds instead of minutes

*EG2140 · **self-paced** — with your lab partner during the week; pod as first support · ~110 min. Quiz 4 at its sitting covers Lecturecises 11–13. No AI tools.*

Your screener answers "is this operating point N-1 secure?" in minutes of power flows. An operator screening thousands of scenarios wants the answer in milliseconds. This lab trains classifiers to approximate your screener — and, more importantly, teaches you to decide **when to trust which**.

## 1. Build the labelled dataset (~35 min)
Implement `build_security_dataset(net_loader, year_parquet, n_hours=250)` in `security.py` (stub provided): sample hours from the year, scale the network to each hour (each zone's loads by that hour's zone factor), label with **your own screener**. Full 52-outage labelling is slow; **decide** a speed-up (the 12 severest outages? DC screening first, AC on the borderline?) and document what the shortcut can miss. Features: the zone loads and temperatures of the hour — the classifier must work from what an operator knows *before* running power flows. Commit the labelled table (it is expensive to rebuild).

## 2. Train and compare (~30 min)
Logistic regression, a decision tree, gradient boosting — temporal split, as always. Accuracy is the WRONG headline here: the classes are imbalanced (~1 insecure hour in 4) and the errors are not symmetric.

## 3. The engineering question (~30 min)
A false negative (calling an insecure hour secure) risks the grid; a false positive wastes an engineer's check. Report precision AND recall for the insecure class, then **choose an operating threshold** and defend it in one paragraph: what miss rate do you accept, and what does it cost? This paragraph is the deliverable — the models are interchangeable, the judgment is not.

## 4. Pod check (15 min)
Three sentences in the other pair's repo ("Lab 8 pod check") — at least one about their threshold argument. Nothing handed in, nothing graded.

## Done when
Dataset committed with its labelling-shortcut documented, three models compared on the right metrics, threshold argued, pod check exchanged — before the Quiz 4 sitting.

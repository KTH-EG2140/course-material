# Lab 2 — Refactor the N-1 screener + pod check

*EG2140 · **self-paced** — do it with your lab partner during the week; your pod is first support (partner → pod → Discussions → open hours) · ~110 min · host repo: the partner whose name comes FIRST alphabetically (Lab 3 swaps). No AI tools.*

Someone left the course a gift: `awful_screener.py` — an N-1 screener that **works**. It produces correct numbers. It is also unreadable, untestable, and one keystroke from disaster. Yesterday you refactored a 20-line version of this problem together; today's is 70 lines, and it is for keeps: the result becomes `svedala_toolbox/screener.py`, a permanent part of your package.

## 0. Meet the patient (15 min)

Get the file and the reference results from the course material (`lab2/` folder), drop both in your repo root, and run it:

```bash
python awful_screener.py
```

While it grinds through 52 contingencies, read it with your partner and **write down every distinct sin you find** — aim for ten. (You will trade lists with the other pair in your pod later.) Then look at what it printed: 15 DANGER lines, worst case AL7 at 205%. Those numbers are *correct* — verify a few against `n1_reference_results.csv`. That file is your **oracle**: the refactor must keep producing these numbers, and the oracle is how you prove it.

## 1. Refactor into the toolbox (50 min)

Create `src/svedala_toolbox/screener.py`. Requirements:

- One public function: `screen_n1(net, loading_limit=100.0) -> pd.DataFrame` with columns `outage_idx, outage_line, status, max_loading_percent, n_violations`
- **Reuse your loader** — the awful script duplicates all of Lab 1 inline; that duplication dies today
- Every outage **restored** whatever happens (`try/finally` — the awful script restores only on success; find that bug, it is real)
- Non-convergence handled **explicitly**: `status="not_converged"`, never a silent `except: pass`
- Named constants, docstrings, no prints inside the function, no hard-coded paths — everything LC3 taught

Work in small commits with honest messages — this history gets reviewed.

## 2. Prove it against the oracle (25 min)

Copy `n1_reference_results.csv` into `tests/data/` and write `tests/test_screener.py`:

- one row per in-service line (52)
- the network is fully restored after screening (`net.line.in_service.all()`)
- **the oracle test**: your results match the reference — loadings within `1e-3`, violation counts exactly

When the oracle test passes, you have proven the one thing refactoring must prove: *behaviour preserved.* Commit, push, watch CI go green.

## 3. Pod check (20 min)

Swap with the other pair in your pod (org access — open their repo on GitHub). Review `screener.py` and its history against the checklist (`labs/review_checklist.md`), then write **three sentences** in their repo (open an Issue titled "Lab 2 pod check"): one thing done well, one concrete improvement, one question. Sign it. Nothing is handed in and nothing is graded — the review lives where reviews belong, in the repository. Being reviewed is the product here — this exact format returns in the opposition rounds, with higher stakes.

## Done when

Oracle test green in CI, pod check written, pod check received — before Quiz 1, which reads this lab's material. Extension: add severity ranking — a `rank_contingencies(results)` that orders by how much trouble each outage causes, tested. (It earns its keep in Module 3, where these rankings become ML training labels.)

# Lab 2 — Refactor the N-1 screener + pod check

*EG2140 · **self-paced** — do it with your lab partner during the week; your pod is first support (partner → pod → Discussions → the TA sessions) · ~110 min · host repo: the partner whose name comes FIRST alphabetically (Lab 3 swaps) — both of you can push to it, every student has push on every workbook repo. No AI tools.*

Someone left the course a gift: `awful_screener.py` — an N-1 screener that **works**. It produces correct numbers. It is also unreadable, untestable, and one keystroke from disaster. In LC3 you refactored a 20-line version of this problem together; today's is 70 lines, and it is for keeps: the result becomes `svedala_toolbox/screener.py`, a permanent part of your package.

## 0. Meet the patient (15 min)

Download [awful_screener.py](awful_screener.py) and [n1_reference_results.csv](n1_reference_results.csv) (both in the course material's `labs/` folder; on GitHub, open the file and use the **Download raw file** button) and drop both in your repo root. They are scratch, like LC3's companions: the oracle moves into `tests/data/` in section 2 and the script is deleted at the end of section 2. If a commit in between sweeps them in anyway, `git rm awful_screener.py` removes the script later and the history simply shows the cleanup.

One check before anything is committed today: run `git status`. If it lists only the two files you just downloaded, your repository already has a `.gitignore` — skip the rest of this paragraph. If it also lists `.venv/` or `__pycache__` folders as untracked, it has none (repositories created from the template early in the course lack it): create a file named `.gitignore` in the repo root, the same kind of file LC2 had you make with `echo ".venv/" > .gitignore` in the scratch folder, with these four lines:

```
.venv/
__pycache__/
*.egg-info/
.pytest_cache/
```

Those are all rebuildable files; the venv alone is hundreds of megabytes and contains single files above GitHub's size limit, so a `git add -A` that catches it makes the push fail. If `git status` shows any of these as *already tracked* (they went in with an earlier `git add -A`), untrack them once with `git rm -r --cached .venv` (same for the others), then commit the `.gitignore` together with the removal.

Activate your environment and run the script. Inside an activated venv, `python` *is* the venv's interpreter — that is what activation does — so the bare name is safe here, exactly as in Lab 1's self-check:

```bash
source .venv/bin/activate            # Windows: .venv\Scripts\activate
python awful_screener.py
```

It takes a few seconds. This is what it printed on the reference solution (trimmed to the parts you read):

```
natet klart 52
ok RL1 94.79363739733799
ok CL5 94.92201019476443
...
DANGER!! RL3 154.02508888507356 3
...
ok CL3 95.19986890885596
klart, worst:
AL7 205.31210376932404
```

How to read it:

- One line per contingency, 52 in all: `ok <line> <worst loading %>` when nothing overloads, `DANGER!! <line> <worst loading %> <number of overloaded lines>` when something does. Count the DANGER lines: 15.
- The last two lines are the summary: the worst outage pushes some line to 205%. Two outages actually tie at that value, AL7 and AL8 — the script names AL7 only because its `>` comparison keeps the first one it saw. Ties like this return in the extension.
- Every one of the 52 cases converged. Remember that — it matters in section 2.

While you have it open, read the script with your partner and **write down every distinct sin you find** — aim for ten. (You will trade lists with the other pair in your pod later.) Then open `n1_reference_results.csv`. The first rows:

```
outage_idx,outage_line,status,max_loading_percent,n_violations
0,RL1,converged,94.7936373973382,0
1,CL5,converged,94.92201019476458,0
3,CL17,converged,97.61512869484363,0
5,RL7,converged,96.11200881681263,0
```

One row per outaged line: its index in `net.line`, its name, whether the power flow converged, the worst loading anywhere in the network with that line out, and how many lines were above 100%. The `outage_idx` column jumps (0, 1, 3, 5, …) because the line table's own index has gaps — nothing is missing, the file has 52 rows. Verify a few numbers against what the script printed: they agree to about twelve decimals and then drift (`94.79363739733799` versus `94.7936373973382`) — floating-point noise from two different machines, and section 2 shows how a test copes with it. This file is your **oracle**: the refactor must keep producing these numbers, and the oracle is how you prove it.

## 1. Refactor into the toolbox (50 min)

Create `src/svedala_toolbox/screener.py`, next to `loader.py`. Requirements:

- One public function: `screen_n1(net, loading_limit=100.0) -> pd.DataFrame` with columns `outage_idx, outage_line, status, max_loading_percent, n_violations`
- **Reuse your loader** — the awful script duplicates all of Lab 1 inline; that duplication dies today: the screener receives a network built by `load_svedala()` and contains no loading code of its own
- Every outage **restored** whatever happens (`try/finally` — the awful script restores only on success; find that bug, it is real)
- Non-convergence handled **explicitly**: `status="not_converged"`, never a silent `except: pass`
- A named constant for the limit (`LOADING_LIMIT_PERCENT = 100.0`, used as the parameter's default), docstrings, no prints inside the function, no hard-coded paths — everything LC3 taught

Three things about the shape before you start.

**Where the loader goes.** "Reuse" here means *do not port*: `screen_n1` takes a network as its parameter, and whoever calls it — your tests, later the CLI — builds that network with `load_svedala()` from Lab 1 first. So the 30 lines of loading code at the top of the awful script do not move into `screener.py` at all: the function starts where the loop starts, and `screener.py` may not need to import the loader at all.

**The loop.** For each line that is in service: switch it off, solve, read the results, switch it back on. "Each line that is in service" is `for idx in net.line.index[net.line.in_service]:` — the `in_service` column is True/False per line, and putting it inside the square brackets keeps only the index labels where it is True; that replaces the awful script's `if ... == True`. Solving is either `pp.runpp(net)` directly or your own `run_power_flow(net)` from Lab 1 — both are fine; the difference is what they raise when the power flow fails (`pp.LoadflowNotConverged` from pandapower, your `RuntimeError` from the wrapper), and you catch the one your call raises. Same trap as Lab 1: `pp.runpp` works in place and returns nothing — the results are read from `net.res_line` afterwards.

**`try / except / finally`.** You have met `try/except` in LC3; `finally` is new. Its block runs *whichever way the try ended* — after the last line of `try` when nothing went wrong, and after the `except` block when something did:

```python
net.line.at[idx, "in_service"] = False       # take the line out
try:
    ...                                       # solve, then read the results from net.res_line
except pp.LoadflowNotConverged:
    ...                                       # record this case as not converged
finally:
    net.line.at[idx, "in_service"] = True    # runs in BOTH cases: the line always comes back
rows.append({...})                            # after the whole try statement: runs once per outage
```

Execution continues below the `finally` block either way, so set `status`, the loading and the count inside `try` and `except`, and append the row once, after — no duplicated append. Now look at the awful script: its restore line sits *inside* `try`, after `pp.runpp`. When `runpp` raises, Python jumps straight to `except` and the restore never runs — the line stays out of service for every contingency that follows, each one now a double outage. That is the bug. It is not visible today, because all 52 base-case contingencies converge; section 2 makes it visible.

What each row carries:

- `status` is `"converged"` or `"not_converged"`.
- `max_loading_percent` is `float(net.res_line.loading_percent.max())`; `n_violations` is `int((net.res_line.loading_percent > loading_limit).sum())` — the comparison gives one True/False per line, the sum counts the Trues. Strictly greater than the limit, as the oracle does. The `float(...)` and `int(...)` turn numpy's own number types into plain Python ones, so the column holds the same kind of value as the `-1` below.
- A not-converged case has no results: give it `float("nan")` for the loading and `-1` for the count — a count that cannot be a real count, so nobody reads it as "zero violations".

Collect one dictionary per outage in a list and hand the list to `pd.DataFrame(rows)` at the end — it becomes one row per dictionary, columns named by the keys.

*Optional upgrade from LC3: the lecture offered `class PowerFlowError(RuntimeError)` as the step up from Lab 1's plain `RuntimeError`. If you take it, define it in `loader.py` and raise it from `run_power_flow` — everything that catches `RuntimeError` still works, because a `PowerFlowError` **is** one.*

Work in small commits with honest messages — this history gets reviewed. Two commits is a natural rhythm here: one when the loop runs and returns a table, one when the not-converged handling and the `finally` are in. The message describes what the commit actually contains, nothing more — if you wrote the whole function in one go, one commit saying so is the honest history. Name the file rather than using `-A`, so the scratch files stay out:

```bash
git add src/svedala_toolbox/screener.py
git commit -m "Add N-1 screener: try/finally restore, explicit not_converged rows"
```

## 2. Prove it against the oracle (25 min)

Move the oracle to where tests keep their data:

```bash
mkdir tests/data                              # Windows: mkdir tests\data
mv n1_reference_results.csv tests/data/       # Windows: move n1_reference_results.csv tests\data\
```

Write `tests/test_screener.py` with three tests:

- one row per in-service line (52)
- the network is fully restored after screening (`net.line.in_service.all()`)
- **the oracle test**: your results match the reference — loadings within `1e-3`, violation counts exactly

Plain test functions, like the two in `tests/test_loader.py`; each one loads its own network with `load_svedala()` (a couple of seconds each — sharing one network between tests is what LC5 is for). Two pieces you have not written before:

```python
from pathlib import Path

import pandas as pd

from svedala_toolbox.loader import load_svedala
from svedala_toolbox.screener import screen_n1

# __file__ is this test file's own path, so the oracle is found no matter
# which folder pytest is started from. loader.py uses the same idea for DATA_DIR.
ORACLE = Path(__file__).parent / "data" / "n1_reference_results.csv"
```

and, inside the oracle test, lining the two tables up:

```python
    results = screen_n1(load_svedala()).set_index("outage_line")
    reference = pd.read_csv(ORACLE).set_index("outage_line")
    # Same index on both sides, so pandas matches rows by line name when you
    # subtract one column from the other.
    loading_gap = (results.max_loading_percent - reference.max_loading_percent).abs()
```

Then the asserts are yours: every status converged, `loading_gap.max()` below `1e-3`, `n_violations` equal on every row. Comparing two columns gives one True/False per row, so "on every row" is `.all()`: `assert (results.n_violations == reference.n_violations).all()`. Trap: leave the `.all()` out and `assert results.n_violations == reference.n_violations` dies with `The truth value of a Series is ambiguous` — pandas refusing to guess whether you meant *all* rows or *any*. Why a tolerance at all: a power flow's last decimals differ between machines and library versions — the reference solution's deviation is about `1e-12`, so `1e-3` is generous on purpose, and the counts are integers, so those must match exactly.

**Checkpoint:** `pytest tests/ -q`. On the reference solution:

```
ssss...ss...s.                                                           [100%]
7 passed, 7 skipped in 3.29s
```

Before this lab it said `4 passed, 7 skipped` — the three provided tests plus the one you wrote in Lab 1. Three more dots, three more passed. Failing? Read the `E` lines as in Lab 1 — the assertion messages you wrote are what makes them readable.

When the oracle test passes, you have proven the one thing refactoring must prove: *behaviour preserved.*

Now the uncomfortable part. **These three tests pass a screener with the awful script's restore bug.** Every base-case contingency converges, so the `except` branch — and the skipped restore — never run; a test that has never seen its bug proves nothing (Lab 1's rule). Test the case where it bites — the stressed network from Lab 1's extension. Add a fourth test:

```python
def test_restores_lines_even_when_power_flow_fails():
    net = load_svedala()
    net.load["scaling"] = 1.05          # same knob as `svedala pf --scaling 1.05`
    results = screen_n1(net)
    assert (results.status == "not_converged").any(), "expected some non-converging cases"
    assert net.line.in_service.all(), "a failed power flow left its outage behind"
```

`net.load["scaling"]` is pandapower's per-load multiplier, the column your Lab 1 CLI sets for `--scaling`. On the reference solution at 1.05, 21 of the 52 contingencies do not converge and all 52 lines are back in service afterwards. With the restore bug, 42 do not converge and only 10 lines are left in service: every failed case leaves its line out, making the next case worse. Do not assert the 21 — assert that *some* case failed and that the network is whole; the exact count is the solver's business.

**Checkpoint:** `pytest tests/ -q` → `ssss...ss....s.` and `8 passed, 7 skipped`.

Now make the new test earn its place — Lab 1's rule again, a test you have never seen fail proves nothing. Move the restore line in `screener.py` from `finally:` to the end of the `try:` block, right after the line that reads the results (the awful script's version), and run `pytest tests/ -q` once more. On the reference solution the first three screener tests still pass and the fourth fails:

```
E       AssertionError: a failed power flow left its outage behind
...
1 failed, 7 passed, 7 skipped in 4.86s
```

The first `E` line is the whole story; the `E +  where ...` lines under it are pytest dumping the tables it compared, and you skip them. Put the line back under `finally:`, run again, green. That red run is the only proof the bug is really caught. Then commit, push, watch CI go green:

```bash
git add src/svedala_toolbox/screener.py tests/test_screener.py tests/data/n1_reference_results.csv
git commit -m "Screener tests: row count, restoration, oracle match, stressed-case restoration"
git push
```

The awful script leaves now. `git status` tells you which case you are in: listed as untracked → plain delete (`rm awful_screener.py`, Windows `del awful_screener.py`); already committed → `git rm awful_screener.py` and commit the removal. If `git status` also lists `__pycache__` folders, your `.gitignore` from section 0 is missing a line — those are Python's compiled caches, never work of yours.

## 2b. What did your screener just tell you? (5 min, discuss in the pair)

Your clean screener reports the same thing the awful one did: **this operating
point violates the N-1 criterion** — around 15 contingencies cause overloads,
the worst far beyond limits. That is not a bug in your code (the oracle agrees) —
and it is not news: several of you caught this weakness already in EG2130.
Now your own screener confirms it systematically. The Svedala CGMES file is a
**stressed planning snapshot** — a design case, deliberately loaded to the
edge. Real
systems are studied at such points precisely to find their limits; nobody would
*operate* there. Two questions to discuss and note in your repo — a `NOTES.md` in the repo root, which Lab 3 continues (`git add NOTES.md`, commit, push, so your partner and your pod can read it):

1. If you were the operator handed this screener output, what would you do first?
2. How much load do you think Svedala *can* serve N-1 securely? Guess a
   percentage and note it — scaled cases return in Module 3, and your
   screener will be the judge.

## 3. Pod check (20 min)

Swap with the other pair in your pod (open their repo on GitHub — everyone in the course can read every course repo). Review `screener.py` and its history against the checklist (`labs/review_checklist.md`) — on GitHub the history is the **Commits** link (the clock icon next to the branch name; clicking a commit shows its diff) — then write **three sentences** in their repo: one thing done well, one concrete improvement, one question. It goes in a GitHub **Issue** — the **Issues** tab at the top of their repository, then **New issue** — titled "Lab 2 pod check". Sign it with both reviewers' names. Nothing is handed in and nothing is graded — the review lives where reviews belong, in the repository. Being reviewed is the product here — this exact format returns in the opposition rounds, with higher stakes.

## Done when

Oracle test green in CI, pod check written, pod check received — before Quiz 1, which reads this lab's material. Extension: add severity ranking — a `rank_contingencies(results)` that takes the screener's table and returns the same table sorted by how much trouble each outage causes, tested. Order by `max_loading_percent`, highest first. AL7 and AL8 tie at the top, so a test that insists on AL7 first will fail on a perfectly good ranking — assert something a tie cannot break. Not-converged rows have no loading to rank by; pandas puts their NaN last, and the docstring says so. (It earns its keep in Module 3, where these rankings become ML training labels.)

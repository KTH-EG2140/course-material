# LC14 hands-on — the A/B experiment (~45 min)

Today the Period 1 rule ends: this is the first course session where you work *with* an agent. The experiment is simple — the same task given twice, once badly and once well — and the task is one you know intimately, because you built it by hand in Lab 2.

**You need:** your agent licence (handed out at LC13), your Period 1 workbook clone with the Lab 2 oracle test green, and an empty scratch folder **outside** the workbook.

Work solo or with your Lab 2 partner — one screen, both judging.

## Part A — the vague prompt (10 min)

Start your agent in the empty scratch folder. This matters: the agent must not be able to see your repository, or it will crib from the screener you already wrote — the experiment needs an agent that starts from nothing, like you did in Lab 2.

Paste exactly this, resisting every urge to improve it:

```text
Write a Python function that screens contingencies in a power grid using pandapower.
```

Take what comes back and save it as `condition_a.py` in the scratch folder. Do not fix it, do not argue with it, do not answer its questions with more than "your choice". Note, in one sentence each: what did it assume about the input, the output, and what "screening" means?

## Part B — the specification (10 min)

**Fresh session, same scratch folder** — condition B must not inherit condition A's context. Paste exactly this:

```text
Write a Python function screen_n1(net, loading_limit=100.0) for pandapower networks.

- Input: a pandapower network ready for pp.runpp. Outage each in-service line in turn.
- Output: a pandas DataFrame, one row per contingency, columns exactly:
  outage_idx, outage_line, status, max_loading_percent, n_violations.
- Non-convergence: catch pandapower's LoadflowNotConverged, record
  status="not_converged" with NaN loading — never skip a case silently.
- Restoration: every outaged line is back in service after the run, even when
  the solve fails (try/finally). The network must be unchanged afterwards.
- Acceptance: on a 52-line network the result has 52 rows; loadings match a
  reference table within 1e-3; violation counts match exactly.
```

Save the result as `condition_b.py`. Same discipline: no fixing, no coaching.

If that specification reads like a docstring plus a test plan, that is the point — you wrote both all through Period 1, and they turn out to be the raw material of a good prompt.

## Part C — judge both (15 min)

Copy `condition_a.py` and `condition_b.py` into an `lc14/` folder in your workbook, and fetch the judge: [lc14_compare.py](companions/lc14_compare.py) (place it in the same folder). It runs a candidate against the acceptance criteria and your Lab 2 oracle:

```bash
python lc14/lc14_compare.py lc14/condition_b.py
python lc14/lc14_compare.py lc14/condition_a.py
```

**Before running it**, read both files and predict each verdict line — the reading is the exercise, the script only checks your judgment. Three things to look for, in order of consequence: does it restore the outaged line when the solve *fails*, does it report non-convergence or swallow it, does the output match the promised shape? The script runs twice — once on the base case, where every outage happens to converge, and once on a stressed grid where many do not. The second run is where those first two sins become visible; a screener can pass the base case with both of them intact.

Then compare with your own `screener.py`. Not on style — on the checklist you were just scored against. Where does the specification-fed version differ from yours, and who is right?

## Part D — the agent reviews the agent (7 min)

One more fresh session. Paste condition A's code in and ask:

```text
Review this function against the following specification. List what fails the
specification, ordered by consequence. Do not rewrite it.
```

…followed by the Part B specification. Now judge the review itself: did it catch what the compare script caught, did it invent problems that are not there, and did it find anything you missed when you read the code? A review that agrees with everything is not a review — and that judgment stays your job in Period 2, where one agent checking another is a working method, not an authority.

## Part E — log it (3 min)

Write one entry in the shape of [decision-log-template.md](../project/decision-log-template.md): what you asked for, what you kept or rejected, and why — today's rejection of condition A with reasons is a perfectly good first entry. This is the habit the project grades: your group's `DECISIONS.md` starts in three weeks, and the opposition rounds read it first.

## What to take with you

- The gap between A and B is the gap between hoping and specifying — input, output, constraints, acceptance. You already know how to write all four.
- The three questions from the [fishbowl](../project/fishbowl-brief.md) — *why did you accept that, did you read it, what would catch it if it were wrong* — were answerable today because a test and an oracle existed before the agent ever ran.
- Keep the scratch-folder habit: an agent only sees what you show it, and that includes every secret in reach. Tokens never go in a prompt, and generated code enters your repository through your judgment, not by default.

# Decision log — template

Copy this file into your group repository as `docs/decision-log.md`. One entry every time the agent proposed something and you decided — adopted or rejected. This log is read: opposition rounds quote it, and your final presentation draws on it. Write the entry when the decision happens, not the night before the freeze — five lines written same-day beat a page reconstructed later.

The log is not a diary of everything the agent did. It records **judgment calls**: the moments where you could have said yes or no, and why you said what you said. Rejections are at least as valuable as adoptions — a log with no rejections says you were not checking.

## Entry format

```
## <date> — <one-line decision>
- **Proposed:** what the agent suggested (one sentence, or the prompt that produced it).
- **Checked:** what you actually did to judge it — tests run, docs read, numbers compared.
- **Decision:** adopted / rejected / adopted-with-changes — and why, in one or two sentences.
- **Consequence:** what changed in the repo (commit or PR), or what you did instead.
```

---

## Two worked entries

## 2026-10-27 — Adopt the agent's TimeSeriesSplit refactor of the walk-forward harness

- **Proposed:** replace our hand-rolled walk-forward loop with `sklearn.model_selection.TimeSeriesSplit`, "less code, same behaviour".
- **Checked:** ran both versions on the Lab 7 test week and asserted the splits are index-identical; read the TimeSeriesSplit docs for the gap/expanding-window semantics.
- **Decision:** adopted — same numbers, thirty fewer lines to maintain, and the harness test stays in place as the guard against silent behaviour change.
- **Consequence:** PR #14; `walk_forward()` now wraps TimeSeriesSplit; the oracle test is unchanged and green.

## 2026-11-03 — Reject the agent's "robustness" fix for non-converging N-1 cases

- **Proposed:** wrap the power-flow call in `try/except` and skip contingencies that fail, "so the screener never crashes".
- **Checked:** counted what disappears on the stressed week — 4 of 52 contingencies silently gone; compared against the Lab 2 oracle: the skipped cases were among the dangerous ones.
- **Decision:** REJECTED — it does not fix non-convergence, it hides it. A screener that drops exactly the worst contingencies is worse than one that stops loudly. Same bug family as the awful screener's silent `except: pass` in Lab 2; the agent's version was just better dressed.
- **Consequence:** kept explicit `status="not_converged"` rows; opened issue #21 to investigate the cases themselves; re-prompted the agent with the explicit-status requirement and merged that version instead.

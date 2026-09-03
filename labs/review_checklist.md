# Peer review checklist (Lab 2 → opposition rounds)

Read the code AND the git history. For each item: fine / could improve / problem.

**Behaviour** — Does the oracle test exist and pass? Would you trust these results?
**Names** — Do functions and variables say what they hold? Any `tmp`, `x`, `data2`?
**Structure** — One job per function? Loader reused, or logic duplicated? Any top-level code that runs on import?
**Error handling** — Specific exceptions? Restoration guaranteed (`finally`)? Anything swallowed silently?
**Tests** — Do they assert something that could actually fail? Tolerances on numerical values? Any test that has never failed?
**History** — Do commit messages say why? Could you follow the work from the log alone?

Then write exactly three sentences in an Issue titled "Lab 2 pod check":
1. One thing done well (be specific — "good names" is not specific)
2. One concrete improvement (point at a line)
3. One honest question

Sign with both reviewers' names. Reviews are about the code, never the coder.

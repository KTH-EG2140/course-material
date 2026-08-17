# Lab 3 — Branches, collisions and git archaeology

*EG2140 · **self-paced** — do it with your lab partner during the week; your pod is first support · ~110 min · host repo: the OTHER partner (swap from Lab 2). No AI tools.*

Two exercises: first you collide with your partner on purpose and clean it up; then you play detective in a repository where something broke, nobody knows when.

## 1. The staged collision (60 min)

Both of you work in the host's repo — the second partner accepts the collaboration invite (host: Settings → Collaborators).

1. **Branch out.** From an up-to-date `main`, each partner creates a branch on their own laptop: `feature/load-scaling` (adds a `--scaling` sanity guard and prints the applied factor in `cmd_pf`) and `feature/result-export` (adds `svedala pf --out results.csv` writing the line results). Both branches will touch `cli.py` — that is the point.
2. **Commit and push both branches.** Small commits, honest messages.
3. **PR #1: the easy one.** First partner opens a Pull Request; the *other* partner reviews it on GitHub — read the diff, comment on at least one line, then merge.
4. **PR #2: the collision.** Second partner opens theirs — GitHub says it cannot merge cleanly. Pull `main` into the branch locally, face the conflict markers, and resolve keeping **both** features working. Push; reviewer re-checks and merges.
5. **Prove the merge.** `svedala pf --scaling 1.05 --out results.csv` must run, scaled, and write the file. If it does, your resolution kept both intents — commit that command's output line into the PR description as evidence.

## 2. Git archaeology (40 min)

Download `bisect-practice.zip` from the course material, unzip, `cd bisect-practice`. Run `pytest -q`: **one test fails.** It passed once — some commit in this 13-commit history broke it, and the commit messages are no help (read them; that is realistic).

Find the guilty commit two ways:

1. **By hand first** (10 min): `git log --oneline`, pick a middle commit, `git checkout <hash>`, run the tests, narrow down. Feel the binary search you are doing.
2. **Then let git do it**: `git switch main` (leave the detached checkout), then

```bash
git bisect start HEAD HEAD~11
git bisect run python -m pytest -q
```

Watch git perform your manual search automatically and name the first bad commit. `git show <hash>` — read what the "tidy formatting" commit actually did. `git bisect reset` when done.

Write two sentences in your repo's `NOTES.md`: what the bug was, and why the commit message made it hard to find by reading history alone.

## Done when

Both PRs merged with review comments, the combined command runs, the bad commit identified with `bisect run`, notes committed. Pod check closes the lab: the other pair reads your merged result and NOTES.md, three sentences as an issue in the host repo ("Lab 3 pod check") — and you theirs. Extension: plant a bug of your own in a fresh branch of bisect-practice, ten commits deep, and have your partner hunt it.

*Why this matters beyond today: in Period 2, "which change broke this?" is a question you will ask about code an agent wrote while you watched. `git bisect` answers it in minutes — if the tests exist. The tests are always the precondition.*

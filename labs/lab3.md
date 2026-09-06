# Lab 3 — Branches, collisions and git archaeology

*EG2140 · **self-paced** — do it with your lab partner during the week; your pod is first support (partner → pod → Discussions → the TA sessions) · ~110 min · host repo: the partner whose name comes LAST alphabetically in today's pair — both of you can push to it, every student has push on every workbook repo. No AI tools.*

Two exercises: first you collide with your partner on purpose and clean it up; then you play detective in a repository where something broke, nobody knows when.

**Before you start.** The host repo needs Lab 1 done — both branches in section 1 extend `cmd_pf` in `cli.py`, the `svedala pf` command. The bisect commands in section 2 are the ones from Part E of the LC4 guide; do that guide first if you have not. Section 2 needs [bisect-practice.zip](bisect-practice.zip) from the course material (on GitHub, open the file and use the **Download raw file** button) — download it now, and put it *next to* your workbook folder, not inside it: it is a git repository of its own, and one repository inside another confuses both.

The partner who is **not** the host works in a clone of the host's repository. A fresh clone has no environment, so build one exactly as in Lab 1:

```bash
git clone https://github.com/KTH-EG2140/p1-workbook-<host>.git
cd p1-workbook-<host>
python3.11 -m venv .venv             # Windows: py -3.11 -m venv .venv
source .venv/bin/activate            # Windows: .venv\Scripts\activate
pip install -r requirements.txt
svedala pf                           # proves the clone works before you branch
```

The first `svedala pf` (or the first `pytest`) in a fresh environment can sit silent for a few minutes: numba, the accelerator in `requirements.txt`, compiles pandapower's solver once and caches it. Every later run takes seconds.

## 1. The staged collision (60 min)

Both of you work on the host's repository, each on your own laptop, each on your own branch. The two features are chosen so that they **must** collide: both change the same line.

1. **Branch out.** Each partner, from an up-to-date `main` (`git switch main && git pull` first — `switch -c` creates the branch and moves you onto it, as in LC4 Part A):

   - Partner A: `git switch -c feature/load-scaling`. In `cmd_pf`, refuse a non-positive `--scaling` before loading the network — `raise SystemExit(f"--scaling must be positive, got {args.scaling}")` (raising `SystemExit` with a message prints it and stops the program with an error code, the polite way for a command-line tool to say no) — **and** add the factor to the end of the summary line the command prints, e.g. `| scaling 1.05`.
   - Partner B: `git switch -c feature/result-export`. Add `--out FILE` to the `pf` command: an `add_argument("--out", default=None, help=...)` next to `--scaling` in `main()`, and in `cmd_pf`, after the power flow, `net.res_line.to_csv(args.out)` when `args.out` is set — **and** add `| written to <file>` to the end of the same summary line, only when a file was written. One way: build the suffix before the print, `written = f" | written to {args.out}" if args.out else ""` — Python's one-line form of *this value if the condition holds, otherwise that one* — and append `+ written` to the summary string.

   Both of you edit the one `print(...)` at the end of `cmd_pf`. That is the collision, and it is guaranteed: two different edits to the same line are the one thing git will not merge without a human.

2. **Commit and push both branches.** Small commits, honest messages. A branch's first push must name its remote home — the `-u` from LC4 Part C:

```bash
git add src/svedala_toolbox/cli.py
git commit -m "pf: reject non-positive --scaling, show the factor in the summary"   # B: your own message
git push -u origin feature/load-scaling                                             # B: feature/result-export
```

3. **PR #1: the easy one.** Partner A opens a Pull Request on GitHub: **Pull requests** tab → **New pull request** → base `main`, compare `feature/load-scaling` → **Create**. Partner B reviews it: **Files changed** shows the diff; hover a line and click the **+** to comment on it — at least one comment — then **Merge pull request**. Both of you: `git switch main && git pull`.

4. **PR #2: the collision.** Partner B opens theirs the same way. The PR page now says **"This branch has conflicts that must be resolved"** — GitHub will not merge it. Resolve it on B's laptop, by bringing the new `main` into the branch. Two commands, the ones LC4 taught, not `git pull` — a plain `git pull` on a branch that has moved on both sides stops with `fatal: Need to specify how to reconcile divergent branches` and three options the course has not covered:

```bash
git switch feature/result-export
git fetch origin               # download GitHub's current main as origin/main; changes nothing of yours yet
git merge origin/main          # merge it into the branch you are standing on
```

   The merge stops with:

```
CONFLICT (content): Merge conflict in src/svedala_toolbox/cli.py
Automatic merge failed; fix conflicts and then commit the result.
```

   Open `cli.py`. The conflict region on the reference solution:

```
<<<<<<< HEAD
          f"worst line {worst:.1f}% | V {net.res_bus.vm_pu.min():.3f}-{net.res_bus.vm_pu.max():.3f} pu"
          + written)
    if args.out:
        net.res_line.to_csv(args.out)
=======
          f"worst line {worst:.1f}% | V {net.res_bus.vm_pu.min():.3f}-{net.res_bus.vm_pu.max():.3f} pu | "
          f"scaling {args.scaling}")
>>>>>>> origin/main
```

   `HEAD` is the branch you are standing on (B's export), the part after `=======` is what came from `origin/main` (A's scaling). Your region will not look exactly like this — which lines fall inside the markers depends on where each of you put things — but the three marker lines are always there, and the question is always the same. Same question as LC4 Part B: which truth wins? **Both.** Edit the region into one print statement that carries the scaling factor *and* the file name, keep the `to_csv` lines, delete the three marker lines, then:

```bash
git add src/svedala_toolbox/cli.py
git commit -m "Merge origin/main into feature/result-export: keep scaling in the summary and the --out export"
git push
```

   The PR page updates itself — the conflict warning is gone. Partner A re-reads **Files changed** and merges.

5. **Prove the merge.** Both of you: `git switch main && git pull`, then

```bash
svedala pf --scaling 1.05 --out results.csv
```

   On the reference solution this prints one line — your wording is your own from Lab 1, the numbers should agree:

```
load 11530.3 MW | losses 466.4 MW | worst line 110.7% | V 0.779-1.117 pu | scaling 1.05 | written to results.csv
```

   and `results.csv` exists, one row per line. If both features show, your resolution kept both intents — paste that output line into PR #2's description as evidence (a merged PR's description can still be edited). `results.csv` is output, not work: delete it, or add it to `.gitignore`, before your next commit.

**Checkpoint:** `git log --oneline --graph` shows two branches leaving `main` and coming back — messier than LC4's single diamond, because GitHub's merge button makes a merge commit for each PR and your resolution is a third. The shape on the reference solution (your hashes differ):

```
*   6bd38bc Merge pull request #2 from feature/result-export
|\
| *   a056181 Merge origin/main into feature/result-export: keep scaling in the summary and the --out export
| |\
| |/
|/|
* |   b993e50 Merge pull request #1 from feature/load-scaling
|\ \
| * | db65d01 pf: reject non-positive --scaling, show the factor in the summary
|/ /
| * 0d59de8 pf: --out writes line results to CSV
|/
* 12d237c Lab 1 state
```

Five commits of yours, three merges — and every line of history says what happened.

## 2. Git archaeology (40 min)

Unzip the file you downloaded, next to your workbook folder (`unzip bisect-practice.zip` on macOS/Linux; on Windows right-click → **Extract All**, or `Expand-Archive bisect-practice.zip .` in PowerShell), and `cd bisect-practice`. Three files: `limits.py`, `report.py`, `test_limits.py` — and a `.git` folder holding thirteen commits. The folder has no environment of its own, so `pytest` comes from your workbook's venv: activate it from here (`source ../p1-workbook-<host>/.venv/bin/activate`, adjust the path to where your workbook lives).

Run the tests with the `python -m pytest` form — same pytest, spelled so that `git bisect` can run it later:

```bash
python -m pytest -q
```

```
F.                                                                       [100%]
=================================== FAILURES ===================================
______________________________ test_known_levels _______________________________

    def test_known_levels():
        assert limit_for(400.0) == 2.0
>       assert limit_for(135.0) == 0.9
E       assert 9.0 == 0.9
E        +  where 9.0 = limit_for(135.0)

test_limits.py:5: AssertionError
=========================== short test summary info ============================
FAILED test_limits.py::test_known_levels - assert 9.0 == 0.9
1 failed, 1 passed in 0.01s
```

**One test fails**: the 135 kV current limit comes back as 9.0 kA instead of 0.9 — ten times too large, the kind of number that makes every overload disappear. It passed once. Some commit in this history broke it, and the messages are no help (read them; that is realistic):

```bash
git log --oneline
```

```
b15b4f9 Additional documentation (10)
ade1b32 Additional documentation (9)
ba88bab Additional documentation (8)
29302e0 Additional documentation (7)
37c6d29 Tidy defaults table formatting
bee48d3 Polish report helper (6)
5c68d36 Polish report helper (5)
c41ca08 Polish report helper (4)
f22f54d Add report helper
19b229e Document review note 3
fa869f2 Document review note 2
5b30c09 Document review note 1
73e8f6d Initial limits module with tests
```

Your hashes are the same as these — the history was built once and zipped. Find the guilty commit two ways:

1. **By hand first** (10 min). Pick a commit in the middle and look at the code as it was then:

```bash
git checkout 5c68d36
python -m pytest -q
```

   `git checkout <hash>` answers with a long note that begins `You are in 'detached HEAD' state`, and `git status` says `HEAD detached at 5c68d36`: you are looking at an old snapshot, not standing on any branch — reading is fine, committing here is not. The tests pass at that commit, so the bug came later; pick a commit between there and the top, check it out, test again. Each round halves what is left — feel the binary search you are doing. (After a test run, `git status` lists a `__pycache__` folder as untracked; that is Python's compiled cache, ignore it.) When you have your suspect, come back to the branch:

```bash
git switch main
```

2. **Then let git do it.** Tell git one commit that is bad and one that is good, and give it the command that decides:

```bash
git bisect start HEAD HEAD~11
git bisect run python -m pytest -q
```

   `HEAD` is the newest commit (bad); `HEAD~11` is eleven commits earlier — "Document review note 1", the second commit, where the tests passed. `bisect run` checks out the middle commit, runs the command, reads pass or fail from its exit code — the number every program hands back when it ends, 0 for success and anything else for failure; pytest returns 0 only when every test passed — and repeats. Trimmed output on the reference run:

```
Bisecting: 5 revisions left to test after this (roughly 3 steps)
[5c68d36669f68a301d332bbbec23c01033e3bab8] Polish report helper (5)
running 'python' '-m' 'pytest' '-q'
2 passed in 0.00s
Bisecting: 2 revisions left to test after this (roughly 2 steps)
...
1 failed, 1 passed in 0.01s
Bisecting: 0 revisions left to test after this (roughly 0 steps)
...
37c6d29ce015e341e122cf3a1df569e0b288e4d4 is the first bad commit
bisect found first bad commit
```

   Four test runs instead of eleven, and the same commit your hand search found. Now read what the "Tidy defaults table formatting" commit actually did:

```bash
git show 37c6d29
```

```
 limits.py | 6 +++++-
 1 file changed, 5 insertions(+), 1 deletion(-)
-DEFAULTS_KA = {400.0: 2.0, 220.0: 1.0, 135.0: 0.9}
+DEFAULTS_KA = {
+    400.0: 2.0,
+    220.0: 1.0,
+    135.0: 9.0,
+}
```

   A reformat of the table — and, inside it, `0.9` became `9.0`. Then, always:

```bash
git bisect reset
```

   It leaves bisect mode and puts you back on `main`.

Write two sentences in the host workbook repo's `NOTES.md` (the file from Lab 2 — create it if that pair did not): what the bug was, and why the commit message made it hard to find by reading history alone. Commit and push.

## Done when

Both PRs merged with review comments, the combined command runs, the bad commit identified with `bisect run`, notes committed. Pod check closes the lab: the other pair reads your merged result and `NOTES.md`, three sentences as an Issue in the host repo (**Issues** tab → **New issue**, titled "Lab 3 pod check", as in Lab 2) — and you theirs. Extension: plant a bug of your own in a fresh branch of `bisect-practice`, ten commits deep, and have your partner hunt it.

*Why this matters beyond today: in Period 2, "which change broke this?" is a question you will ask about code an agent wrote while you watched. `git bisect` answers it in minutes — if the tests exist. The tests are always the precondition.*

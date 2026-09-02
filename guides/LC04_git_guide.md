# LC4 follow-along guide — Version control for collaboration

*EG2140 · Lecturecise 4. The first hour is the Vattenfall guest lecture, so this guide is self-paced: work through it before Lab 3 (~40 min). You need the survival git from LC2 (config, init, add, commit).*

Work in a scratch copy — not your toolbox: `mkdir git-practice && cd git-practice && git init`.

*(If `git switch main` below answers `invalid reference: main`: your git names its first branch `master`. Fix it once with `git branch -m main`, and run `git config --global init.defaultBranch main` so every future repo starts on `main`.)*

## Part A — Branches (10 min)

```bash
echo "limits = {400: 2.0}" > limits.py
git add -A && git commit -m "Start limits table"
git switch -c add-220kv          # create + switch to a branch
echo "limits[220] = 1.0" >> limits.py
git commit -am "Add 220 kV limit"
git switch main                  # look: your change is gone...
git log --all --oneline          # ...no — it lives on the branch
```

**Checkpoint:** two branches, one commit apart. A branch is just a movable label on a commit — cheap to make, cheap to throw away.

## Part B — A merge that hurts (15 min)

Create a conflict on purpose. On `main`:

```bash
echo "limits = {400: 2.1}  # updated per planning dept" > limits.py
git commit -am "Update 400 kV limit"
git merge add-220kv
```

**Checkpoint:** `CONFLICT (content): Merge conflict in limits.py`. Open the file:

```
<<<<<<< HEAD
limits = {400: 2.1}  # updated per planning dept
=======
limits = {400: 2.0}
limits[220] = 1.0
>>>>>>> add-220kv
```

Git is not broken — it is *asking you a question* no algorithm can answer: which truth wins? Edit the file to the version that keeps **both** intents (the 2.1 value *and* the 220 kV entry), delete the markers, then:

```bash
git add limits.py && git commit -m "Merge add-220kv, keep updated 400 kV value"
```

**Checkpoint:** `git log --oneline --graph` shows the diamond. You have resolved your first conflict; Lab 3 stages a bigger one with a partner.

## Part C — Pull requests: the review mechanism (10 min, on GitHub)

*Switch back to your **toolbox repository** for this part — not the `git-practice` scratch folder. The scratch folder has no remote on GitHub, and a pull request needs one.*

Make a branch with any small change and push it:

```bash
git switch -c lc04-practice
# touch up a docstring or a comment somewhere, then:
git add -A
git commit -m "Docstring touch-up (LC4 PR practice)"
git push -u origin lc04-practice   # -u: a branch's FIRST push must name its remote home
```

(Plain `git push` on a new branch stops with `fatal: ... has no upstream branch` — that is what `-u origin <branch>` is for; you need it once per branch.) Now open a Pull Request on GitHub (base: `main`, compare: `lc04-practice`). Look at what the PR page gives you: the **diff** (exactly what would change), a place to **comment on any line**, and a **merge button that can wait**. That gap — between "code exists" and "code is accepted" — is where review lives. Every lab from now on merges through it, and in Period 2 it is where you will catch what the AI got wrong.

Two habits that make PRs reviewable: small (one intent per PR) and described (what + why in the description, so the reviewer isn't reverse-engineering you).

## Part D — Code you did not write (5 min, read)

The course rule, from here to the end: **anything you did not write gets attributed.** A copied function gets a comment with its source and license; a dependency gets a `requirements.txt` line; in Period 2, agent-generated code gets a decision-log entry. Licensing is not decoration — your project repos will be published, and unattributed code is the one thing that blocks publication.

## Part E — Finding the commit that broke it (10 min)

Lab 3 asks you to find a bug in a 13-commit history. `git bisect` does that by binary search: you tell it one commit where the code was fine and one where it is broken, and it checks out the middle one for you, over and over, until one commit is left.

Try the mechanism once here, in the scratch repo, where you know the answer. Go back to the `git-practice` folder from Part A (from your toolbox repo that is typically `cd ../git-practice`) and make five commits — one of them quietly breaks the limit value, and the messages are deliberately useless, exactly like Lab 3's. First create `test_limit.py` with your editor — one test that fails exactly when the limit is wrong:

```python
def test_limit_is_sane():
    # the 400 kV limit is a small number in kA — 21 means someone dropped a dot
    assert float(open("limit.txt").read()) < 3
```

Then the five commits:

```bash
echo "2.1" > limit.txt
git add limit.txt test_limit.py
git commit -qm "set the 400 kV limit"
echo "note 1" >> notes.txt
git add notes.txt
git commit -qm "tidy formatting"
echo "21" > limit.txt
git commit -aqm "tidy formatting"
echo "note 2" >> notes.txt
git commit -aqm "tidy formatting"
echo "note 3" >> notes.txt
git commit -aqm "tidy formatting"
```

The limit silently became 21 somewhere in the middle — pretend you just discovered that and do not know when. Tell git the newest commit is bad and the oldest good, then judge each commit it checks out by looking at the file (`cat limit.txt` — 2.1 is good, 21 is bad):

```bash
git bisect start HEAD HEAD~4     # bad = now, good = four commits back
cat limit.txt                    # look at the commit git checked out - it shows 21
git bisect bad                   # so tell git: this one is broken
cat limit.txt                    # git jumps to the next candidate - this one shows 2.1
git bisect good                  # so: fine. git now names the first bad commit
git bisect reset                 # always: leaves bisect mode, back to your branch
```

Git names the first bad commit — check it is the `21` one (`git show <hash>`), and notice how little the message helped. Now the same search with nobody judging: `test_limit.py` has been in every commit since the first, so a test can decide good/bad instead of you. This is the exact form Lab 3 uses:

```bash
git bisect start HEAD HEAD~4
git bisect run python -m pytest -q
git bisect reset
```

(`pytest` comes from your course environment — if `python -m pytest` is not found, activate the venv as in the LC2 guide first.)

**Checkpoint:** both rounds name the same commit — the one you judged by hand and the one `git bisect run` found alone. Five commits take a minute; thirteen take four steps instead of thirteen.

This Part E is the warm-up. Lab 3 runs the same search on a separate history you download as [bisect-practice.zip](../labs/bisect-practice.zip) — 13 commits, so the span there is `git bisect start HEAD HEAD~11`, and a failing test plays the judge from the start.

*Reading: Pro Git, "Debugging with Git" (in the Git Tools chapter) — https://git-scm.com/book/en/v2/Git-Tools-Debugging-with-Git*

## Self-check

1. You resolved the Part B conflict and the file keeps both changes
2. You opened (not necessarily merged) one real PR on your toolbox repo
3. You ran a bisect session to the end, including `git bisect reset`, and it named the `21` commit
4. You can explain what `<<<<<<<` / `=======` / `>>>>>>>` delimit

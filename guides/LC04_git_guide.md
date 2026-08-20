# LC4 follow-along guide — Version control for collaboration

*EG2140 · Lecturecise 4. The first hour is the Vattenfall guest lecture, so this guide is self-paced: work through it before Lab 3 (~40 min). You need the survival git from LC2 (config, init, add, commit).*

Work in a scratch copy — not your toolbox: `mkdir git-practice && cd git-practice && git init`.

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

Push a branch of your *toolbox* repo and open a Pull Request on GitHub (base: `main`, compare: your branch). Look at what the PR page gives you: the **diff** (exactly what would change), a place to **comment on any line**, and a **merge button that can wait**. That gap — between "code exists" and "code is accepted" — is where review lives. Every lab from now on merges through it, and in Period 2 it is where you will catch what the AI got wrong.

Two habits that make PRs reviewable: small (one intent per PR) and described (what + why in the description, so the reviewer isn't reverse-engineering you).

## Part D — Code you did not write (5 min, read)

The course rule, from here to the end: **anything you did not write gets attributed.** A copied function gets a comment with its source and license; a dependency gets a `requirements.txt` line; in Period 2, agent-generated code gets a decision-log entry. Licensing is not decoration — your project repos will be published, and unattributed code is the one thing that blocks publication.

## Part E — Finding the commit that broke it (10 min)

Lab 3 asks you to find a bug in a 13-commit history. `git bisect` does that by binary search: you tell it one commit where the code was fine and one where it is broken, and it checks out the middle one for you, over and over, until one commit is left.

Try the mechanism once here, in the scratch repo, where you know the answer. Make five commits, breaking something in the middle:

```bash
cd git-practice
for i in 1 2 3 4 5; do echo "line $i" >> notes.txt; git add notes.txt; git commit -qm "commit $i"; done
```

Now say that the newest commit is bad and the oldest is good, and mark each step by hand:

```bash
git bisect start HEAD HEAD~4     # bad = now, good = four commits back
git bisect good                  # or: git bisect bad - for the commit git checks out
...                              # git narrows it down; two or three answers is enough
git bisect reset                 # always: leaves bisect mode, back to your branch
```

When a test can decide for you, git does the whole search on its own — this is the form you use in Lab 3:

```bash
git bisect start HEAD HEAD~11
git bisect run python -m pytest -q
git bisect reset
```

**Checkpoint:** you have seen `start`, `good`/`bad`, `run` and `reset` once. Five commits take a minute; thirteen take four steps instead of thirteen.

*Reading: Pro Git, "Debugging with Git" (in the Git Tools chapter) — https://git-scm.com/book/en/v2/Git-Tools-Debugging-with-Git*

## Self-check

1. You resolved the Part B conflict and the file keeps both changes
2. You opened (not necessarily merged) one real PR on your toolbox repo
3. You ran a bisect session to the end, including `git bisect reset`
3. You can explain what `<<<<<<<` / `=======` / `>>>>>>>` delimit

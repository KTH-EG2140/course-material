# Lab 4 — Bug hunt in contingency code (Quiz 1 at the sitting)

*EG2140 · Quiz 1 at the scheduled sitting (30 min, individual, supervised); the room then stays open as a TA session. The bug hunt itself is **self-paced** — do it with your lab partner during the week, pod as first support (partner → pod → Discussions → the TA sessions) · host repo: the partner whose name comes FIRST alphabetically in today's pair. No AI tools.*

## Quiz 1 (at the sitting)

Individual, supervised, on Canvas, code-reading rather than recall, drawn from a question pool covering Lecturecises 1–5 and the Lab 1–3 material. Failed? The resit is at the end of this week — see the schedule.

## The hunt (70 min)

Each pair receives **one script**: a short Svedala security summary that imports your own toolbox. Before the Quiz 1 sitting we push it into your pair's host repo as `lab4/security_summary.py`. Fetch it the way Lab 3 taught:

```bash
git switch main && git pull
```

(If you still have Lab 2 commits that were never pushed, `git pull` merges our commit with yours and says so — push your own work first and the pull is a plain fast-forward.)

Open it. The script is small: one function, `summarise(net)`, that runs your `run_power_flow` and your `screen_n1` and returns a dictionary of six headline numbers — base-case violations and worst loading, number of contingencies screened, how many cause violations, the worst outage and its loading — plus an `if __name__ == "__main__":` block that prints three lines from that dictionary. Four of the six are counts or names; the two loadings are floats — remember that when you write the test. Run it from the repo root with the venv active:

```bash
python lab4/security_summary.py
```

It runs without crashing. It prints plausible numbers. **Exactly one printed number is wrong, because the script contains one planted bug.** These bugs were written by an AI — in four weeks you will be reviewing its code daily; consider this a first taste of the genre: confident, tidy, wrong.

The rules, in this order:

1. **Find it by reading and by suspicion.** You know this network cold by now. Your `svedala pf` output from Lab 1 holds the true base-case numbers; Lab 2 holds the rest — the awful script's 52 lines and 15 `DANGER` lines, the oracle's worst row (a count of rows with `n_violations > 0` is one pandas line away, as in your oracle test). Which printed line contradicts what you know? (That knowledge is your real debugging tool. Someone who has never run Svedala cannot do this lab.) Then read `summarise` line by line until you can point at the cause. Expect pandas you have not seen — the author was an AI and it writes dense; when a line resists reading, run it on its own with `python -c` and print the length or the head of what it produces, as you did with the screener table in Lab 2.

2. **Write the test that catches it — before touching the bug.** Create `lab4/test_security_summary.py`, next to the script:

```python
from security_summary import summarise
from svedala_toolbox.loader import load_svedala


def test_<what you expect to be true>():
    s = summarise(load_svedala())
    assert s["<the key that is wrong>"] == <the value you know>, f"got {s['...']}"
```

   For a count or a name, `==` is right. For one of the two loadings, it is not — you know 94.9 from a print with one decimal, the dictionary holds 94.8659..., and `==` stays red *after* a correct fix. Lab 2's rule: compare floats with a tolerance, `assert abs(s["<key>"] - 94.9) < 0.1`.

   Two mechanisms, named: pytest puts the test file's own folder on the import path — the list of folders Python searches when it meets an `import` — so `from security_summary import summarise` finds the script sitting next to the test by its file name. And importing the script runs *nothing* — the `if __name__ == "__main__":` guard from LC3 keeps the printing out of the way, so you get the function and only the function. Test the **number in the dictionary**, never the printed sentence: a test that reads printed text is satisfied by editing the text. Run it:

```bash
pytest lab4/ -q
```

   Watch it fail — `1 failed in 2.3s` on the reference, with the `E` line showing the number you got against the number you expected. *This is the step that matters:* the test is your proof you understood the bug, not just spotted it.

3. **Fix the bug minimally.** The offending expression, and any line that only existed to feed it — nothing else. `pytest lab4/ -q` → `1 passed`. Then the whole suite, `pytest -q` from the repo root: pytest *collects* (finds and lists) every `test_*.py` under the folder it is started in, so `tests/` and `lab4/` run together and your count is Lab 2's count plus one — `9 passed, 7 skipped` on the reference solution. Did your fix break anything else?

   One honest question before you move on, the Lab 2 question again: would your test also pass a fake fix — the correct number typed into the dictionary as a constant? It would; a test that pins one number on one network cannot tell a computation from a constant. The reading you did in step 1 is what protects you here; the test pins what you learned. If that bothers you, a second check on the stressed network costs four lines — load a network, set `net.load["scaling"] = 1.05`, call `summarise` on it, and assert the same key against the number your own `svedala pf --scaling 1.05` printed in Lab 1 (a second full screening, so the test takes twice as long).

4. Commit all three — script, test, fix — with a message that names the bug precisely ("threshold compared in per-unit against percent values", not "fixed bug"):

```bash
git add lab4/
git commit -m "<what was wrong, in one line>"
git push
```

## Plant your own (last 20 min)

Take the clean script, plant **one** bug of your own — subtle, plausible, and wrong in a way a test could catch — and deliver it to the other pair in your pod, as a branch in *their* host repo (everyone in the course has push on every workbook repo). Write and try the bug in your *own* repo first, where the venv already works: edit, run `python lab4/security_summary.py`, check that it still runs and prints plausible numbers, then put the file back — `git restore lab4/security_summary.py` returns a file to its last committed state, safe here because the clean version is committed. Then clone their repo if you have not already (`https://github.com/KTH-EG2140/p1-workbook-<their host's username>.git`; no venv needed there — you only carry a file), and:

```bash
git switch -c lab4/planted-bug
# copy your edited lab4/security_summary.py over theirs
git add lab4/security_summary.py
git commit -m "update summary script"
git push -u origin lab4/planted-bug
```

They see it with `git fetch && git switch lab4/planted-bug`. Two rules of the game: the planted code carries **no comment, marker or hint** pointing at the bug, and the commit message reveals nothing — "update summary script" is perfect. Yes, that inverts step 4's rule: honest messages for fixes, poker face for planted bugs. Best planted bug of the day gets named in the next lecturecise.

## Done when

Test-fail-fix-pass committed; your planted bug pushed as `lab4/planted-bug` in the other pair's repo. That closes Module 1: you now have a tested, versioned, reviewed package built entirely by hand — and, more importantly, the reading habits to judge code you did *not* write. From Module 2 the toolbox starts eating real data.

# Lab 4 — Bug hunt in contingency code (Quiz 1 at the sitting)

*EG2140 · Quiz 1 at the scheduled sitting (30 min, individual, supervised); the room then stays open as a TA session. The bug hunt itself is **self-paced** — do it with your lab partner during the week, pod as first support (partner → pod → Discussions → the TA sessions) · host repo: the partner whose name comes FIRST alphabetically in today's pair. No AI tools.*

## Quiz 1 (at the sitting)

Individual, supervised, on Canvas, code-reading rather than recall, drawn from a question pool covering Lecturecises 1–5 and the Lab 1–3 material. Failed? The resit is at the end of this week — see the schedule.

## The hunt (70 min)

Each pair receives **one script**: a short Svedala security summary that imports your own toolbox. Before the Quiz 1 sitting we push it into your pair's host repo as `lab4/security_summary.py`. Fetch it the way Lab 3 taught:

```bash
git switch main && git pull
```

Open it. The script is small: one function, `summarise(net)`, that runs your `run_power_flow` and your `screen_n1` and returns a dictionary of five headline numbers — base-case violations and worst loading, number of contingencies screened, how many cause violations, the worst outage and its loading — plus an `if __name__ == "__main__":` block that prints three lines from that dictionary. Run it from the repo root with the venv active:

```bash
python lab4/security_summary.py
```

It runs without crashing. It prints plausible numbers. **Exactly one of them is wrong, because the script contains one planted bug.** These bugs were written by an AI — in four weeks you will be reviewing its code daily; consider this a first taste of the genre: confident, tidy, wrong.

The rules, in this order:

1. **Find it by reading and by suspicion.** You know this network cold by now. Your `svedala pf` output from Lab 1 holds the true base-case numbers; your Lab 2 oracle holds the true contingency count, the number of dangerous outages and the worst one. Which printed line contradicts what you know? (That knowledge is your real debugging tool. Someone who has never run Svedala cannot do this lab.) Then read `summarise` line by line until you can point at the cause.

2. **Write the test that catches it — before touching the bug.** Create `lab4/test_security_summary.py`, next to the script:

```python
from security_summary import summarise
from svedala_toolbox.loader import load_svedala


def test_<what you expect to be true>():
    s = summarise(load_svedala())
    assert s["<the key that is wrong>"] == <the value you know>, f"got {s['...']}"
```

   Two mechanisms, named: pytest puts the test file's own folder on the import path, so `from security_summary import summarise` finds the script sitting next to the test by its file name. And importing the script runs *nothing* — the `if __name__ == "__main__":` guard from LC3 keeps the printing out of the way, so you get the function and only the function. Test the **number in the dictionary**, never the printed sentence: a test that reads printed text is satisfied by editing the text. Run it:

```bash
pytest lab4/ -q
```

   Watch it fail — `1 failed in 2.3s` on the reference, with the `E` line showing the number you got against the number you expected. *This is the step that matters:* the test is your proof you understood the bug, not just spotted it.

3. **Fix the bug minimally.** `pytest lab4/ -q` → `1 passed`. Then the whole suite, `pytest -q` from the repo root: it collects `tests/` and `lab4/` together, so your count is Lab 2's count plus one — `9 passed, 7 skipped` on the reference solution. Did your fix break anything else?

4. Commit all three — script, test, fix — with a message that names the bug precisely ("threshold compared in per-unit against percent values", not "fixed bug"):

```bash
git add lab4/
git commit -m "<what was wrong, in one line>"
git push
```

## Plant your own (last 10 min)

Take the clean script, plant **one** bug of your own — subtle, plausible, and wrong in a way a test could catch — and deliver it to the other pair in your pod, as a branch in *their* host repo (everyone in the course has push on every workbook repo). Clone their repo if you have not already, then:

```bash
git switch -c lab4/planted-bug
# edit lab4/security_summary.py; run it once - it must still run and print plausible numbers
git add lab4/security_summary.py
git commit -m "update summary script"
git push -u origin lab4/planted-bug
```

They see it with `git fetch && git switch lab4/planted-bug`. Two rules of the game: the planted code carries **no comment, marker or hint** pointing at the bug, and the commit message reveals nothing — "update summary script" is perfect. Yes, that inverts step 4's rule: honest messages for fixes, poker face for planted bugs. Best planted bug of the day gets named in the next lecturecise.

## Done when

Test-fail-fix-pass committed; your planted bug pushed as `lab4/planted-bug` in the other pair's repo. That closes Module 1: you now have a tested, versioned, reviewed package built entirely by hand — and, more importantly, the reading habits to judge code you did *not* write. From Module 2 the toolbox starts eating real data.

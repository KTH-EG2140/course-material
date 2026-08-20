# Lab 4 — Bug hunt in contingency code (Quiz 1 at the sitting)

*EG2140 · Quiz 1 at the scheduled sitting (30 min, individual, supervised); the room then stays open as a TA session. The bug hunt itself is **self-paced** — do it with your lab partner during the week, pod as first support · host repo: the partner whose name comes FIRST alphabetically in today's pair. No AI tools.*

## Quiz 1 (at the sitting)

Individual, supervised, on Canvas, code-reading rather than recall, drawn from a question pool covering Lecturecises 1–5 and the Lab 1–3 material. Failed? The resit is at the end of this week — see the schedule.

## The hunt (70 min)

Each pair receives **one script**: a short Svedala security summary that imports your own toolbox. Before the Quiz 1 sitting we push it into your pair's host repo as `lab4/security_summary.py` — `git pull`, and it is there. It runs without crashing. It prints plausible numbers. **Exactly one of them is wrong, because the script contains one planted bug.** These bugs were written by an AI — in four weeks you will be reviewing its code daily; consider this a first taste of the genre: confident, tidy, wrong.

The rules, in this order:

1. **Find it by reading and by suspicion.** You know this network cold by now — you know its total load, its worst base-case line, its 15 dangerous contingencies. Which printed number contradicts what you know? (That knowledge is your real debugging tool. Someone who has never run Svedala cannot do this lab.)
2. **Write the test that catches it — before touching the bug.** A pytest test that fails on the buggy behaviour. Run it. Watch it fail. *This is the step that matters:* the test is your proof you understood the bug, not just spotted it.
3. **Fix the bug minimally.** Watch your test pass. Run the whole suite — did your fix break anything else?
4. Commit all three — script, test, fix — with a message that names the bug precisely ("threshold compared in per-unit against percent values", not "fixed bug").

## Plant your own (last 10 min)

Take the clean script, plant **one** bug of your own — subtle, plausible, and wrong in a way a test could catch — and deliver it to the other pair in your pod: push it as a branch `lab4/planted-bug` in *their* host repo. (Their host adds one of you as a collaborator first — Settings → Collaborators, the same flow as Lab 3.) Best planted bug of the day gets named in the next lecturecise.

## Done when

Test-fail-fix-pass committed; your planted bug pushed as `lab4/planted-bug` in the other pair's repo. That closes Module 1: you now have a tested, versioned, reviewed package built entirely by hand — and, more importantly, the reading habits to judge code you did *not* write. From Module 2 the toolbox starts eating real data.

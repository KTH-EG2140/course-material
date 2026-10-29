# The opposition pack — forms and instructions

Opposition is part of your examination: each group examines another group's work three times, and is examined three times. It is practiced code review, not a debate club — the goal is to make the opposed project *better* while it can still change.

## The weekly rhythm (identical every round)

| When | Who | What |
|---|---|---|
| Wednesday 19:00 | opposed group | tag the repository `opp1` / `opp2` / `opp3` — the tag freezes what is reviewed; work on main continues |
| Friday 19:00 | opposing group | three questions posted as THREE issues in the opposed repo, one question each, against the tag; the issue links submitted in Canvas |
| Monday session | both groups | 20 minutes per pairing: questions, answers, discussion of the tagged state |

## The three questions

Each round, post exactly three questions, one issue each, titled "Opposition round N, question 1/2/3 — from group X". One issue per question keeps each answer and its follow-up in one thread. A good opposition question is specific (points at a file, a function, a decision-log entry), answerable (the opposed group can respond with evidence), and consequential (the answer should matter for the project's success). "Why did you choose X over Y for Z?" beats "have you thought about performance?".

## Round themes

- **Round 1 — Architecture and design.** Basis: the design half of the plan (sections 8–9: the environment–agent figure and the stack) and the `opp1` tag. Does the environment fit the challenge? Is the interface between environment and agent program defensible — written down, tested? Where is the riskiest assumption?
- **Round 2 — Testing.** Basis: the `opp2` tag. What is tested, what is not, and does the test suite actually protect what matters? Would you trust this CI to catch the agent's mistakes?
- **Round 3 — Results and interface.** Basis: the `opp3` tag. Are the results evaluated honestly (baselines, splits, metrics)? Can an outsider run and understand the deliverable?

## In the session

The session is recorded on the one-page form in [opposition-form.md](opposition-form.md): the questions as posted, the answers given, the follow-ups, and at most three concrete takeaways agreed by both groups. The opposing group fills it in and the opposed group gets a copy.

The opposing group leads: restate each question briefly, let the opposed group answer, follow up once. The opposed group answers from the tagged state — "we fixed that yesterday" is a fine remark but the discussion concerns the tag. Everyone else listens; the best follow-up question from the audience is welcome in the last minutes.

## What is assessed

Each round is one of the six oral sessions: every member of both groups is scored individually, 0–2 (absent / answered or asked when it was your turn / also spoke up unasked). Questions posted on time are a gate: not posted by Friday 19:00 = 0 for the whole opposing group that round. Each question is put to a member of the opposed group drawn at the session, so everyone must be ready to answer from the repository. MANDATORY attendance: a missed round must be made up with the examiner.

# The opposition pack — forms and instructions

Opposition is part of your examination: each group examines another group's work three times, and is examined three times. It is practiced code review, not a debate club — the goal is to make the opposed project *better* while it can still change.

## The weekly rhythm (identical every round)

| When | Who | What |
|---|---|---|
| Wednesday 19:00 | opposed group | tag the repository `opp1` / `opp2` / `opp3` — the tag freezes what is reviewed; work on main continues |
| Friday 19:00 | opposing group | three questions posted as ONE issue in the opposed repo, against the tag; issue link submitted in Canvas |
| Monday session | both groups | 20 minutes per pairing: questions, answers, discussion of the tagged state |

## The three questions

Each round, post exactly three questions as an issue titled "Opposition round N — questions from group X". A good opposition question is specific (points at a file, a function, a decision-log entry), answerable (the opposed group can respond with evidence), and consequential (the answer should matter for the project's success). "Why did you choose X over Y for Z?" beats "have you thought about performance?".

## Round themes

- **Round 1 — Architecture and design.** Basis: the design document and the `opp1` tag. Does the structure fit the challenge? Are the module boundaries and data flows defensible? Where is the riskiest assumption?
- **Round 2 — Testing.** Basis: the `opp2` tag. What is tested, what is not, and does the test suite actually protect what matters? Would you trust this CI to catch the agent's mistakes?
- **Round 3 — Results and interface.** Basis: the `opp3` tag. Are the results evaluated honestly (baselines, splits, metrics)? Can an outsider run and understand the deliverable?

## In the session

The opposing group leads: restate each question briefly, let the opposed group answer, follow up once. The opposed group answers from the tagged state — "we fixed that yesterday" is a fine remark but the discussion concerns the tag. Everyone else listens; the best follow-up question from the audience is welcome in the last minutes.

## What is assessed

Opposition earns up to 2 points per round (6 of the 28 project points): substantive questions posted on time, active and constructive participation in the session, and answers grounded in your own repository when you are opposed. MANDATORY attendance: all three rounds are gates for course completion.

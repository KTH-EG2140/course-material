# The four project challenges

Each challenge comes from a company that presents it in person during Period 1 (see the schedule) and returns for the final presentations. The descriptions below are the working brief; the guest lecture adds context, data pointers and the company's own emphasis. Every challenge is sized for a group of 3-4 with an AI agent under supervision — the deliverable is always a working, tested, documented system plus your decision log.

## 1. Vattenfall — grid capacity screening (presented at LC4)
Distribution customers ask for new connections faster than grids grow. Build a tool that, for a queue of connection requests against the Svedala network (size, bus, type), screens which can be accepted directly, which need reinforcement, and which should be offered a flexible connection — with N-1 security as the acceptance criterion and a ranked, explained output an engineer can act on.

## 2. Hitachi Energy — the operator's morning report (presented at LC09)
Control-room software drowns operators in signals. Using the course year of operational data, build the system that writes the morning report: what happened in the grid during the night (load, temperature, anomalies, near-limit hours), what today looks like (forecast with uncertainty), and what deserves a human's attention first — generated automatically, verifiable against the data behind it.

## 3. Svenska kraftnät — imbalance forecasting (presented at LC6)
The system operator pays for every megawatt of imbalance. Build a forecasting service for zonal load that beats the course baselines honestly (walk-forward, against persistence and SARIMA), quantifies its own uncertainty, and — the SvK emphasis — knows when NOT to trust itself: flag the hours where the forecast is likely to be poor, before they happen.

## 4. DigPro — from CIMXML to a decision (presented at LC10)
Grid data lives in CIMXML; decisions live in people. Build the pipeline that ingests a CGMES model plus a stream of SSH snapshots, runs N-1 contingency analysis across them, and presents the results so that the *prioritisation* is the interface: which contingencies matter, when, and why — not a table of everything, but a defensible shortlist.

## Choosing

Groups of 3-4 sign up in Canvas; each challenge is taken by exactly one group (first come, first served, and the exchange-student rule from Lab 1 applies: spread experience). You may propose a variation of a challenge in your project plan — argue it, and clear it at the plan seminar.

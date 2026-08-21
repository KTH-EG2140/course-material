# Project plan and system design — template

*EG2140 Period 2. One document per group, handed in Thursday 22 October 12:00 and presented
at the seminar on Friday 23 October. It is a steering document: too long and nobody reads it,
too short and it steers nothing.*

*The plan half follows the KTH structure — the full guidance, section by section, is the
document "The content of a project plan" linked on the Lecturecise 15 page in Canvas. The
design half is specific to this course, and it is what opposition round 1 interrogates.*

---

## 1. Background

Why this project exists: the challenge as the company posed it, and what already exists that
you build on (your toolbox, the data pipeline, the forecaster). End with a list of reference
documents — the challenge brief, the course PM, anything the mentor gave you.

*It should be readable on its own, and with small changes it becomes the introduction to your
final documentation.*

## 2. Goals

Narrow the background into goals, then list them as bullets — each one testable, each one with
how you will test it. Include your delimitation: what you are explicitly not doing.

- Project goals: what the deliverable does.
- Business goals for this course: what the group wants out of it, and by when.

*"A forecast tool" is not a goal. "Hourly zonal forecast, 24 hours ahead, beating seasonal
persistence on the reference week" is one, and you can test it.*

## 3. Organisation

The four of you, with real responsibilities — connected to goals, deliveries or a technical
area. Include the mentor and how to reach them.

## 4. Project model

Phases, milestones and dates in a table, one responsible person each. Your opposition tags,
the fishbowl and the freeze are already milestones; add your own so that each sub-goal has at
least one.

| Phase | Milestone | Ready date | Responsible |
|---|---|---|---|
| | | | |

## 5. Commentary on the time and resource plan

What was uncertain when you planned, what is not planned yet, and when you will plan it.
Exam periods and other courses belong here.

## 6. Risk analysis

At least five risks, with probability, consequence, action, follow-up date and a responsible
person. Proactive actions where you can, reactive where you cannot.

| Risk | P | C | R | Action (proactive / reactive) | Follow-up | Responsible |
|---|---|---|---|---|---|---|
| | | | | | | |

*Read each action and ask: so what? If you would have done it anyway, it is not an action.*

## 7. Document and communication rules

How you communicate, how often you meet the mentor, where things are stored, how documents are
named and versioned, who is responsible for what. In this course, add: how the decision log is
kept and by whom.

---

# The design

*This half is not in the KTH structure. It is ours, because in Period 2 an agent writes part of
the code and the design is what makes that reviewable.*

## 8. Architecture

The modules and what each is responsible for. One diagram, simple enough that anyone in the
group could redraw it from memory.

## 9. Data flow

Where data enters, what happens to it, where results leave. You have built this twice already,
in Labs 5 and 6.

## 10. Test strategy

What you will test and how — the tests are what let you accept agent-written code at all. Say
what CI runs and when.

## 11. Technology stack, justified

What you chose and why. pandapower is not mandated. Choosing is a decision with reasons, and
not something an agent does for you.

---

## Appendices

- **Time plan** — the graphical version of the project model. The same milestones, no others.
- **Resource plan** — who works when, given the rest of your term.
- **Work breakdown structure** — including photographs of making it, if you did it on a wall.

*Tip for this course: break the WBS down until each leaf is about a week's work for one pair —
which is usually also small enough to be a specification you could hand to an agent. Estimate
the reading of what comes back, not only the writing.*

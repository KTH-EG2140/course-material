# Lab 1 — Start the svedala-toolbox: from notebook to package

*EG2140 · in pairs (assigned at the start of the session) · ~110 minutes.
Goal: turn code you already understand into software someone else could use.*

In the LC1 warm-up notebook — [notebooks/LC01_svedala_warmup.ipynb](../notebooks/LC01_svedala_warmup.ipynb), the one from the first session — you (re-)ran a Svedala power flow. That code works — but it lives in a notebook: not installable, not testable, not reviewable. Today you turn it into a package. **The power-flow logic is not the work; the engineering around it is.** No AI coding tools.

---

## 0. Get your repository (10 min)

1. Accept the email invitation to your personal repository `p1-workbook-<username>` (sent after Lecturecise 1, to the address behind the Github username you gave in the diagnostic). It is created for you from the course template.
2. Clone it, create the environment, install:

```bash
git clone <your-repo-url>
cd p1-workbook-<you>
python -m venv .venv
source .venv/bin/activate            # Windows: .venv\Scripts\activate
pip install -r requirements.txt      # the dependencies
pip install -e .                     # your own package, editable
```

3. Look around. The layout is the one from LC2, with three things already in place: a **stubbed package** in `src/svedala_toolbox/`, a **test suite** in `tests/` (one test passing, two waiting for your code), and a **self-check** in `checks/`.

Run the self-check now, before writing anything:

```bash
python checks/lab1_check.py
```

One PASS, four FAIL. Those four FAIL lines are this lab's task list.

`checks/lab1_check.py` is a thin wrapper: it runs the same tests `pytest -q` runs and prints them as a task list, so you can see at a glance what is left. Use either — the counts describe the same tests. *(Laptop trouble? Say so at the start of the session; that is what the session is for.)*

## 1. Port the loader (30 min)

Open `src/svedala_toolbox/loader.py`. Two functions carry TODOs — the signatures and docstrings are already sketched in the stub; you write the bodies:

- **`load_svedala()`** — move the loading code from your warm-up notebook into this function: read the five CSVs (`index_col=0`, the indices matter), create the network, add buses, lines, transformers, generators, loads. Keep the current-limit defaults exactly as the stub describes — including the comment saying they are an assumption. Keep the slack flag on the generators.
- **`run_power_flow()`** — run `pp.runpp` and **raise a `RuntimeError` with a useful message if the power flow does not converge.** A function that returns nonsense quietly is worse than one that stops loudly (this idea gets a whole lecturecise later).

Working in a module instead of a notebook means: no prints scattered around, no top-level code that runs on import, docstrings kept honest.

**Checkpoint:** `pytest tests/ -q` — the two provided loader tests now pass.

Commit: `git add -A && git commit -m "Port Svedala loader from L1 notebook"` and `git push`.

## 2. Wire the CLI (25 min)

Open `src/svedala_toolbox/cli.py`. The argument parsing is done; two command functions carry TODOs:

- **`svedala info`** — element counts and the list of zones.
- **`svedala pf`** — run a power flow (honouring `--scaling`) and print one summary line: total load, losses, worst line loading, voltage range.

The command already exists on your PATH (that is what the editable install did) — it just crashes until you fill the functions.

**Checkpoint:**

```bash
svedala info
svedala pf
svedala pf --scaling 1.05      # the Lab-1 version of the notebook's task 3
```

Commit and push.

## 3. Write the first test the Svedala loader has ever had (20 min)

Open `tests/test_loader.py`. Two tests are written for you as models. Add **one of your own** — something *you* think should always be true of a correctly loaded Svedala network. Ideas in the file; better if you invent your own. One good assertion beats five trivial ones.

Then make it mean something: break the loader on purpose (comment out the slack flag, or skip the loads), watch your test fail, restore, watch it pass. **A test you have never seen fail proves nothing.**

Commit and push. Notice the dot next to your commit on GitHub turning green — that is the CI robot running your tests on every push, from your `requirements.txt`, on a machine you have never touched. Reproducibility, cashed in.

## 4. Finish line (5 min)

```bash
python checks/lab1_check.py
```

**ALL OK = done.** The self-check is for you — nothing is handed in. The quiz in Lab 4 will show you code like today's and ask what is wrong with it; having done this lab *is* the preparation.

## Extension (if time remains)

- Delete your `.venv/`, rebuild it from `requirements.txt`, reinstall the package and run the self-check again. Same result, environment thrown away and recreated in a minute — that is what LC2 meant by the recipe being the thing you keep.
- Add `svedala pf --scaling 1.10` to your experiments: at what scaling does the first line pass 100%? Remember the number — it returns when we generate training data in Module 3.

---

*Pairs and pods: you work at one laptop, in the repository of whichever partner's name comes first alphabetically today — the other partner's repo hosts Lab 2's work (Lab 3 swaps again). Your **pod** is four people: your pair plus one other pair, formed today and kept through Period 1. Each lab you work in pairs, alternating partners within the pod — same four people, different pairings. For the self-paced labs the pod is your first line of support: partner → pod → Discussions → the TA sessions. Both of you must be able to explain every line committed: quiz questions are individual.*

# Lab 1 — Start the svedala-toolbox: from notebook to package

*EG2140 · in pairs (assigned at the start of the session) · ~110 minutes.
Goal: turn code you already understand into software someone else could use.*

In the LC1 warm-up notebook — [notebooks/LC01_svedala_warmup.ipynb](../notebooks/LC01_svedala_warmup.ipynb), the one from the first session — you (re-)ran a Svedala power flow. That code works — but it lives in a notebook: not installable, not testable, not reviewable. Today you turn it into a package. **The power-flow logic is not the work; the engineering around it is.** No AI coding tools.

---

## 0. Get your repository (10 min)

1. Check the email behind the Github username you gave in the diagnostic: you received **two** GitHub invitations after Lecturecise 1 — one to the course organisation, one to your personal repository `p1-workbook-<username>` (created for you from the course template). **Accept both.** The organisation invitation is the one that matters: it carries your membership, the cohort team, and the write access that pair work depends on.
2. Clone it, create the environment (explicit Python version — outside a venv, plain `python` is whichever interpreter your system finds first; the LC2 guide has the why), install:

```bash
git clone <your-repo-url>
cd p1-workbook-<you>
python3.11 -m venv .venv             # Windows: py -3.11 -m venv .venv
source .venv/bin/activate            # Windows: .venv\Scripts\activate
pip install -r requirements.txt      # dependencies + your own package, editable (-e . is its last line)
```

3. Look around. The layout is the one from LC2, with three things already in place: a **stubbed package** in `src/svedala_toolbox/`, a **test suite** in `tests/` (one test passing, two waiting for your code), and a **self-check** in `checks/`.

Run the self-check now, before writing anything:

```bash
python checks/lab1_check.py
```

One PASS, four FAIL. Those four FAIL lines are this lab's task list.

`checks/lab1_check.py` covers the same goals as the tests, printed as a task list so you can see at a glance what is left — plus the CLI commands and the suite as a whole, which `pytest -q` alone does not reach. That is why its counts differ from pytest's; both views go green together when the lab is done. *(Laptop trouble? Say so at the start of the session; that is what the session is for.)*

## 1. Port the loader (30 min)

Open `src/svedala_toolbox/loader.py`. Two functions carry TODOs — the signatures and docstrings are already sketched in the stub; you write the bodies:

- **`load_svedala()`** — move the loading code from your warm-up notebook into this function: read the five CSVs (`index_col=0`, the indices matter), create the network, add buses, lines, transformers, generators, loads. Keep the current-limit defaults exactly as the stub describes — including the comment saying they are an assumption. Keep the slack flag on the generators.
- **`run_power_flow()`** — run `pp.runpp` and **raise a `RuntimeError` with a useful message if the power flow does not converge.** Careful: pandapower reports non-convergence by raising its own `pp.LoadflowNotConverged` — catch that and re-raise it as your `RuntimeError`. A function that returns nonsense quietly is worse than one that stops loudly (this idea gets a whole lecturecise later).

Working in a module instead of a notebook means: no prints scattered around, no top-level code that runs on import, docstrings kept honest.

Before the checkpoint, meet the tool behind it. **pytest is a test runner**: it looks in `tests/` for files named `test_*.py`, runs every function named `test_*`, and counts. A test fails when an `assert` inside it is false or an error is raised. The `-q` flag keeps it quiet — one character per test, then a summary. Today you only *run* tests; writing them gets its own treatment in Lecturecise 5.

This is what `pytest tests/ -q` printed on a fresh repository, before any code was written (trimmed to the parts you read):

```
ssssFFsss.                                                               [100%]
=================================== FAILURES ===================================
______________________________ test_network_sizes ______________________________

    def test_network_sizes():
        """The model has the element counts we know from the data."""
>       net = load_svedala()
...
>       raise NotImplementedError("Lab 1: port your notebook code here")
E       NotImplementedError: Lab 1: port your notebook code here

src/svedala_toolbox/loader.py:35: NotImplementedError
... (the second failure reads the same) ...
=========================== short test summary info ============================
FAILED tests/test_loader.py::test_network_sizes - NotImplementedError: Lab 1:...
FAILED tests/test_loader.py::test_power_flow_converges - NotImplementedError:...
2 failed, 1 passed, 7 skipped in 17.42s
```

How to read it:

- Each `.` is a pass, each `F` a failure, each `s` a skipped placeholder for a later lab.
- The FAILURES section replays each failing test — read the `E` lines and the assert or raise they point at (here: the stub's `NotImplementedError`), ignore the rest at this stage.
- The last line is the count, and it is the verdict.

Failing tests before you write the code are expected — they are the task list.

**Checkpoint:** `pytest tests/ -q` — the two provided loader tests now pass: **3 passed, 7 skipped**.

Commit: `git add -A && git commit -m "Port Svedala loader from L1 notebook"` and `git push`.

## 2. Wire the CLI (25 min)

Open `src/svedala_toolbox/cli.py`. The argument parsing is done; two command functions carry TODOs:

- **`svedala info`** — element counts and the list of zones.
- **`svedala pf`** — run a power flow (honouring `--scaling`) and print one summary line: total load, losses, worst line loading, voltage range.

The command already exists on your PATH — it just crashes until you fill the functions. Where it came from: `pyproject.toml` declares `svedala = "svedala_toolbox.cli:main"` under `[project.scripts]`, the editable install (the `-e .` from LC2's C3) wrote a small `svedala` executable into `.venv/bin` (`Scripts\` on Windows), and activating the venv put that folder first on PATH. One more piece of magic worth naming: the usage text a bare `svedala` prints is argparse's own, generated from the parser declarations in `cli.py` — no code of ours prints it.

**Checkpoint:**

```bash
svedala info
svedala pf
svedala pf --scaling 1.05      # the Lab-1 version of the notebook's task 3
```

Commit and push.

## 3. Write the first test the Svedala loader has ever had (20 min)

Open `tests/test_loader.py`. Two tests are written for you as models. Add **one of your own** — something *you* think should always be true of a correctly loaded Svedala network. Ideas in the file; better if you invent your own. One good assertion beats five trivial ones.

Then make it mean something: break the loader on purpose (comment out the slack flag, or skip the loads), run `pytest tests/ -q` and watch your test fail — same reading as before — then restore and watch it pass. **A test you have never seen fail proves nothing.**

Commit and push. Notice the dot next to your commit on GitHub turning green — that is the CI robot running your tests on every push, from your `requirements.txt`, on a machine you have never touched. Reproducibility, cashed in.

## 4. Finish line (5 min)

```bash
python checks/lab1_check.py
```

**ALL OK = done.** The self-check is for you — nothing is handed in. The quiz in Lab 4 will show you code like today's and ask what is wrong with it; having done this lab *is* the preparation.

## Extension (if time remains)

- Delete your `.venv/`, rebuild it from `requirements.txt` (which reinstalls your package too) and run the self-check again. Same result, environment thrown away and recreated in a minute — that is what LC2 meant by the recipe being the thing you keep.
- Add `svedala pf --scaling 1.02` to your experiments — the first line just reaches 100%. Then keep raising the scaling in small steps: at what point does the power flow stop converging entirely? Remember both numbers — the edge returns in the LC5 testing session, and scaled cases return when we generate training data in Module 3.

---

*Pairs and pods: you work at one laptop, in the repository of whichever partner's name comes first alphabetically today — the other partner's repo hosts Lab 2's work (Lab 3 swaps again). Your **pod** is four people: your pair plus one other pair, formed today and kept through Period 1. Each lab you work in pairs, alternating partners within the pod — same four people, different pairings. For the self-paced labs the pod is your first line of support: partner → pod → Discussions → the TA sessions. Both of you must be able to explain every line committed: quiz questions are individual.*

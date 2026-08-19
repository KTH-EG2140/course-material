# LC2 follow-along guide — Reproducible environments (+ survival git)

*EG2140 · Lecturecise 2 hands-on. Work along in the session, or self-paced if you missed it. Time: ~45 minutes, plus Part C (~10 min) before Lab 1. Nothing here touches your course repository — that arrives in Lab 1. Today you practice in a scratch folder.*

**What you need:** a terminal, Python 3.11+, git, a text editor. (Checked in Lecturecise 1 — if something is broken on your machine, fix it now: raise your hand, this session exists for exactly that.)

**A note on terminals:** the commands below work in any modern shell. Where macOS/Linux and Windows differ, both variants are given — pick yours. Everything in this course can be done from the command line, and we encourage it: the CLI is where your Period 2 agent lives too.

---

## Part A — A reproducible environment (25 min)

### A1. Make a scratch folder and check your Python

Create a folder called `eg2140-scratch` anywhere you like and open a terminal **in that folder**.

```bash
mkdir eg2140-scratch
cd eg2140-scratch
python --version
```

*Hints: the two commands above work in both bash and PowerShell, one line at a time. If `python` is not found, try `python3` (macOS/Linux) or `py` (Windows). You can also create the folder in your file manager and use "Open in Terminal" / "Open PowerShell window here".*

**Checkpoint:** version 3.11 or higher.
*If you see 2.x or "command not found": your PATH points at the wrong Python — ask now.*

### A2. Create a virtual environment

A virtual environment is a private set of installed packages for one project — so your projects can't break each other.

```bash
python -m venv .venv
```

Activate it:

```bash
source .venv/bin/activate          # macOS / Linux
```
```powershell
.venv\Scripts\Activate.ps1         # Windows (PowerShell)
```

**Checkpoint:** your prompt now starts with `(.venv)`.
*Windows: if you get an execution-policy error, run `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned` once and retry.*

### A3. Install a package — into the venv, not your system

```bash
pip install pandapower
python -c "import pandapower; print(pandapower.__version__)"
```

**Checkpoint:** a version number prints.

Now see what "into the venv" means:

```bash
deactivate
python -c "import pandapower"    # this should FAIL
```

**Checkpoint:** `ModuleNotFoundError`. That failure is the whole point: the package lives inside `.venv`, nowhere else. Reactivate (same command as in A2).

### A4. Freeze what you depend on

```bash
pip freeze > requirements.txt
```

Look inside the file — with your editor, or:

```bash
cat requirements.txt               # macOS / Linux
```
```powershell
type requirements.txt              # Windows
```

**Checkpoint:** a list of packages with pinned versions. This file *is* reproducibility: anyone (including future-you, and the CI robot you meet in Lab 1) can rebuild your exact environment with `pip install -r requirements.txt`.

### A5. Prove it — the five-line power flow

Create a file `pf.py` with your editor:

```python
import pandas as pd, pandapower as pp

url = "https://raw.githubusercontent.com/KTH-EPE/CIM_exportimport/main/Svedala_csv/loads.csv"
loads = pd.read_csv(url, index_col=0)
print(f"Svedala has {len(loads)} loads totalling {loads.p_mw.sum():.0f} MW")
```

```bash
python pf.py
```

**Checkpoint:** `Svedala has 60 loads totalling 10981 MW`.
Same number on every laptop in the room — that is what "reproducible" means.

### A6. How a small project is laid out

You just made the pieces by hand. A real small Python project arranges them like this — memorize the shape, your Lab 1 repository looks exactly like it:

```
project/
├── .venv/              never committed (see .gitignore below)
├── requirements.txt    committed — this is the environment
├── src/<package>/      the code you keep
├── tests/              the proof it works
└── README.md           how to run it
```

---

## Part B — Survival git (15 min)

Full git comes in Lecturecise 4. Today: the four commands that let you save work in Lab 1. Still in `eg2140-scratch`:

### B1. Tell git who you are (once per machine)

```bash
git config --global user.name  "Your Name"
git config --global user.email "you@kth.se"
```

### B2. Make the folder a repository, and keep the venv out of it

```bash
git init
```

Create a file named `.gitignore` containing a single line: `.venv/` — with your editor, or:

```bash
echo ".venv/" > .gitignore
```

*(The `echo` line works in bash and PowerShell alike.) Why the `.gitignore`: the venv is hundreds of megabytes of rebuildable files. You commit the `requirements.txt` recipe, never the environment itself.*

### B3. The save cycle: status → add → commit

```bash
git status                       # what changed?
git add pf.py requirements.txt .gitignore
git commit -m "First power flow script with pinned environment"
git log --oneline
```

**Checkpoint:** `git log` shows one commit, yours.

That cycle — *status, add, commit with a message that says why* — is the habit. In Lab 1, `push` sends it to GitHub; you get that command with your course repository.

---

## Part C — Prepare for Lab 1 (10 min, do before the Lab 1 session)

Lab 1 assumes the steps below are already done, so that the session is spent building — not installing. Everything is the Part A/B routine, applied to your real course repository.

### C1. Accept the invitation

Check your KTH mail for a GitHub invitation to your personal repository `p1-workbook-<your username>` (sent after the day-1 survey). Accept it and log in on github.com so you can see the repository.

**Checkpoint:** you can open your repository page in the browser.

### C2. Clone it

In the folder where you keep course work (not inside `eg2140-scratch`):

```bash
git clone https://github.com/KTH-EG2140/p1-workbook-<your username>.git
cd p1-workbook-<your username>
```

*If git asks you to authenticate, follow its browser prompt (first time only).*

### C3. Environment, from the recipe this time

Create and activate a venv exactly as in A2, then install the pinned course environment:

```bash
python -m venv .venv
# activate it (A2), then:
pip install -r requirements.txt
```

**Checkpoint:** the install finishes without red errors. It is a few hundred megabytes — do this on decent wifi, not at 09:58 before the lab.

### C4. Install the package you are about to build

```bash
pip install -e .
```

The `-e` is an *editable install*: Python runs the code straight from `src/`, so every edit you make is live immediately — no reinstalling. This is how the toolbox will be developed all through Period 1.

### C5. Run the tests you were given

```bash
pytest -q
```

**Checkpoint:** pytest runs and reports results. Some stub tests are expected to fail — they describe the code you have not written yet. That failing list is, quite literally, your Lab 1 todo list.

---

## Self-check

You are done when all five are true:

1. `python --version` in a fresh terminal says 3.11+
2. You can create, activate and deactivate a venv and explain the `ModuleNotFoundError` in A3
3. `python pf.py` prints the 10 981 MW line
4. `git log --oneline` in your scratch folder shows your commit
5. Your course repository is cloned, its venv installed (C3–C4), and `pytest -q` runs

The scratch folder has served its purpose — keep it or delete it. Lab 1 starts from your real course repository.

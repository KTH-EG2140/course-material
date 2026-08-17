# LC2 follow-along guide — Reproducible environments (+ survival git)

*EG2140 · Lecturecise 2 hands-on. Work along in the session, or self-paced if you missed it. Time: ~45 minutes. Nothing here touches your course repository — that arrives in Lab 1. Today you practice in a scratch folder.*

**What you need:** a terminal, Python 3.11+, git, a text editor. (Checked in Lecturecise 1 — if something is broken, fix it now or use the Codespaces fallback linked on Canvas.)

---

## Part A — A reproducible environment (25 min)

### A1. Make a scratch folder and check your Python

```bash
mkdir eg2140-scratch && cd eg2140-scratch
python --version        # some systems: python3 --version
```

**Checkpoint:** version 3.11 or higher.
*If you see 2.x or "command not found": your PATH points at the wrong Python — ask now, this is exactly what this session is for.*

### A2. Create a virtual environment

A virtual environment is a private set of installed packages for one project — so your projects can't break each other.

```bash
python -m venv .venv
```

Activate it:

```bash
source .venv/bin/activate        # macOS / Linux
.venv\Scripts\activate           # Windows (PowerShell)
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

**Checkpoint:** `ModuleNotFoundError`. That failure is the whole point: the package lives inside `.venv`, nowhere else. Reactivate:

```bash
source .venv/bin/activate        # or the Windows variant
```

### A4. Freeze what you depend on

```bash
pip freeze > requirements.txt
cat requirements.txt             # Windows: type requirements.txt
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
echo ".venv/" > .gitignore
```

*Why the `.gitignore`: the venv is hundreds of megabytes of rebuildable files. You commit the `requirements.txt` recipe, never the environment itself.*

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

## Part C — The same idea, one level up (5 min, watch or try)

A venv freezes your *Python packages*. A **container** freezes the whole machine — OS, Python, everything. Your Lab 1 repository ships a `.devcontainer/` folder: one file that lets GitHub Codespaces build the complete course environment in your browser. It is the fallback if your laptop misbehaves, and it is Docker in its friendliest form. We look inside the file together; nothing to install today.

---

## Self-check

You are done when all four are true:

1. `python --version` in a fresh terminal says 3.11+
2. You can create, activate and deactivate a venv and explain the `ModuleNotFoundError` in A3
3. `python pf.py` prints the 10 981 MW line
4. `git log --oneline` in your scratch folder shows your commit

The scratch folder has served its purpose — keep it or delete it. Lab 1 starts from your real course repository.

# LC2 follow-along guide — Reproducible environments (+ survival git)

*EG2140 · Lecturecise 2 hands-on. Work along in the session, or self-paced if you missed it. Time: ~45 minutes, plus Part C (~10 min) before Lab 1. Nothing here touches your course repository — that arrives in Lab 1. Today you practice in a scratch folder.*

**What you need:** a terminal, Python 3.11+, git, a text editor. Git is a requirement, not a nice-to-have — Part B runs on it and every lab from Lab 1 hands in through it. Check it now with `git --version`; if that fails, install it from https://git-scm.com/downloads (macOS: `xcode-select --install` also works) before you reach Part B. (Both were checked in Lecturecise 1 — if something is broken on your machine, fix it now: raise your hand, this session exists for exactly that.)

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

**Checkpoint:** version 3.11 or higher. Newer is fine too — anything 3.11+ works for this course.
*If you see 2.x or "command not found": your PATH points at the wrong Python — ask now.*

### A2. Create a virtual environment

A virtual environment is a private set of installed packages for one project — so your projects can't break each other.

Outside a venv, plain `python` is whichever interpreter your system finds first — not predictable. Create the venv with an explicit version; the venv then locks that interpreter in:

```bash
python3.11 -m venv .venv           # macOS / Linux
```
```powershell
py -3.11 -m venv .venv             # Windows
```

*3.11 is the version the course stack is pinned and tested on. No `python3.11` on your machine? Use the newest Python 3 you do have — but name it explicitly (`python3.12 -m venv .venv`), never plain `python`.*

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
python -c "import pandapower"    # for most of you this FAILS
```

**Checkpoint:** `ModuleNotFoundError`. That failure is the whole point: the package lives inside `.venv`, nowhere else.

*Did the import succeed instead of failing? Then your system Python already had pandapower (Anaconda installs a lot of things). Your venv still isolates — prove it by running `python -c "import pandapower; print(pandapower.__file__)"` now and again after reactivating: the path changes to one inside `.venv`. That path difference is the same point, made on a machine with a crowded system Python.*

Reactivate (same command as in A2).

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

**Checkpoint:** a list of packages with pinned versions. This file *is* reproducibility: anyone (including future-you, and the CI robot you meet in Lab 1 — CI is a machine that reruns your tests on every push) can rebuild your exact environment with `pip install -r requirements.txt`.

### A5. Prove it — five lines, same number on every laptop

Create a file `pf.py` with your editor:

```python
import pandas as pd

url = "https://raw.githubusercontent.com/KTH-EPE/CIM_exportimport/main/Svedala_csv/loads.csv"
loads = pd.read_csv(url, index_col=0)
print(f"Svedala has {len(loads)} loads totalling {loads.p_mw.sum():.0f} MW")
```

```bash
python pf.py
```

One detail worth registering now: `index_col=0` is not cosmetic — the first CSV column holds each element's ID, and the other Svedala tables refer to elements *by* those IDs, so they must become the DataFrame's index rather than ordinary data (your Lab 1 loader reads all five tables exactly this way).

**Checkpoint:** `Svedala has 60 loads totalling 10981 MW`.
Same number on every laptop in the room — that is what "reproducible" means. (The script needs internet; if the download fails, tell a TA — the same file also ships inside your Lab 1 repository.)

### A6. How a small project is laid out

You just made the pieces by hand. A real small Python project arranges them like this — memorize the shape, your Lab 1 repository looks exactly like it:

```
project/
├── .venv/              never committed (see .gitignore below)
├── requirements.txt    committed — this is the environment
├── src/<package>/      the code you keep (in Lab 1: src/svedala_toolbox/)
├── tests/              the proof it works
└── README.md           how to run it
```

---

## Part B — Survival git (15 min)

Full git comes in Lecturecise 4. Today: the four commands that let you save work in Lab 1. Still in `eg2140-scratch`:

### B1. Tell git who you are (once per machine)

First check whether it is already set — if you have used git before, it is:

```bash
git config --global user.name
git config --global user.email
```

If both print something sensible, **leave them alone** (especially the email your GitHub account knows). If they are empty:

```bash
git config --global user.name  "Your Name"
git config --global user.email "you@kth.se"
```

One more line, for everyone (it makes every new repository start on a branch called `main`, which all course instructions assume — some git installs still default to the older name `master`):

```bash
git config --global init.defaultBranch main
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

### C1. Accept both invitations

Check your KTH mail for **two** GitHub invitations (sent within a day after the day-1 survey): one to the course organisation, one to your personal repository `p1-workbook-<your GitHub username>`. Accept **both**, then log in on github.com so you can see the repository. The organisation invitation is the one that matters — it carries your membership, the cohort team, and the write access pair work depends on.

**Checkpoint:** you can open your repository page in the browser.
*No invitations a day after the survey? Post on Discussions — do not wait until the lab.*

### C2. Clone it

In the folder where you keep course work (not inside `eg2140-scratch`):

```bash
git clone https://github.com/KTH-EG2140/p1-workbook-<your GitHub username>.git
cd p1-workbook-<your GitHub username>
```

*If git asks you to authenticate, follow its browser prompt (first time only). A trap worth knowing: GitHub answers `Repository not found` both when a repository does not exist AND when you are not logged in as someone allowed to see it — so that message usually means "authentication problem" or "invitation not accepted yet", not "the repo is missing".*

### C3. Environment, from the recipe this time

Create and activate a venv exactly as in A2 — explicit interpreter here too — then install the pinned course environment:

```bash
python3.11 -m venv .venv           # Windows: py -3.11 -m venv .venv
# activate it (A2), then:
pip install -r requirements.txt
```

**Checkpoint:** the install finishes without red errors. It is a few hundred megabytes — do this on decent wifi, not at 09:58 before the lab.

### C4. The package you are about to build is already installed

No command here — the last line of `requirements.txt` is `-e .`, so C3 already installed your own package. The `-e` is an *editable install*: Python runs the code straight from `src/`, so every edit you make is live immediately — no reinstalling. This is how the toolbox will be developed all through Period 1.

### C5. Run the tests you were given

```bash
pytest -q
```

**Checkpoint:** pytest reports **1 passed, 2 failed, 7 skipped**. The two failures describe the loader code you have not written yet — that failing list is, quite literally, your Lab 1 todo list. The seven skipped tests are placeholders for later labs; they stay skipped for now.

Your repository also contains `checks/lab1_check.py`. It prints the same state as a task list rather than as test output — **one PASS, four FAIL** before you start — and Lab 1 opens by running it. Its counts differ from pytest's because it also checks the CLI and the suite as a whole; both views go green together when the lab is done.

### C6. One piece of Python that Lab 1 needs a day early

Lab 1 asks `run_power_flow()` to **stop loudly** when the power flow does not converge. pandapower signals non-convergence by raising its own exception, `pp.LoadflowNotConverged`; your function must catch it and re-raise it as a plain `RuntimeError` with a message a human can act on. The pattern:

```python
try:
    pp.runpp(net)                      # may raise pp.LoadflowNotConverged
except pp.LoadflowNotConverged as err:
    # re-raise as a RuntimeError; "from err" keeps the original cause visible
    raise RuntimeError("Power flow did not converge — check the input data") from err
```

Why not let `LoadflowNotConverged` escape on its own? Whoever calls your toolbox should not need to know pandapower internals to handle your errors. A function that returns nonsense quietly is worse than one that stops loudly — exception handling gets its full treatment in Lecturecise 3, the day after Lab 1, so use the pattern as given and bring your questions there.

---

## Part D — Docker, for reference only (5 min, optional)

**Nothing in Period 1 requires this, and no lab or quiz asks about it.** Read it once so you
know the option exists; come back to it in Period 2 if your project ever needs it.

A virtual environment freezes your *packages*. It does not freeze the Python version, the
operating system, or the compiled libraries underneath — and those do occasionally decide
whether numerical code produces the same answer. A container freezes all of it: the whole
machine, described in a text file, rebuilt identically anywhere.

The description lives in a file called `Dockerfile`. This one is enough for a course project:

```dockerfile
FROM python:3.11-slim
WORKDIR /work
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
CMD ["python", "pf.py"]
```

Read it as five instructions rather than as code: start from a machine that has Python 3.11 and
little else; work in `/work`; copy the recipe in and install from it; copy the project in; and
when the container starts, run this. The recipe is copied *before* the project on purpose — the
install step is then re-used unchanged whenever only your own code has changed, which is what
makes rebuilds fast.

If you have Docker Desktop installed, from your scratch folder:

```bash
docker build -t svedala .        # build the image, once per change to the recipe
docker run --rm svedala          # run pf.py inside it, then throw the container away
```

You should see the same 10 981 MW line as in A5 — this time from a machine that did not exist a
minute ago and will not exist a minute from now.

**Where this actually matters in this course:** in Period 2, if your group's results depend on a
version you cannot get everyone to install, or if the challenge partner needs to run what you
built without a call to explain it. That is the point at which a `Dockerfile` in the repository
is worth the twenty minutes. Not before.

Installing Docker Desktop is a large download and needs administrator rights, so do not do it
today unless you already have it. https://docs.docker.com/get-started/

---

## Self-check

You are done when all five are true:

1. `python --version` in a fresh terminal says 3.11+
2. You can create, activate and deactivate a venv and explain what A3 demonstrated (the failed import — or the changed module path)
3. `python pf.py` prints the 10 981 MW line
4. `git log --oneline` in your scratch folder shows your commit
5. Your course repository is cloned, its venv installed (C3), and `pytest -q` runs

The scratch folder has served its purpose — keep it or delete it. Lab 1 starts from your real course repository.

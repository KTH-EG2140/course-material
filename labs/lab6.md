# Lab 6 — From CIMXML to an hourly load series

*EG2140 · **self-paced** — do it with your lab partner during the week; your pod is first support (partner → pod → Discussions → the TA sessions) · ~110 min · host repo: the partner whose name comes LAST alphabetically in today's pair — both of you can push to it. Quiz 3 covers Lecturecises 8–9; this lab is the CIM part in practice. No AI tools.*

Lecturecise 8 read one SSH file by hand. This lab industrialises it: parse the Svedala EQ once, then turn the 168 timestamped SSH snapshots in `data/svedala-year/ssh_week.zip` into a tidy hourly **zonal** load DataFrame — the SCADA-side twin of the market data you fetched in Lab 5.

**Before you start.** Walk the LC8 notebook first: its section 2.1 is the join you industrialise here, and its section 2.2 names the three functions. Two files from the course material have to come into your workbook, because the tests must run in CI on a machine that has only your repo:

```bash
# from your workbook root, with <cm> = the path to your clone of course-material
mkdir -p data/svedala-cim
cp <cm>/data/svedala-cim/network_EQ.xml data/svedala-cim/     # 4 MB, committed - the tests need it
git add data/svedala-cim/network_EQ.xml && git commit -m "Add the Svedala EQ file for the Lab 6 zone map"
```

The week of snapshots (`ssh_week.zip`, 21 MB) stays in the course-material clone — you read it from there; section 3 makes a 3-file slice of it for the tests.

## 1. The EQ join (~30 min)

Implement `load_zone_map(eq_path, csv_dir)` in `src/svedala_toolbox/cim.py` (the stub is there; its docstring is the specification). It returns a dictionary **keyed by mRID**, value the zone — the name is only a stepping stone. The chain is mRID → name (EQ) → bus (`loads.csv`) → zone (`buses.csv`). LC8's EQ regex gives you the first step verbatim; `pd.read_csv(csv_dir / "loads.csv", index_col=0)` and the same for `buses.csv` give the other two, and a dictionary built from `loads.csv` — `{row["name"]: zone_of_bus[row["bus"]] for _, row in loads.iterrows()}` (`iterrows()` walks a table one row at a time, as `(index, row)` pairs) — is the name → zone lookup.

Two traps, both real:

- `buses.csv` has a column called `zone`. It holds the **substation** name (`AGGAN CT11`), not the zone. The `ZON_*` zone is the column `SubGeographicalRegion_name` — the one your Lab 1 loader used for `zone=`. Map through that column or every load lands in its own "zone".
- The EQ knows 73 ConformLoads; the CSVs know 60; only **55** carry the same name in both. The 18 EQ-only loads (all `ST…` stations) draw about 60 MW in the base snapshot and about 37 MW on average in the week — real power that no zone column will receive. **Decide** what to do with them and write the decision down: dropping them silently is the one wrong answer. The reference keeps them under a fifth key, `"unmapped"`, so their megawatts stay visible in the table.

Log the unmapped ones with `logging` at level `INFO` (LC3 Part B: a module asks for a logger named after itself and never configures anything — which means the line is **silent by default**; you see it only when the program that calls you switches it on, as LC3 B4 did with `logging.basicConfig(level=logging.INFO)`). On the reference solution, with INFO switched on, the line reads:

```
INFO:svedala_toolbox.cim:zone map: 55 loads mapped, 18 unmapped: ['ST13_T1_LAST', 'ST14_T1_LAST', 'ST16_T1_LAST', ...]
```

**Checkpoint:** from the repo root, with the venv active:

```bash
python -c "import logging; logging.basicConfig(level=logging.INFO); from svedala_toolbox.cim import load_zone_map; m = load_zone_map('data/svedala-cim/network_EQ.xml', 'data/svedala'); print(len([z for z in m.values() if z != 'unmapped']), 'mapped')"
```

prints the INFO line above and then `55 mapped`. Commit: `git add src/svedala_toolbox/cim.py` and a message that says what the map does.

## 2. One snapshot → one row (~25 min)

Implement `parse_ssh(source, zone_map)` returning `(timestamp, {zone: MW})`. Two things to read from the file: `Model.scenarioTime` (LC8's `scenarioTime>([^<]+)<` pattern; `pd.Timestamp("2025-01-13T00:00:00Z")` parses the string, and the `Z` makes it UTC) and every ConformLoad's `EnergyConsumer.p` (LC8's SSH pattern). Sum per zone as you go: `per_zone[zone] = per_zone.get(zone, 0.0) + float(p)` — `dict.get(key, default)` gives the running total or 0.0 the first time a zone appears.

`source` may be a path *or* the bytes `zipfile` hands you in section 3; `bytes` needs `.decode("utf-8")`, a path needs `.read_text(encoding="utf-8")` — check with `isinstance(source, bytes)`.

Regex or `ElementTree` — your call; write one sentence in the README on why. (Regex: every step visible, brittle if the file layout changes. ElementTree with namespaces: robust, more to learn.)

**Checkpoint:** `parse_ssh("<cm>/data/svedala-cim/network_SSH.xml", zone_map)` on the reference solution returns

```
(Timestamp('2021-04-21 17:30:00+0000', tz='UTC'), {'ZON_NORR': 1180, 'ZON_EXTERN': 2300, 'ZON_MITT': 6065, 'ZON_SYDVÄST': 1390, 'unmapped': 60})
```

(values rounded here). The four zones sum to 10 935 MW and the unmapped 60 MW bring it to 10 995 — Lab 1's `svedala pf` printed 10 981 from the CSVs, which hold four loads this EQ file does not. Commit.

## 3. The week (~30 min)

`assemble_series(ssh_zip, zone_map)` loops the archive into a wide DataFrame: `zipfile.ZipFile(ssh_zip)` opens it, `sorted(zf.namelist())` lists the 168 files in time order, `zf.read(name)` gives each file's bytes for `parse_ssh`; collect `{timestamp: per_zone}` and `pd.DataFrame.from_dict(rows, orient="index").sort_index()` turns it into one row per timestamp with one column per zone (`orient="index"` says the dictionary's keys are row labels, not column names). Name the index `timestamp`.

**Checkpoint** on the reference solution, `assemble_series("<cm>/data/svedala-year/ssh_week.zip", zone_map)`:

```
(168, 5) 2025-01-13 00:00:00+00:00 -> 2025-01-19 23:00:00+00:00
                           ZON_NORR  ZON_EXTERN  ZON_MITT  ZON_SYDVÄST  unmapped
timestamp
2025-01-13 00:00:00+00:00     685.0      1330.0    3939.2       1004.0      38.2
2025-01-13 01:00:00+00:00     577.2      1313.5    3948.2        978.1      37.4
```

168 hours, UTC, the five columns your policy produced (four if you dropped the unmapped loads — then say so). If your terminal hides a column behind `...`, that is pandas fitting the window, not a missing column — `pd.set_option("display.width", 200)` widens it. Plot it, the four zones only:

```python
zones = ["ZON_NORR", "ZON_MITT", "ZON_SYDVÄST", "ZON_EXTERN"]
week[zones].plot(figsize=(10, 3))
```

Then the real test — **compare your week against the course dataset**, the same seven days of `svedala_hourly.parquet`:

```python
ref = pd.read_parquet("<cm>/data/svedala-year/svedala_hourly.parquet").loc[week.index]
rel = (week[zones] - ref[zones]) / ref[zones]          # relative deviation, hour by hour, zone by zone
print((rel.mean() * 100).round(2))                     # mean deviation per zone, in percent
print(round(rel.abs().max().max() * 100, 2), "% largest single-hour deviation")
```

`.loc[week.index]` picks the reference rows at exactly your timestamps — both indexes are UTC, so they align. On the reference solution the per-zone mean deviation is 0.00 % for three zones and −0.76 % for `ZON_MITT`, the largest single-hour deviation 0.76 %, and the total over the four zones runs 0.42 % below the parquet — which is almost exactly the unmapped column: add it back and the total agrees to 0.12 %. **The residual is your unmapped loads**, and they sit in `ZON_MITT`. State the number and its explanation in your README — a comparison without a tolerance is not a comparison; start from 2 % per zone and tighten to what you measured.

**Tests** — two, in `tests/test_cim.py` (replace the two placeholders, keep the function names): the zone map covers at least 55 loads, and `assemble_series` on a small zip gives the right shape. CI must stay fast, so the test reads a **3-file mini-zip** you build once from the week and commit under `tests/data/` — create that folder first (`mkdir -p tests/data`; the template does not have it), then in a scratch cell or a one-off script:

```python
import zipfile
src = zipfile.ZipFile("<cm>/data/svedala-year/ssh_week.zip")
with zipfile.ZipFile("tests/data/ssh_mini.zip", "w", zipfile.ZIP_DEFLATED) as z:
    for name in sorted(src.namelist())[:3]:      # the first three hours of the week
        z.writestr(name, src.read(name))
```

(`writestr` writes bytes into the new archive under the given name; `ZIP_DEFLATED` compresses — about 380 kB for three files.) Paths inside the tests come from `__file__`, as in Lab 5: `Path(__file__).parent / "data" / "ssh_mini.zip"` for the zip, and `Path(__file__).resolve().parents[1] / "data" / "svedala-cim" / "network_EQ.xml"` for the EQ file you committed — `parents[1]` is two folders up from the test file, `tests/` then the repo root, the same idea as the loader's `parents[2]`. The shape test asserts three rows (`len(df) == 3`), a UTC index (`str(df.index.tz) == "UTC"`), and the four `ZON_*` columns present (`{"ZON_NORR", ...} <= set(df.columns)` — *is a subset of*).

**Checkpoint:** `pytest tests/test_cim.py -q` → `2 passed`; `pytest -q` → Lab 5's count plus two (`12 passed, 3 skipped` on the reference solution, which has Labs 1–5 done). Commit `cim.py`, the tests, the mini-zip and the README paragraph; push; CI green.

## 4. Pod check (15 min)

The other pair reads your `cim.py`, your unmapped policy and your comparison argument. Three sentences as an Issue in their host repo (**Issues** tab → **New issue**), titled "Lab 6 pod check": one thing done well, one improvement, one question — at least one about the comparison, not the code. Nothing handed in, nothing graded.

## Done when

`assemble_series` tested on the mini-zip, the comparison number and its explanation in the README, pod check exchanged — before the Quiz 3 sitting.

# Lab 6 — From CIMXML to an hourly load series

*EG2140 · **self-paced** — with your lab partner during the week; pod as first support · ~110 min · host repo: alternate. Quiz 3 covers Lecturecises 8–10; this lab is the CIM part in practice. No AI tools.*

Lecturecise 8 read one SSH file by hand. This lab industrialises it: parse the Svedala EQ once, then turn the 168 timestamped SSH snapshots in `data/svedala-year/ssh_week.zip` into a tidy hourly **zonal** load DataFrame — the SCADA-side twin of the market data you fetched in Lab 5.

## 1. The EQ join (~30 min)
Implement `load_zone_map(eq_path, csv_dir)` in `cim.py` (stub provided): ConformLoad mRID → name (EQ) → bus → zone (the CSVs). Sanity: ≥ 55 of the ~60 CSV loads must map; log the ones that do not and **decide** what to do with SSH loads absent from the CSVs (drop? bucket as "unmapped"? — document the choice).

## 2. One snapshot → one row (~25 min)
Implement `parse_ssh(path_or_bytes, zone_map)` returning `(timestamp, {zone: MW})` from `Model.scenarioTime` and the ConformLoad P values. Regex or `ElementTree` — your call; write down why.

## 3. The week (~30 min)
`assemble_series(ssh_zip)` loops the archive into a wide DataFrame (UTC index, one column per zone). Plot it. Then the real test: **compare your week against the course dataset** (`svedala_hourly.parquet`, same week). Within what tolerance do they agree, and what explains the residual? (Hint: your unmapped loads.) Put the number in your README.

## 4. Pod check (15 min)
Three sentences in the other pair's repo ("Lab 6 pod check") on their series and their comparison argument. Nothing handed in, nothing graded.

## Done when
`assemble_series` tested (a 3-file mini-zip under `tests/data/` keeps CI fast), the comparison number argued in the README, pod check exchanged — before the Quiz 3 sitting.

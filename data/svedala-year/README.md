# Svedala hourly year (D6)

One year of hourly zonal load on the Svedala grid, with temperature covariates.

**Source:** SYNTHETIC PROXY — replace via fetch_entsoe.py. Areas mapped SE1+SE2→NORR, SE3→MITT, SE4→SYDVÄST,
FI→EXTERN; each zone scaled so its mean equals the Svedala base-case zone load
× k=0.52, where k is calibrated by AC N-1 screening so that
~23% of hours are N-1 insecure — the year deliberately straddles
the security boundary.

**Columns:** `ZON_*` (MW), `total_mw`, `temp_north/mid/south` (°C, zone anchor
sites Luleå/Stockholm/Malmö). Timestamps UTC.

Used by: Lab 6 (SSH assembly — see `ssh_week/`), Lab 7 (SARIMA), Lab 8
(security labels come from YOUR screener, not this file), Lab 9 (forecast
comparison with temperature covariate), LC9 (OPF cases).


## Two regimes, on purpose

The Svedala CGMES snapshot (the CSVs, 10 981 MW) is a **stressed planning
case** — it violates the N-1 criterion by design, the way planning cases are
deliberately loaded to the edge. This dataset is the **operational history**:
a year that runs *below* the design case (mean ≈ 5.7 GW) and crosses the
security boundary only in its heavier hours. Comparing the two is not an
inconsistency to hide but the industry's normal state of affairs — and the
distance between them is exactly what Lecturecise 9's optimisation quantifies.

Regenerate: `tooling/d6/` — fetch_entsoe.py → build_dataset.py → generate_ssh.py.

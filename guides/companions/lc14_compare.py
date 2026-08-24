"""LC14 A/B experiment — score a generated screener against the acceptance criteria.

Usage, from your workbook root (the folder with src/ and tests/):

    python lc14/lc14_compare.py lc14/condition_b.py

The candidate file must define screen_n1(net, loading_limit=100.0). The script
runs it on the Svedala network and prints one verdict line per acceptance
criterion — the same criteria as the Part B specification. Read the code and
predict the verdicts BEFORE you run this; the script only checks your judgment.
"""
import importlib.util
import sys
from pathlib import Path

import pandas as pd

# The oracle from Lab 2 — looked up relative to where you RUN the script
# (your workbook root), with the course-material location as fallback.
ORACLE_CANDIDATES = [Path("tests/data/n1_reference_results.csv"),
                     Path("../labs/n1_reference_results.csv")]


def load_candidate(path):
    """Import the generated file by path, wherever it lives."""
    spec = importlib.util.spec_from_file_location("candidate", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)   # runs the file — top-level code runs too!
    if not hasattr(module, "screen_n1"):
        sys.exit(f"FAIL  {path} defines no screen_n1 function — condition A often "
                 "invents its own name; that is itself a finding, note it.")
    return module.screen_n1


def verdict(ok, text):
    print(("PASS  " if ok else "FAIL  ") + text)
    return ok


def main():
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    screen_n1 = load_candidate(sys.argv[1])

    # Your own Lab 1 loader builds the network — the candidate only screens it.
    from svedala_toolbox.loader import load_svedala
    net = load_svedala()
    in_service_before = net.line.in_service.copy()

    try:
        result = screen_n1(net)
    except TypeError:
        # Some generations demand extra arguments — also a finding.
        sys.exit("FAIL  screen_n1(net) not callable with a network alone — "
                 "check its signature against the specification.")

    ok = True
    # 1. Restoration: the network is unchanged after the run, whatever happened.
    ok &= verdict(net.line.in_service.equals(in_service_before),
                  "restoration — every line back in service after the run")
    # 2. Shape: a DataFrame with exactly the promised columns.
    want = ["outage_idx", "outage_line", "status", "max_loading_percent", "n_violations"]
    is_df = isinstance(result, pd.DataFrame)
    ok &= verdict(is_df and list(result.columns) == want,
                  f"output shape — DataFrame with columns {want}")
    if not is_df:
        sys.exit("      (cannot check further without a DataFrame)")
    # 3. Coverage: one row per in-service line.
    n_lines = int(in_service_before.sum())
    ok &= verdict(len(result) == n_lines,
                  f"coverage — {len(result)} rows for {n_lines} in-service lines")
    # 4. The oracle: loadings within 1e-3, violation counts exact.
    oracle_path = next((p for p in ORACLE_CANDIDATES if p.exists()), None)
    if oracle_path is None:
        print("SKIP  oracle — n1_reference_results.csv not found (run from your "
              "workbook root, or copy it next to this script)")
    else:
        oracle = pd.read_csv(oracle_path)
        # Join on the outage line NAME — robust against row-order differences.
        merged = oracle.merge(result, on="outage_line", suffixes=("_ref", ""))
        close = (merged["max_loading_percent"]
                 .sub(merged["max_loading_percent_ref"]).abs() < 1e-3)
        counts = merged["n_violations"] == merged["n_violations_ref"]
        ok &= verdict(len(merged) == len(oracle) and bool(close.all()),
                      f"oracle loadings — within 1e-3 on {int(close.sum())}/{len(oracle)} rows")
        ok &= verdict(bool(counts.all()),
                      f"oracle violation counts — exact on {int(counts.sum())}/{len(oracle)} rows")

    # ---- Second pass: the stressed grid, where the failure paths actually run.
    # On the BASE case all outages converge, so restore-on-failure and silent
    # skipping never get exercised (Lab 2's own tests share this blind spot).
    # At scaling 1.05 a good number of contingencies fail to converge - that is
    # where a "restores only on success" bug or a bare except shows itself.
    print()
    print("--- stressed case (load scaling 1.05) ---")
    net = load_svedala()
    net.load["scaling"] = 1.05
    in_service_before = net.line.in_service.copy()
    result = screen_n1(net)
    ok &= verdict(net.line.in_service.equals(in_service_before),
                  "stressed restoration — lines restored even when the solve fails")
    ok &= verdict(len(result) == n_lines,
                  f"stressed coverage — {len(result)} rows for {n_lines} contingencies "
                  "(fewer means failures were silently skipped)")
    # A reported failure = a NaN loading, or a status that names the failure.
    # (Counting every status != "converged" would credit candidates that just
    # call success something else.)
    reported = 0
    cols = getattr(result, "columns", [])
    if "max_loading_percent" in cols:
        reported = int(result["max_loading_percent"].isna().sum())
    if "status" in cols:
        named = result["status"].astype(str).str.lower().str.contains(
            "not_conv|no_conv|fail|diverg|error").sum()
        reported = max(reported, int(named))
    ok &= verdict(reported >= 1,
                  f"stressed reporting — {reported} non-converging case(s) reported "
                  "as such (this grid has them; zero reported means they were hidden)")

    print()
    print("Specification met." if ok else
          "Specification NOT met — now say which prompt produced this, and why.")


if __name__ == "__main__":
    main()

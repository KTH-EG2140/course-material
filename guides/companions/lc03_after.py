"""Zone load report — the refactored version (LC3 live refactor, end state)."""
from pathlib import Path

import pandas as pd

DATA_DIR = Path("data/svedala")


def zone_load_totals(scaling: float = 1.0, data_dir: Path = DATA_DIR) -> pd.Series:
    """Total active load per zone, in MW, optionally scaled.

    Raises FileNotFoundError if the Svedala CSVs are not where expected,
    and KeyError if a load references a bus that does not exist — both
    are errors we want to SEE, not skip.
    """
    if scaling <= 0:
        raise ValueError(f"scaling must be positive, got {scaling}")
    data_dir = Path(data_dir)   # accept plain strings too — normalise at the boundary
    loads = pd.read_csv(data_dir / "loads.csv", index_col=0)
    buses = pd.read_csv(data_dir / "buses.csv", index_col=0)
    zones = loads["bus"].map(buses["SubGeographicalRegion_name"])
    if zones.isna().any():
        missing = loads.loc[zones.isna(), "bus"].tolist()
        raise KeyError(f"loads reference buses without a zone: {missing}")
    return (loads["p_mw"] * scaling).groupby(zones).sum()


if __name__ == "__main__":
    print(zone_load_totals().round(0))

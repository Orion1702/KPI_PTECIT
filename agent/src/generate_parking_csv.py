"""Generate synthetic parking.csv for tests (run from agent/src: python generate_parking_csv.py)."""
import csv
import random
from pathlib import Path
from typing import Optional, Union


def generate_parking_csv(
    path: Optional[Union[str, Path]] = None,
    num_rows: Optional[int] = None,
    seed: Optional[int] = 42,
) -> Path:
    if path is None:
        path = Path(__file__).resolve().parent / "data" / "parking.csv"
    else:
        path = Path(path)

    if num_rows is None:
        num_rows = random.randint(20, 30)
    if seed is not None:
        random.seed(seed)

    path.parent.mkdir(parents=True, exist_ok=True)

    base_lat, base_lon = 50.45, 30.52
    with path.open("w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["empty_count", "longitude", "latitude"])
        for _ in range(num_rows):
            empty = random.randint(0, 50)
            lon = base_lon + random.uniform(-0.05, 0.05)
            lat = base_lat + random.uniform(-0.05, 0.05)
            w.writerow([empty, f"{lon:.14f}", f"{lat:.14f}"])

    return path


if __name__ == "__main__":
    generate_parking_csv(num_rows=25, seed=42)
    print("Wrote data/parking.csv")

from __future__ import annotations

from pathlib import Path
from typing import List, Tuple


def parse_location_file(path: str) -> List[Tuple[float, float]]:
    points = []
    for row in Path(path).read_text().splitlines():
        row = row.strip().replace("−", "-")
        if not row:
            continue
        if "," in row:
            parts = [p.strip() for p in row.split(",")]
        else:
            parts = row.split()
        if len(parts) < 2:
            continue
        try:
            points.append((float(parts[0]), float(parts[1])))
        except ValueError:
            continue
    return points

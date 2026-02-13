from __future__ import annotations

from pathlib import Path
from typing import List, Tuple


def parse_location_file(path: str) -> List[Tuple[float, float]]:
    text = Path(path).read_text().strip().splitlines()
    if not text:
        return []
    rows = [line.strip() for line in text[1:] if line.strip()]
    points = []
    for row in rows:
        row = row.replace("−", "-")
        parts = [p.strip() for p in row.split(",")]
        if len(parts) < 2:
            continue
        points.append((float(parts[0]), float(parts[1])))
    return points

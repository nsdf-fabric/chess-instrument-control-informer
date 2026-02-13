from __future__ import annotations

from dataclasses import dataclass, replace
from pathlib import Path
from typing import Iterable, Optional, Tuple

import yaml


@dataclass(frozen=True)
class Config:
    full_file: str
    new_file: str
    entry: str
    detector_ids: Tuple[str, ...]
    fit: str
    hkls: Tuple[str, ...]
    data_group: str = "centers"
    dataset_names: Tuple[str, str, str] = ("labx", "labz", "values")
    loc_dir: Optional[str] = None
    initial_points: Optional[Tuple[Tuple[float, float], ...]] = None
    initial_count: Optional[int] = None
    seed: Optional[int] = None


def load_config(path: str) -> Config:
    data = yaml.safe_load(Path(path).read_text()) or {}
    return _config_from_dict(data)


def _config_from_dict(data: dict) -> Config:
    return Config(
        full_file=str(data["full_file"]),
        new_file=str(data["new_file"]),
        entry=str(data["entry"]),
        detector_ids=tuple(str(x) for x in data["detector_ids"]),
        fit=str(data["fit"]),
        hkls=tuple(str(x) for x in data["hkls"]),
        data_group=str(data.get("data_group", "centers")),
        dataset_names=tuple(data.get("dataset_names", ("labx", "labz", "values"))),
        loc_dir=data.get("loc_dir"),
        initial_points=_normalize_points(data.get("initial_points")),
        initial_count=data.get("initial_count"),
        seed=data.get("seed"),
    )


def merge_config(base: Config, **overrides) -> Config:
    filtered = {k: v for k, v in overrides.items() if v is not None}
    if "detector_ids" in filtered:
        filtered["detector_ids"] = tuple(str(x) for x in filtered["detector_ids"])
    if "hkls" in filtered:
        filtered["hkls"] = tuple(str(x) for x in filtered["hkls"])
    if "dataset_names" in filtered:
        filtered["dataset_names"] = tuple(filtered["dataset_names"])
    if "initial_points" in filtered:
        filtered["initial_points"] = _normalize_points(filtered["initial_points"])
    return replace(base, **filtered)


def _normalize_points(
    points: Optional[Iterable[Iterable[float]]],
) -> Optional[Tuple[Tuple[float, float], ...]]:
    if points is None:
        return None
    return tuple((float(x), float(y)) for x, y in points)

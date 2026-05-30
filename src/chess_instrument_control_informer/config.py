from __future__ import annotations

from dataclasses import dataclass, replace
from pathlib import Path
from typing import Iterable, Literal, Optional, Tuple

import yaml


@dataclass(frozen=True)
class Config:
    full_file: str
    new_file: str
    entry: Optional[str] = None
    detector_ids: Tuple[str, ...] = ()
    fit: Optional[str] = None
    hkls: Tuple[str, ...] = ()
    data_group: str = "centers"
    dataset_names: Tuple[str, str, str] = ("labx", "labz", "values")
    loc_dir: Optional[str] = None
    initial_points: Optional[Tuple[Tuple[float, float], ...]] = None
    initial_count: Optional[int] = None
    seed: Optional[int] = None
    source_format: Literal["hdf5", "json"] = "hdf5"
    labx_key: str = "labx"
    labz_key: str = "labz"
    copy_all_json_keys: bool = True
    measurement_delay_seconds: float = 0.0


def load_config(path: str) -> Config:
    data = yaml.safe_load(Path(path).read_text()) or {}
    return _config_from_dict(data)


def _config_from_dict(data: dict) -> Config:
    source_format = str(data.get("source_format", "hdf5"))
    if source_format not in ("hdf5", "json"):
        raise ValueError(f"Unsupported source_format: {source_format}")
    return Config(
        full_file=str(data["full_file"]),
        new_file=str(data["new_file"]),
        entry=_optional_str(data.get("entry")),
        detector_ids=tuple(str(x) for x in data.get("detector_ids", ())),
        fit=_optional_str(data.get("fit")),
        hkls=tuple(str(x) for x in data.get("hkls", ())),
        data_group=str(data.get("data_group", "centers")),
        dataset_names=tuple(data.get("dataset_names", ("labx", "labz", "values"))),
        loc_dir=data.get("loc_dir"),
        initial_points=_normalize_points(data.get("initial_points")),
        initial_count=data.get("initial_count"),
        seed=data.get("seed"),
        source_format=source_format,
        labx_key=str(data.get("labx_key", "labx")),
        labz_key=str(data.get("labz_key", "labz")),
        copy_all_json_keys=bool(data.get("copy_all_json_keys", True)),
        measurement_delay_seconds=float(data.get("measurement_delay_seconds", 0.0)),
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
    if "source_format" in filtered:
        source_format = str(filtered["source_format"])
        if source_format not in ("hdf5", "json"):
            raise ValueError(f"Unsupported source_format: {source_format}")
        filtered["source_format"] = source_format
    return replace(base, **filtered)


def _optional_str(value: Optional[object]) -> Optional[str]:
    if value is None:
        return None
    return str(value)


def _normalize_points(
    points: Optional[Iterable[Iterable[float]]],
) -> Optional[Tuple[Tuple[float, float], ...]]:
    if points is None:
        return None
    return tuple((float(x), float(y)) for x, y in points)

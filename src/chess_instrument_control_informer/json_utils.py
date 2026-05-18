from __future__ import annotations

import copy
import json
import os
import tempfile
from pathlib import Path
from typing import Iterable, Tuple

import numpy as np


def load_json(path: str) -> dict:
    with Path(path).open(encoding="utf-8") as f:
        data = json.load(f)
    if not isinstance(data, dict):
        raise ValueError(f"JSON file must contain an object: {path}")
    return data


def atomic_write_json(path: str, data: dict) -> None:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp_name = tempfile.mkstemp(
        prefix=f".{target.name}.",
        suffix=".tmp",
        dir=str(target.parent),
        text=True,
    )
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            json.dump(data, f, allow_nan=True)
            f.flush()
            os.fsync(f.fileno())
        os.replace(tmp_name, target)
    except Exception:
        try:
            os.unlink(tmp_name)
        except FileNotFoundError:
            pass
        raise


def clone_json_without_data(
    *,
    full_path: str,
    new_path: str,
    labx_key: str = "labx",
    labz_key: str = "labz",
    copy_all_json_keys: bool = True,
) -> None:
    full = load_json(full_path)
    _validate_coordinate_lists(full, labx_key, labz_key)

    new = {}
    for key, value in full.items():
        if isinstance(value, list):
            if copy_all_json_keys or key in (labx_key, labz_key):
                new[key] = []
        else:
            new[key] = copy.deepcopy(value)

    new.setdefault(labx_key, [])
    new.setdefault(labz_key, [])
    atomic_write_json(new_path, new)


def read_json_points(
    *,
    full_path: str,
    labx_key: str = "labx",
    labz_key: str = "labz",
) -> Tuple[np.ndarray, np.ndarray]:
    full = load_json(full_path)
    labx, labz = _validate_coordinate_lists(full, labx_key, labz_key)
    return np.asarray(labx, dtype=float), np.asarray(labz, dtype=float)


def nearest_json_row(
    labx: np.ndarray,
    labz: np.ndarray,
    target_x: float,
    target_z: float,
) -> int:
    if labx.size == 0:
        raise ValueError("Cannot find nearest JSON row because coordinate arrays are empty")
    distances = (labx - target_x) ** 2 + (labz - target_z) ** 2
    return int(np.argmin(distances))


def append_interpolated_json_points(
    *,
    full_path: str,
    new_path: str,
    points: Iterable[Tuple[float, float]],
    labx_key: str = "labx",
    labz_key: str = "labz",
    copy_all_json_keys: bool = True,
) -> None:
    full = load_json(full_path)
    new = load_json(new_path)
    full_labx, full_labz = read_json_points(
        full_path=full_path,
        labx_key=labx_key,
        labz_key=labz_key,
    )
    _validate_output_coordinate_lists(new, labx_key, labz_key)

    list_keys = [
        key
        for key, value in full.items()
        if isinstance(value, list) and (copy_all_json_keys or key in new)
    ]
    for key in list_keys:
        new.setdefault(key, [])
        if not isinstance(new[key], list):
            raise ValueError(f"JSON output key must contain a list: {key}")

    for labx, labz in points:
        nearest = nearest_json_row(full_labx, full_labz, float(labx), float(labz))
        for key in list_keys:
            if key == labx_key:
                new[key].append(float(labx))
            elif key == labz_key:
                new[key].append(float(labz))
            else:
                source = full[key]
                if nearest < len(source):
                    new[key].append(copy.deepcopy(source[nearest]))
                else:
                    new[key].append(float("nan"))

    atomic_write_json(new_path, new)


def _validate_coordinate_lists(data: dict, labx_key: str, labz_key: str) -> Tuple[list, list]:
    missing = [key for key in (labx_key, labz_key) if key not in data]
    if missing:
        raise ValueError(f"JSON coordinate key(s) missing: {', '.join(missing)}")
    labx = data[labx_key]
    labz = data[labz_key]
    if not isinstance(labx, list) or not isinstance(labz, list):
        raise ValueError(f"JSON coordinate keys must contain lists: {labx_key}, {labz_key}")
    if len(labx) != len(labz):
        raise ValueError(
            f"JSON coordinate lists must have the same length: "
            f"{labx_key}={len(labx)}, {labz_key}={len(labz)}"
        )
    return labx, labz


def _validate_output_coordinate_lists(data: dict, labx_key: str, labz_key: str) -> None:
    for key in (labx_key, labz_key):
        if key not in data:
            data[key] = []
        if not isinstance(data[key], list):
            raise ValueError(f"JSON output coordinate key must contain a list: {key}")

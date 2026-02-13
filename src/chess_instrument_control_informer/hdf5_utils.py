from __future__ import annotations

from pathlib import Path
from typing import Iterable, Sequence, Tuple

import h5py
import numpy as np


def clone_without_data(
    *,
    full_path: str,
    new_path: str,
    entry: str,
    detector_ids: Sequence[str],
    fit: str,
    hkls: Sequence[str],
    data_group: str,
    dataset_names: Tuple[str, str, str],
) -> None:
    # Ensure parent directory exists
    Path(new_path).parent.mkdir(parents=True, exist_ok=True)

    with h5py.File(full_path, "r") as full, h5py.File(new_path, "w") as new:
        _copy_group(full["/"], new["/"])
        for detector_id in detector_ids:
            for hkl in hkls:
                centers_path = f"{entry}/{detector_id}/{fit}/{hkl}/{data_group}"
                if centers_path not in new:
                    continue
                centers = new[centers_path]
                for name in dataset_names:
                    if name in centers:
                        ds = centers[name]
                        dtype = ds.dtype
                        del centers[name]
                        centers.create_dataset(
                            name,
                            shape=(0,),
                            maxshape=(None,),
                            dtype=dtype,
                        )


def append_interpolated_points(
    *,
    full_path: str,
    new_path: str,
    entry: str,
    detector_ids: Sequence[str],
    fit: str,
    hkls: Sequence[str],
    data_group: str,
    dataset_names: Tuple[str, str, str],
    points: Iterable[Tuple[float, float]],
) -> None:
    with h5py.File(full_path, "r") as full, h5py.File(new_path, "r+") as new:
        for detector_id in detector_ids:
            for hkl in hkls:
                centers_path = f"{entry}/{detector_id}/{fit}/{hkl}/{data_group}"
                if centers_path not in full or centers_path not in new:
                    continue
                full_centers = full[centers_path]
                new_centers = new[centers_path]
                full_labx = np.asarray(full_centers[dataset_names[0]][:])
                full_labz = np.asarray(full_centers[dataset_names[1]][:])
                full_values = np.asarray(full_centers[dataset_names[2]][:])
                for labx, labz in points:
                    value = _nearest_value(full_labx, full_labz, full_values, labx, labz)
                    _append_to_dataset(new_centers[dataset_names[0]], labx)
                    _append_to_dataset(new_centers[dataset_names[1]], labz)
                    _append_to_dataset(new_centers[dataset_names[2]], value)


def read_points(
    *,
    full_path: str,
    entry: str,
    detector_id: str,
    fit: str,
    hkl: str,
    data_group: str,
    dataset_names: Tuple[str, str, str],
) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    with h5py.File(full_path, "r") as full:
        centers = full[f"{entry}/{detector_id}/{fit}/{hkl}/{data_group}"]
        return (
            np.asarray(centers[dataset_names[0]][:]),
            np.asarray(centers[dataset_names[1]][:]),
            np.asarray(centers[dataset_names[2]][:]),
        )


def _append_to_dataset(dataset: h5py.Dataset, value: float) -> None:
    current = dataset.shape[0]
    dataset.resize((current + 1,))
    dataset[current] = value


def _nearest_value(
    labx: np.ndarray,
    labz: np.ndarray,
    values: np.ndarray,
    target_x: float,
    target_z: float,
) -> float:
    if labx.size == 0:
        return float("nan")
    distances = (labx - target_x) ** 2 + (labz - target_z) ** 2
    idx = int(np.argmin(distances))
    return float(values[idx])


def _copy_group(src: h5py.Group, dst: h5py.Group) -> None:
    for key, value in src.attrs.items():
        dst.attrs[key] = value
    for name, item in src.items():
        if isinstance(item, h5py.Dataset):
            src.copy(item, dst, name=name)
        else:
            group = dst.require_group(name)
            _copy_group(item, group)

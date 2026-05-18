from __future__ import annotations

from typing import Iterable, List, Optional, Sequence, Tuple

import numpy as np

from .hdf5_utils import read_points
from .json_utils import read_json_points


def select_initial_points(
    *,
    full_path: str,
    entry: Optional[str],
    detector_ids: Sequence[str],
    fit: Optional[str],
    hkls: Sequence[str],
    data_group: str,
    dataset_names: Tuple[str, str, str],
    initial_points: Optional[Iterable[Tuple[float, float]]],
    initial_count: Optional[int],
    source_format: str = "hdf5",
    labx_key: str = "labx",
    labz_key: str = "labz",
    seed: Optional[int] = None,
) -> List[Tuple[float, float]]:
    if initial_points is not None:
        return [(float(x), float(y)) for x, y in initial_points]
    if not initial_count:
        return []

    if source_format == "json":
        labx, labz = read_json_points(
            full_path=full_path,
            labx_key=labx_key,
            labz_key=labz_key,
        )
    elif source_format == "hdf5":
        if entry is None or fit is None or not detector_ids or not hkls:
            raise ValueError("HDF5 sampling requires entry, detector_ids, fit, and hkls")
        detector_id = detector_ids[0]
        hkl = hkls[0]
        labx, labz, _ = read_points(
            full_path=full_path,
            entry=entry,
            detector_id=detector_id,
            fit=fit,
            hkl=hkl,
            data_group=data_group,
            dataset_names=dataset_names,
        )
    else:
        raise ValueError(f"Unsupported source_format: {source_format}")

    rng = np.random.default_rng(seed)
    count = min(initial_count, labx.size)
    idx = rng.choice(labx.size, size=count, replace=False)
    return [(float(labx[i]), float(labz[i])) for i in idx]

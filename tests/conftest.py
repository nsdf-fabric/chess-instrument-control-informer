"""Pytest fixtures for chess-instrument-control-informer tests."""

import json

import h5py
import numpy as np
import pytest


@pytest.fixture
def simple_full_file(tmp_path):
    """Create a simple HDF5 file with minimal structure for basic tests.

    Structure: entry/0/uniform_fit/2_2_0/centers with 3 data points.
    """
    path = tmp_path / "simple_full.nxs"
    with h5py.File(path, "w") as f:
        centers = f.create_group("entry/0/uniform_fit/2_2_0/centers")
        centers.create_dataset("labx", data=np.array([0.0, 1.0, 2.0], dtype=np.float64))
        centers.create_dataset("labz", data=np.array([0.0, 1.0, 2.0], dtype=np.float64))
        centers.create_dataset("values", data=np.array([10.0, 20.0, 30.0], dtype=np.float64))
    return path


@pytest.fixture
def simple_full_file_with_metadata(tmp_path):
    """Create a simple HDF5 file with metadata for testing selective cloning.

    Structure: entry/0/uniform_fit/2_2_0/centers with 2 data points + metadata.
    """
    path = tmp_path / "simple_full_with_meta.nxs"
    with h5py.File(path, "w") as f:
        entry = f.create_group("entry")
        det = entry.create_group("0")
        fit = det.create_group("uniform_fit")
        hkl = fit.create_group("2_2_0")
        centers = hkl.create_group("centers")
        centers.create_dataset("labx", data=np.array([0.0, 1.0], dtype=np.float64))
        centers.create_dataset("labz", data=np.array([0.0, 1.0], dtype=np.float64))
        centers.create_dataset("values", data=np.array([10.0, 20.0], dtype=np.float64))
        hkl.create_dataset("meta", data=np.array([1, 2, 3], dtype=np.int32))
    return path


@pytest.fixture
def realistic_full_file(tmp_path):
    """Create an HDF5 file with structure matching strain_map.nxs.

    Structure: v8-p3-10s-0deg_dataset1_strainanalysis with multiple detectors,
    fits, and HKLs, each with 100 data points.
    """
    path = tmp_path / "realistic_full.nxs"
    with h5py.File(path, "w") as f:
        # Create entry group
        entry = f.create_group("v8-p3-10s-0deg_dataset1_strainanalysis")

        # Create detector groups
        for det_id in ["0", "10", "2"]:
            det = entry.create_group(det_id)

            # Create fit groups
            for fit_type in ["uniform_fit", "unconstrained_fit"]:
                fit = det.create_group(fit_type)

                # Create HKL groups
                for hkl in ["2_2_0", "2_2_2", "4_0_0"]:
                    hkl_group = fit.create_group(hkl)

                    # Create centers group with datasets
                    centers = hkl_group.create_group("centers")
                    centers.create_dataset("labx", data=np.linspace(-50, 50, 100), dtype=np.float64)
                    centers.create_dataset(
                        "labz", data=np.linspace(-250, -200, 100), dtype=np.float64
                    )
                    centers.create_dataset(
                        "values", data=np.random.rand(100) * 100, dtype=np.float64
                    )
    return path


@pytest.fixture
def empty_new_file(tmp_path):
    """Create an empty HDF5 file with resizable datasets for appending.

    Structure: entry/0/uniform_fit/2_2_0/centers with empty datasets.
    """
    path = tmp_path / "empty_new.nxs"
    with h5py.File(path, "w") as f:
        centers = f.create_group("entry/0/uniform_fit/2_2_0/centers")
        centers.create_dataset("labx", shape=(0,), maxshape=(None,), dtype=np.float64)
        centers.create_dataset("labz", shape=(0,), maxshape=(None,), dtype=np.float64)
        centers.create_dataset("values", shape=(0,), maxshape=(None,), dtype=np.float64)
    return path


@pytest.fixture
def simple_full_json(tmp_path):
    """Create a flat reduced JSON file with CHESS-like list-valued result keys."""
    path = tmp_path / "full_reduced_data.json"
    data = {
        "labx": [1.0, 2.0, 3.0],
        "labz": [10.0, 20.0, 30.0],
        "0/data/norm": [100.0, 200.0, 300.0],
        "0/data/uniform_strain": [0.1, float("nan"), 0.3],
        "0/uniform_fit/results/success": [True, False, True],
        "0/uniform_fit/results/included_peaks": [
            [True, False],
            [False, True],
            [True, True],
        ],
        "0/uniform_fit/4_4_0/centers/values": [114.1, float("nan"), 114.3],
        "short_values": [1.0],
        "metadata": {"example": True},
    }
    path.write_text(json.dumps(data, allow_nan=True), encoding="utf-8")
    return path

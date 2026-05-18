import json
import math

import numpy as np
import pytest

from chess_instrument_control_informer.json_utils import (
    append_interpolated_json_points,
    clone_json_without_data,
    load_json,
    nearest_json_row,
    read_json_points,
)


def test_clone_json_without_data_copies_structure_and_metadata(tmp_path, simple_full_json):
    new_path = tmp_path / "new_reduced_data.json"

    clone_json_without_data(full_path=str(simple_full_json), new_path=str(new_path))

    full = load_json(str(simple_full_json))
    new = load_json(str(new_path))
    for key, value in full.items():
        if isinstance(value, list):
            assert key in new
            assert new[key] == []
        else:
            assert new[key] == value


def test_append_interpolated_json_points_uses_requested_coords_and_nearest_values(
    tmp_path,
    simple_full_json,
):
    new_path = tmp_path / "new_reduced_data.json"
    clone_json_without_data(full_path=str(simple_full_json), new_path=str(new_path))

    append_interpolated_json_points(
        full_path=str(simple_full_json),
        new_path=str(new_path),
        points=[(2.1, 20.1)],
    )

    data = load_json(str(new_path))
    assert data["labx"] == [2.1]
    assert data["labz"] == [20.1]
    assert data["0/data/norm"] == [200.0]
    assert data["0/uniform_fit/results/success"] == [False]
    assert data["0/uniform_fit/results/included_peaks"] == [[False, True]]
    assert math.isnan(data["0/data/uniform_strain"][0])


def test_append_interpolated_json_points_appends_multiple_rows_and_short_lists(
    tmp_path,
    simple_full_json,
):
    new_path = tmp_path / "new_reduced_data.json"
    clone_json_without_data(full_path=str(simple_full_json), new_path=str(new_path))

    append_interpolated_json_points(
        full_path=str(simple_full_json),
        new_path=str(new_path),
        points=[(1.0, 10.0), (3.0, 30.0)],
    )

    data = load_json(str(new_path))
    list_lengths = {len(value) for value in data.values() if isinstance(value, list)}
    assert list_lengths == {2}
    assert data["0/data/norm"] == [100.0, 300.0]
    assert data["short_values"][0] == 1.0
    assert math.isnan(data["short_values"][1])


def test_json_helpers_validate_coordinates(tmp_path):
    path = tmp_path / "bad.json"
    path.write_text(json.dumps({"labx": [1.0], "labz": "not-list"}), encoding="utf-8")

    with pytest.raises(ValueError, match="coordinate keys must contain lists"):
        read_json_points(full_path=str(path))


def test_nearest_json_row_rejects_empty_coordinates():
    with pytest.raises(ValueError, match="coordinate arrays are empty"):
        nearest_json_row(
            labx=np.asarray([]),
            labz=np.asarray([]),
            target_x=1.0,
            target_z=1.0,
        )

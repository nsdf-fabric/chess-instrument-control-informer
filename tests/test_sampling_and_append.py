import h5py

from chess_instrument_control_informer.json_utils import read_json_points
from chess_instrument_control_informer.hdf5_utils import append_interpolated_points
from chess_instrument_control_informer.sampling import select_initial_points


def test_append_interpolated_points(tmp_path, simple_full_file, empty_new_file):
    append_interpolated_points(
        full_path=str(simple_full_file),
        new_path=str(empty_new_file),
        entry="entry",
        detector_ids=["0"],
        fit="uniform_fit",
        hkls=["2_2_0"],
        data_group="centers",
        dataset_names=("labx", "labz", "values"),
        points=[(0.9, 0.9)],
    )

    with h5py.File(empty_new_file, "r") as f:
        centers = f["entry/0/uniform_fit/2_2_0/centers"]
        assert centers["labx"][:].tolist() == [0.9]
        assert centers["labz"][:].tolist() == [0.9]
        assert centers["values"][:].tolist() == [20.0]


def test_select_initial_points_count(simple_full_file):
    points = select_initial_points(
        full_path=str(simple_full_file),
        entry="entry",
        detector_ids=["0"],
        fit="uniform_fit",
        hkls=["2_2_0"],
        data_group="centers",
        dataset_names=("labx", "labz", "values"),
        initial_points=None,
        initial_count=2,
        seed=123,
    )

    assert len(points) == 2
    assert all(len(p) == 2 for p in points)


def test_select_initial_points_json_count(simple_full_json):
    points = select_initial_points(
        full_path=str(simple_full_json),
        entry=None,
        detector_ids=(),
        fit=None,
        hkls=(),
        data_group="centers",
        dataset_names=("labx", "labz", "values"),
        source_format="json",
        labx_key="labx",
        labz_key="labz",
        initial_points=None,
        initial_count=2,
        seed=123,
    )

    labx, labz = read_json_points(full_path=str(simple_full_json))
    candidates = {(float(x), float(z)) for x, z in zip(labx, labz)}
    assert len(points) == 2
    assert set(points).issubset(candidates)


def test_select_initial_points_override_works_for_json(simple_full_json):
    points = select_initial_points(
        full_path=str(simple_full_json),
        entry=None,
        detector_ids=(),
        fit=None,
        hkls=(),
        data_group="centers",
        dataset_names=("labx", "labz", "values"),
        source_format="json",
        initial_points=[(9, 8)],
        initial_count=2,
    )

    assert points == [(9.0, 8.0)]

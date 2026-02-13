import h5py

from chess_instrument_control_informer.hdf5_utils import clone_without_data


def test_clone_without_data_creates_empty_datasets(tmp_path, simple_full_file_with_metadata):
    new_path = tmp_path / "new.nxs"

    clone_without_data(
        full_path=str(simple_full_file_with_metadata),
        new_path=str(new_path),
        entry="entry",
        detector_ids=["0"],
        fit="uniform_fit",
        hkls=["2_2_0"],
        data_group="centers",
        dataset_names=("labx", "labz", "values"),
    )

    with h5py.File(new_path, "r") as f:
        centers = f["entry/0/uniform_fit/2_2_0/centers"]
        assert centers["labx"].shape == (0,)
        assert centers["labz"].shape == (0,)
        assert centers["values"].shape == (0,)
        assert f["entry/0/uniform_fit/2_2_0/meta"].shape == (3,)

import h5py

from chess_instrument_control_informer.config import Config
from chess_instrument_control_informer.cli import run


def test_run_creates_output_directory(tmp_path, simple_full_file):
    """Test that run() creates the output directory if it doesn't exist."""
    # Create a nested directory path that doesn't exist yet
    output_dir = tmp_path / "output" / "subdir"
    new_path = output_dir / "new.nxs"

    config = Config(
        full_file=str(simple_full_file),
        new_file=str(new_path),
        entry="entry",
        detector_ids=("0",),
        fit="uniform_fit",
        hkls=("2_2_0",),
        data_group="centers",
        dataset_names=("labx", "labz", "values"),
        initial_count=2,
        seed=42,
    )

    # This should not raise FileNotFoundError
    run(config)

    # Verify the file was created
    assert new_path.exists()

    # Verify it has the expected structure
    with h5py.File(new_path, "r") as f:
        centers = f["entry/0/uniform_fit/2_2_0/centers"]
        assert len(centers["labx"]) == 2
        assert len(centers["labz"]) == 2
        assert len(centers["values"]) == 2

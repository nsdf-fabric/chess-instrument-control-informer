import h5py

from chess_instrument_control_informer.config import Config
from chess_instrument_control_informer.cli import run


def test_run_with_realistic_structure(tmp_path, realistic_full_file):
    """Test run() with a structure matching the real strain_map.nxs file."""
    output_dir = tmp_path / "output"
    new_path = output_dir / "new_strain_map.nxs"

    config = Config(
        full_file=str(realistic_full_file),
        new_file=str(new_path),
        entry="v8-p3-10s-0deg_dataset1_strainanalysis",
        detector_ids=("0", "10", "2"),
        fit="uniform_fit",
        hkls=("2_2_0", "2_2_2", "4_0_0"),
        data_group="centers",
        dataset_names=("labx", "labz", "values"),
        initial_count=5,
        seed=42,
    )

    # This should work
    run(config)

    # Verify the file was created
    assert new_path.exists()

    # Verify structure and initial points
    with h5py.File(new_path, "r") as f:
        for det_id in ["0", "10", "2"]:
            for hkl in ["2_2_0", "2_2_2", "4_0_0"]:
                path = f"v8-p3-10s-0deg_dataset1_strainanalysis/{det_id}/uniform_fit/{hkl}/centers"
                centers = f[path]

                # Should have 5 initial points
                assert len(centers["labx"]) == 5
                assert len(centers["labz"]) == 5
                assert len(centers["values"]) == 5

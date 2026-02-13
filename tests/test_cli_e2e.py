"""Test that verifies CLI works end-to-end with the example config."""

import subprocess
import time

import h5py


def test_cli_with_example_config(tmp_path):
    """Test the CLI runs successfully with random_sampling config."""
    # Create a test config pointing to test files
    config_content = f"""
full_file: ./data/strain_map.nxs
new_file: {tmp_path}/test_output.nxs
entry: v8-p3-10s-0deg_dataset1_strainanalysis
detector_ids:
  - "0"
  - "10"
  - "2"
fit: uniform_fit
hkls:
  - "2_2_0"
  - "2_2_2"
  - "4_0_0"
data_group: centers
dataset_names:
  - labx
  - labz
  - values
initial_count: 3
seed: 42
"""
    config_path = tmp_path / "test_config.yaml"
    config_path.write_text(config_content)

    # Run the CLI for a short time
    proc = subprocess.Popen(
        ["uv", "run", "chess-instrument-control-informer", "--config", str(config_path)],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )

    # Let it run for 1 second to create the file
    time.sleep(1)
    proc.terminate()
    proc.wait(timeout=5)

    # Verify the output file exists
    output_file = tmp_path / "test_output.nxs"
    assert output_file.exists()

    # Verify it has data
    with h5py.File(output_file, "r") as f:
        centers = f["v8-p3-10s-0deg_dataset1_strainanalysis/0/uniform_fit/2_2_0/centers"]
        assert len(centers["labx"]) == 3
        assert len(centers["labz"]) == 3
        assert len(centers["values"]) == 3

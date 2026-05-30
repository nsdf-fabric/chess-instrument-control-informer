import json

import h5py

from chess_instrument_control_informer.config import Config
from chess_instrument_control_informer.cli import (
    _handle_location,
    _resolve_measurement_delay_seconds,
    run,
)


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


def test_run_json_creates_output_and_initial_points(tmp_path, simple_full_json):
    new_path = tmp_path / "output" / "reduced_data.json"

    config = Config(
        full_file=str(simple_full_json),
        new_file=str(new_path),
        source_format="json",
        initial_count=2,
        seed=42,
    )

    run(config)

    data = json.loads(new_path.read_text(encoding="utf-8"))
    assert len(data["labx"]) == 2
    assert len(data["labz"]) == 2
    assert len(data["0/data/norm"]) == 2
    assert data["metadata"] == {"example": True}


def test_run_json_processes_existing_locations(tmp_path, simple_full_json, monkeypatch):
    new_path = tmp_path / "output" / "reduced_data.json"
    loc_dir = tmp_path / "loc"
    loc_dir.mkdir()
    (loc_dir / "loc001.txt").write_text("labx labz\n2.1 20.1\n", encoding="utf-8")

    config = Config(
        full_file=str(simple_full_json),
        new_file=str(new_path),
        source_format="json",
        loc_dir=str(loc_dir),
    )

    monkeypatch.setattr("chess_instrument_control_informer.cli.watch_directory", lambda *args: None)
    run(config)

    data = json.loads(new_path.read_text(encoding="utf-8"))
    assert data["labx"] == [2.1]
    assert data["labz"] == [20.1]
    assert data["0/data/norm"] == [200.0]


def test_handle_location_applies_measurement_delay(tmp_path, simple_full_json, monkeypatch):
    loc_path = tmp_path / "loc001.txt"
    loc_path.write_text("labx,labz\n2.1,20.1\n", encoding="utf-8")

    config = Config(
        full_file=str(simple_full_json),
        new_file=str(tmp_path / "reduced_data.json"),
        source_format="json",
        measurement_delay_seconds=0.25,
    )

    sleep_calls: list[float] = []
    append_calls: list[dict] = []

    monkeypatch.setattr(
        "chess_instrument_control_informer.cli.time.sleep",
        lambda seconds: sleep_calls.append(seconds),
    )
    monkeypatch.setattr(
        "chess_instrument_control_informer.cli.append_interpolated_json_points",
        lambda **kwargs: append_calls.append(kwargs),
    )

    _handle_location(str(loc_path), config)

    assert sleep_calls == [0.25]
    assert len(append_calls) == 1


def test_resolve_measurement_delay_seconds_precedence(monkeypatch):
    monkeypatch.setenv("CHESS_MEASUREMENT_DELAY_SECONDS", "1.75")
    assert _resolve_measurement_delay_seconds(0.5, None) == 1.75
    assert _resolve_measurement_delay_seconds(0.5, 2.25) == 2.25

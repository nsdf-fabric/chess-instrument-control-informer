from __future__ import annotations

import argparse
from pathlib import Path
from typing import List, Optional, Tuple

from .config import Config, load_config, merge_config
from .hdf5_utils import append_interpolated_points, clone_without_data
from .locations import parse_location_file
from .sampling import select_initial_points
from .watcher import watch_directory


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="CHESS instrument control informer",
    )
    parser.add_argument("--config", help="Path to YAML config file")
    parser.add_argument("--full-file", help="Path to full HDF5 Nexus file")
    parser.add_argument("--new-file", help="Path to new HDF5 Nexus file")
    parser.add_argument("--entry", help="Entry group name in HDF5")
    parser.add_argument("--detector-ids", help="Comma-separated detector ids")
    parser.add_argument("--fit", help="Fit directory name")
    parser.add_argument("--hkls", help="Comma-separated HKL names")
    parser.add_argument("--data-group", default=None, help="Data group (default: centers)")
    parser.add_argument(
        "--dataset-names",
        help="Comma-separated dataset names for labx,labz,values",
    )
    parser.add_argument("--loc-dir", help="Directory to watch for location files")
    parser.add_argument(
        "--initial-points",
        help="Semicolon-separated points x,z; e.g. '0,0;1,1'",
    )
    parser.add_argument("--initial-count", type=int, help="Random initial sample count")
    parser.add_argument("--seed", type=int, help="Random seed")
    return parser


def main() -> None:
    parser = build_arg_parser()
    args = parser.parse_args()

    if args.config:
        config = load_config(args.config)
    else:
        config = _config_from_args(args)

    config = merge_config(
        config,
        full_file=args.full_file,
        new_file=args.new_file,
        entry=args.entry,
        detector_ids=_split_list(args.detector_ids),
        fit=args.fit,
        hkls=_split_list(args.hkls),
        data_group=args.data_group,
        dataset_names=_split_list(args.dataset_names),
        loc_dir=args.loc_dir,
        initial_points=_parse_points_arg(args.initial_points),
        initial_count=args.initial_count,
        seed=args.seed,
    )

    run(config)


def run(config: Config) -> None:
    clone_without_data(
        full_path=config.full_file,
        new_path=config.new_file,
        entry=config.entry,
        detector_ids=config.detector_ids,
        fit=config.fit,
        hkls=config.hkls,
        data_group=config.data_group,
        dataset_names=config.dataset_names,
    )

    points = select_initial_points(
        full_path=config.full_file,
        entry=config.entry,
        detector_ids=config.detector_ids,
        fit=config.fit,
        hkls=config.hkls,
        data_group=config.data_group,
        dataset_names=config.dataset_names,
        initial_points=config.initial_points,
        initial_count=config.initial_count,
        seed=config.seed,
    )

    if points:
        append_interpolated_points(
            full_path=config.full_file,
            new_path=config.new_file,
            entry=config.entry,
            detector_ids=config.detector_ids,
            fit=config.fit,
            hkls=config.hkls,
            data_group=config.data_group,
            dataset_names=config.dataset_names,
            points=points,
        )

    if config.loc_dir:
        _process_existing_locations(config)
        watch_directory(
            config.loc_dir,
            lambda path: _handle_location(path, config),
        )


def _process_existing_locations(config: Config) -> None:
    directory = Path(config.loc_dir)
    for path in sorted(directory.glob("*.txt")):
        _handle_location(str(path), config)


def _handle_location(path: str, config: Config) -> None:
    points = parse_location_file(path)
    if not points:
        return
    append_interpolated_points(
        full_path=config.full_file,
        new_path=config.new_file,
        entry=config.entry,
        detector_ids=config.detector_ids,
        fit=config.fit,
        hkls=config.hkls,
        data_group=config.data_group,
        dataset_names=config.dataset_names,
        points=points,
    )


def _split_list(value: Optional[str]) -> Optional[List[str]]:
    if value is None:
        return None
    return [v.strip() for v in value.split(",") if v.strip()]


def _parse_points_arg(value: Optional[str]) -> Optional[List[Tuple[float, float]]]:
    if not value:
        return None
    points: List[Tuple[float, float]] = []
    for item in value.split(";"):
        if not item.strip():
            continue
        parts = [p.strip() for p in item.split(",")]
        if len(parts) < 2:
            continue
        points.append((float(parts[0]), float(parts[1])))
    return points


def _config_from_args(args: argparse.Namespace) -> Config:
    missing = [
        name
        for name in ("full_file", "new_file", "entry", "detector_ids", "fit", "hkls")
        if getattr(args, name) is None
    ]
    if missing:
        raise SystemExit(f"Missing required arguments: {', '.join(missing)}")

    return Config(
        full_file=args.full_file,
        new_file=args.new_file,
        entry=args.entry,
        detector_ids=tuple(_split_list(args.detector_ids) or []),
        fit=args.fit,
        hkls=tuple(_split_list(args.hkls) or []),
        data_group=args.data_group or "centers",
        dataset_names=tuple(_split_list(args.dataset_names) or ["labx", "labz", "values"]),
        loc_dir=args.loc_dir,
        initial_points=_parse_points_arg(args.initial_points),
        initial_count=args.initial_count,
        seed=args.seed,
    )

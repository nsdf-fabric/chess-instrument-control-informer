# CHESS Instrument Control Informer

CHESS Watcher for Instrument Control Files

## Installation

This project uses [uv](https://docs.astral.sh/uv/) for dependency management.

```bash
# Install dependencies
uv sync

# Run the application
uv run chess-instrument-control-informer --help

# Run tests
uv run pytest tests/
```

## Usage

The informer supports two source formats:

- `hdf5` - default, backward-compatible Nexus/HDF5 behavior
- `json` - explicit flat reduced JSON mode for downstream stream-results monitoring

### Using a config file (recommended)

```bash
uv run chess-instrument-control-informer --config examples/random_sampling.yaml
```

For JSON mode:

```bash
uv run chess-instrument-control-informer --config examples/json_random_sampling.yaml
```

### Using command-line arguments

HDF5 mode remains the default:

```bash
uv run chess-instrument-control-informer \
  --full-file ./data/strain_map.nxs \
  --new-file ./output/new_strain_map.nxs \
  --entry v8-p3-10s-0deg_dataset1_strainanalysis \
  --detector-ids 0,10,2 \
  --fit uniform_fit \
  --hkls 2_2_0,2_2_2,4_0_0 \
  --loc-dir ./data/exp_01 \
  --initial-count 5

# Optional: simulate per-measurement latency
uv run chess-instrument-control-informer \
  --config examples/random_sampling.yaml \
  --measurement-delay-seconds 2.0
```

JSON mode must be requested explicitly:

```bash
uv run chess-instrument-control-informer \
  --source-format json \
  --full-file ./data/full_reduced_data.json \
  --new-file ./output/reduced_data.json \
  --labx-key labx \
  --labz-key labz \
  --loc-dir ./data/exp_01 \
  --initial-count 5 \
  --seed 42
```

In JSON mode the full input file is a flat dictionary with top-level coordinate
arrays such as `labx` and `labz`. The informer creates a new JSON file with all
list-valued keys present as empty arrays, then appends requested `labx`/`labz`
coordinates from initial sampling or location files. Other list-valued keys copy
the value from the nearest row in the full JSON file. JSON output is written
atomically and preserves `NaN` values so the downstream data-service can monitor
the file without reading partial writes.

See [examples/](examples/) for more configuration examples.

## Simulated Measurement Delay

You can delay processing of each new location file (to simulate measurement time)
using any of these knobs:

- YAML config key: `measurement_delay_seconds`
- CLI flag: `--measurement-delay-seconds`
- Environment variable: `CHESS_MEASUREMENT_DELAY_SECONDS`

Precedence is: CLI > environment variable > config file.

Examples:

```bash
CHESS_MEASUREMENT_DELAY_SECONDS=1.5 uv run chess-instrument-control-informer --config examples/random_sampling.yaml
```

```yaml
# in config.yaml
measurement_delay_seconds: 1.5
```

## Docker

```bash
# Build the image
docker build -t chess-instrument-control-informer .

# Run with --help
docker run --rm chess-instrument-control-informer

# Run with mounted config and data
docker run --rm \
  -v $(pwd)/examples:/config \
  -v $(pwd)/data:/data \
  -v $(pwd)/output:/output \
  chess-instrument-control-informer \
  chess-instrument-control-informer --config /config/docker_example.yaml
```

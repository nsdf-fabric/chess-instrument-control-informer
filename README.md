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

### Using a config file (recommended)

```bash
uv run chess-instrument-control-informer --config examples/random_sampling.yaml
```

### Using command-line arguments

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
```

See [examples/](examples/) for more configuration examples.

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

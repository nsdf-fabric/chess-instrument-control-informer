#!/bin/bash
# Example usage of chess-instrument-control-informer CLI

# Using a config file (recommended)
chess-instrument-control-informer --config examples/random_sampling.yaml

# Or using command-line arguments
chess-instrument-control-informer \
  --full-file ./data/strain_map.nxs \
  --new-file ./output/new_strain_map.nxs \
  --entry v8-p3-10s-0deg_dataset1_strainanalysis \
  --detector-ids 0,10,2 \
  --fit uniform_fit \
  --hkls 2_2_0,2_2_2,4_0_0 \
  --loc-dir ./data/exp_01 \
  --initial-count 5

# Or with specific initial points
chess-instrument-control-informer \
  --full-file ./data/strain_map.nxs \
  --new-file ./output/new_strain_map.nxs \
  --entry v8-p3-10s-0deg_dataset1_strainanalysis \
  --detector-ids 0,10,2 \
  --fit uniform_fit \
  --hkls 2_2_0,2_2_2,4_0_0 \
  --loc-dir ./data/exp_01 \
  --initial-points "0,0;10.5,-20.3;-47.33,-242.5"

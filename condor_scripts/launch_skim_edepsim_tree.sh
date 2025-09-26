#!/bin/bash

if [ $# -lt 1 ]; then
    echo "Usage: $0 <index>"
    exit 1
fi

INDEX=$1
INPUT_FILE="/storage/gpfs_data/neutrino/SAND-LAr/SAND-LAr-EDEPSIM-PROD/new-numu-CC-QE-in-GRAIN/grain_numu_ccqe/grain_numu_ccqe_${INDEX}/sand-events.${INDEX}.edep.root"
CONFIG_FILE="edepsim_tree_cuts_TDR.json"
OUTPUT_FILE="/storage/gpfs_data/neutrino/SAND-LAr/SAND-LAr-EDEPSIM-PROD/new-numu-CC-QE-in-GRAIN/grain_numu_ccqe/grain_numu_ccqe_${INDEX}/skimmed-sand-events.${INDEX}.edep.root"

source source_libs_neutrino01.sh
python3 skim_edepsim_tree.py "$INPUT_FILE" --config_file "$CONFIG_FILE" --output_file "$OUTPUT_FILE"


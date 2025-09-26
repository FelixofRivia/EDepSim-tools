#!/bin/bash

INPUT_FILE_PATTERN="/storage/gpfs_data/neutrino/SAND-LAr/SAND-LAr-EDEPSIM-PROD/new-numu-CC-QE-in-GRAIN/grain_numu_ccqe/grain_numu_ccqe_*/sand-events.*.edep.root"
OUTPUT_FILE="/storage/gpfs_data/neutrino/SAND-LAr/SAND-LAr-EDEPSIM-PROD/new-numu-CC-QE-in-GRAIN/grain_numu_ccqe/merged-skimmed-sand-events.edep.root"

source source_libs_neutrino01.sh
python3 merge_edepsim_tree.py "$INPUT_FILE_PATTERN" --output_file "$OUTPUT_FILE"


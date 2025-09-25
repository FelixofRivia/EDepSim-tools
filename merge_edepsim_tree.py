import os
import sys
import glob
import argparse
import ROOT

import edep_tree

def build_chain(tree_name, path_pattern):
    """Build a TChain from all ROOT files matching the pattern."""
    chain = ROOT.TChain(tree_name)
    files = glob.glob(path_pattern)
    if not files:
        print("Error: No input files matched the pattern.")
        return None
    for f in files:
        chain.Add(f)
    print(f"Added {len(files)} files to the chain.")
    return chain

if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    
    parser.add_argument("input_path_pattern", type=str, help="EDepSim input files (use wildcards)")
    parser.add_argument("--output_file", type=str, default="output/merged.root", help="Merged output file name")

    args = parser.parse_args()

    INPUT_PATH_PATTERN = args.input_path_pattern #"/storage/gpfs_data/neutrino/SAND-LAr/SAND-LAr-EDEPSIM-PROD/new-numu-CC-QE-in-GRAIN/grain_numu_ccqe/grain_numu_ccqe_*/sand-events.*.edep.root"
    OUTPUT_PATH = args.output_file

    # Suppress GUI popups from ROOT
    ROOT.gROOT.SetBatch(True)

    # Get matching input files
    input_files = glob.glob(INPUT_PATH_PATTERN)
    if not input_files:
        sys.exit("Error: No input files found.")

    # Use the first file as reference (for copying geometry and detsim trees)
    reference_file_path = input_files[0]
    input_file = ROOT.TFile.Open(reference_file_path)
    if not input_file or input_file.IsZombie():
        sys.exit(f"Error: Could not open reference file: {reference_file_path}")

    # Build event chain
    chain = build_chain("EDepSimEvents", INPUT_PATH_PATTERN)
    n_entries = chain.GetEntries()
    print(f"Total entries in chain: {n_entries}")

    # Prepare output
    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
    output_file = ROOT.TFile(OUTPUT_PATH, "RECREATE")

    # Copy all entries from chain
    print("Copying tree entries...")
    output_file.cd()
    output_tree = chain.CopyTree("")
    output_tree.Write("", ROOT.TObject.kWriteDelete)
    print("Tree copied.")

    # Copy detsim trees
    print("Copying detsim trees...")
    edep_tree.copy_detsim_trees(input_file, output_file)

    # Copy geometry
    print("Copying geometry...")
    edep_tree.copy_geometry(input_file, output_file)

    output_file.Close()
    input_file.Close()
    print(f"Done. Output written to: {OUTPUT_PATH}")

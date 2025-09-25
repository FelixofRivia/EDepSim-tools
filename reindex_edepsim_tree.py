import ROOT
import argparse
from array import array

import edep_tree

def reindex_tree(tree):

    new_tree = tree.CloneTree(0)
    n_entries = tree.GetEntries()

    event_id_new = array("i", [0])

    new_tree.SetBranchAddress("EventId", event_id_new)

    for i in range(n_entries):
        tree.GetEntry(i)
        event_id_new[0] = i  # Set new EventId = index
        new_tree.Fill()
        if i % 1000 == 0:
            print(f"Processed {i} / {n_entries}")
    
    return new_tree

def create_reindexed_file(file_name, output_name):

    # Disable pop-ups
    ROOT.gROOT.SetBatch(True)
    # Open file
    file = ROOT.TFile.Open(file_name)
    tree = file.Get("EDepSimEvents")

    output_file = ROOT.TFile(output_name, "RECREATE")

    # Get skimmed tree
    new_tree = reindex_tree(tree)

    # Write the new tree to the new file and close the files
    new_tree.AutoSave()

    edep_tree.copy_detsim_trees(file, output_file)

    edep_tree.copy_geometry(file, output_file)

    output_file.Close()
    file.Close()

if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument("input_file", type=str, help="EDepSim input file")
    parser.add_argument("--output_file", type=str, default="reindexed.root", help="Output ROOT file name")
    args = parser.parse_args()

    create_reindexed_file(args.input_file, args.output_file)



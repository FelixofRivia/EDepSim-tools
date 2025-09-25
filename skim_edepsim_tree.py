import ROOT
import numpy as np
import json
import argparse

import edep_tree

def create_default_config_file():
    # Create a configuration dictionary
    config = {
        "GeoCuts": {
            "Vertex_min_x": -800,
            "Vertex_max_x": 800,
            "Vertex_min_y": -800,
            "Vertex_max_y": 800,
            "Vertex_min_z": -400,
            "Vertex_max_z": 400
        },
        "TrackCuts": {
            "Min_number": 1,
            "Max_number": 9999,
            "Min_length_mm": 0,
            "Min_en_deposit_MeV": 0
        },
        "InteractionCuts": {
            "Allowed_interactions": ""
        }
    }

    # Write the configuration to a file
    with open('edepsim_tree_cuts.json', 'w') as configfile:
        json.dump(config, configfile, indent=4)

def read_config_file(config_name):
    # Read the configuration file
    with open(config_name, 'r') as configfile:
        config = json.load(configfile)
    return config

def get_transform_to_local_coord(file_name):
    ROOT.gSystem.Load("libGeom")
    ROOT.TGeoManager.Import(file_name)
    ROOT.gGeoManager.cd('/volWorld_PV/rockBox_lv_PV_0/volDetEnclosure_PV_0/volSAND_PV_0/MagIntVol_volume_PV_0/sand_inner_volume_PV_0/GRAIN_lv_PV_0/GRAIN_LAr_lv_PV_0')
    local = np.array([0.,0.,0.])
    master = np.array([0.,0.,0.])
    ROOT.gGeoManager.LocalToMaster(local, master)
    return master

def skim_tree(tree, cuts, master_transform):

    new_tree = tree.CloneTree(0)
    primaries_tot_lengths = {}
    primaries_tot_en_deposits = {}

    for entry in tree:
        # InteractionCuts
        if not cuts["InteractionCuts"]["Allowed_interactions"] == "":
            interaction_list = cuts["InteractionCuts"]["Allowed_interactions"].split('-')
            evt_interaction = entry.Event.Primaries[0].GetReaction().split("proc:")[1]
            if not any(interaction in evt_interaction for interaction in interaction_list):
                continue

        # GeoCuts
        vertex = entry.Event.Primaries[0].GetPosition()
        if not cuts["GeoCuts"]["Vertex_min_x"] <= vertex.X() - master_transform[0] <= cuts["GeoCuts"]["Vertex_max_x"]:
            continue
        if not cuts["GeoCuts"]["Vertex_min_y"] <= vertex.Y() - master_transform[1] <= cuts["GeoCuts"]["Vertex_max_y"]:
            continue
        if not cuts["GeoCuts"]["Vertex_min_z"] <= vertex.Z() - master_transform[2] <= cuts["GeoCuts"]["Vertex_max_z"]:
            continue

        # TrackCuts
        segments = entry.Event.SegmentDetectors
        count_tracks = 0
        for s in segments:
            if s.first == "LArHit":
                for v in s.second:
                    if v.GetPrimaryId() in primaries_tot_lengths:
                        primaries_tot_lengths[v.GetPrimaryId()] += v.GetTrackLength()
                        primaries_tot_en_deposits[v.GetPrimaryId()] += v.GetEnergyDeposit()
                    else:
                        primaries_tot_lengths[v.GetPrimaryId()] = v.GetTrackLength()
                        primaries_tot_en_deposits[v.GetPrimaryId()] = v.GetEnergyDeposit()
                for l in primaries_tot_lengths:
                    if primaries_tot_lengths[l] >= cuts["TrackCuts"]["Min_length_mm"] and primaries_tot_en_deposits[l] >= cuts["TrackCuts"]["Min_en_deposit_MeV"]:
                        count_tracks += 1
                primaries_tot_lengths.clear()
                primaries_tot_en_deposits.clear()
        if not cuts["TrackCuts"]["Min_number"] <= count_tracks <= cuts["TrackCuts"]["Max_number"]:
            continue
    
        new_tree.Fill()
    
    return new_tree

def create_skimmed_file(file_name, output_name, cuts):

    # Disable pop-ups
    ROOT.gROOT.SetBatch(True)
    # Open file
    file = ROOT.TFile.Open(file_name)
    tree = file.Get("EDepSimEvents")
    master_transform = get_transform_to_local_coord(file_name)

    output_file = ROOT.TFile(output_name, "RECREATE")

    # Get skimmed tree
    new_tree = skim_tree(tree, cuts, master_transform)

    # Write the new tree to the new file and close the files
    new_tree.AutoSave()

    edep_tree.copy_detsim_trees(file, output_file)

    edep_tree.copy_geometry(file, output_file)

    output_file.Close()
    file.Close()

if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument("input_file", type=str, help="EDepSim input file")
    parser.add_argument("--config_file", type=str, default="edepsim_tree_cuts.json", help="json configuration file")
    parser.add_argument("--output_file", type=str, default="output/skimmed.root", help="Output file name")
    args = parser.parse_args()

    #create_default_config_file()
    cuts = read_config_file(args.config_file)
    print(cuts)
    create_skimmed_file(args.input_file, args.output_file, cuts)



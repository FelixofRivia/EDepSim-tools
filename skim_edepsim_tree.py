import ROOT
import numpy as np
import json
import argparse

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

def plot_edep_tree_info(file_name):

    # Disable pop-ups
    ROOT.gROOT.SetBatch(True)
    # Open file
    file = ROOT.TFile.Open(file_name)
    # Get the TTree
    tree = file.Get("EDepSimEvents")

    master = get_transform_to_local_coord(file_name)

    # Create a canvas to draw the histograms
    c_interactions = ROOT.TCanvas("c_interactions", "c_interactions", 1920, 1080)
    c_vertices = ROOT.TCanvas("c_vertices", "c_vertices", 1920, 1080)
    c_vertices.Divide(2, 2)
    c_traj = ROOT.TCanvas("c_traj", "c_traj", 1920, 1080)
    c_seg = ROOT.TCanvas("c_seg", "c_seg", 1920, 1080)
    c_LAr = ROOT.TCanvas("c_LAr", "c_LAr", 1920, 1080)
    c_LAr.Divide(2, 3)

    # Create interaction histograms
    h_interaction = ROOT.TH1F("interaction", "interaction", 10, 0, 10)

    # Create vertex histograms
    h_vertex_X = ROOT.TH1F("vertex_X", "vertex_X; x (mm); entries", 200, -800, 800)
    h_vertex_Y = ROOT.TH1F("vertex_Y", "vertex_Y; y (mm); entries", 200, -800, 800)
    h_vertex_Z = ROOT.TH1F("vertex_Z", "vertex_Z; z (mm); entries", 200, -800, 800)
    h_vertex_3D = ROOT.TH3F("vertex_3D", "vertex_3D; x (mm); y (mm); z (mm)", 200, -800, 800, 200, -800, 800, 200, -800, 800)

    # Create trajectory histograms
    h_traj_multiplicity = ROOT.TH1F("traj_multiplicity", "traj_multiplicity", 200, 0, 1000)

    # Create segments histograms
    h_seg_detector = ROOT.TH1F("seg_detector", "seg_detector", 4, 0, 4)
    h_LArHit_seg_secondary_en_deposit_ratio = ROOT.TH1F("LArHit_seg_secondary_en_deposit_ratio", "LArHit_seg_secondary_en_deposit_ratio", 101, 0, 1.01)
    h_LArHit_en_deposit = ROOT.TH1F("LArHit_en_deposit", "LArHit_en_deposit; E (MeV); entries", 1000, 0, 100)
    h_LArHit_track_length = ROOT.TH1F("LArHit_track_length", "LArHit_track_length; l (mm); entries", 1000, 0, 1000)
    h_LArHit_primary_tot_length = ROOT.TH1F("LArHit_primary_tot_length", "LArHit_primary_tot_length; l (mm); entries", 1000, 0, 1000)
    h_LArHit_primary_tot_en_deposit = ROOT.TH1F("LArHit_primary_tot_en_deposit", "LArHit_primary_tot_en_deposit; E (MeV); entries", 1000, 0, 1000)
    h_LArHit_primary_multiplicity = ROOT.TH1F("LArHit_primary_multiplicity", "LArHit_primary_multiplicity; number of macrotracks; entries", 100, 0, 100)

    primaries_tot_lengths = {}
    primaries_tot_en_deposits = {}

    for entry in tree:
        # There is only one primary per event (the neutrino), segments have different primaries
        vertex = entry.Event.Primaries[0].GetPosition()
        h_vertex_X.Fill(vertex.X() - master[0])
        h_vertex_Y.Fill(vertex.Y() - master[1])
        h_vertex_Z.Fill(vertex.Z() - master[2])
        h_vertex_3D.Fill(vertex.X() - master[0], vertex.Y() - master[1], vertex.Z() - master[2])
        reaction = entry.Event.Primaries[0].GetReaction() # nu:14;tgt:1000180400;N:2112;q:1(v);proc:Weak[CC],DIS;
        h_interaction.Fill(reaction.split("proc:")[1], 1)
        trajectories = entry.Event.Trajectories
        segments = entry.Event.SegmentDetectors
        # for t in trajectories:
        #     print(t.GetTrackId(), t.GetName(), t.GetParentId(), t.GetPDGCode())
        for s in segments:
            h_seg_detector.Fill(s.first.c_str(), len(s.second))
            if s.first == "LArHit":
                for v in s.second:
                    if v.GetPrimaryId() in primaries_tot_lengths:
                        primaries_tot_lengths[v.GetPrimaryId()] += v.GetTrackLength()
                        primaries_tot_en_deposits[v.GetPrimaryId()] += v.GetEnergyDeposit()
                    else:
                        primaries_tot_lengths[v.GetPrimaryId()] = v.GetTrackLength()
                        primaries_tot_en_deposits[v.GetPrimaryId()] = v.GetEnergyDeposit()
                    h_LArHit_track_length.Fill(v.GetTrackLength())
                    h_LArHit_en_deposit.Fill(v.GetEnergyDeposit())
                    h_LArHit_seg_secondary_en_deposit_ratio.Fill(v.GetSecondaryDeposit()/v.GetEnergyDeposit())
                    #print(v.GetPrimaryId(), v.GetEnergyDeposit(), v.GetSecondaryDeposit(), v.GetTrackLength())
                for l in primaries_tot_lengths:
                    h_LArHit_primary_tot_length.Fill(primaries_tot_lengths[l])
                for e in primaries_tot_en_deposits:
                    h_LArHit_primary_tot_en_deposit.Fill(primaries_tot_en_deposits[e])
                h_LArHit_primary_multiplicity.Fill(len(primaries_tot_lengths))
                primaries_tot_lengths.clear()
                primaries_tot_en_deposits.clear()
        h_traj_multiplicity.Fill(len(trajectories))


    # Draw the histograms
    c_interactions.cd()
    h_interaction.Draw()

    c_vertices.cd(1)
    h_vertex_X.Draw()
    c_vertices.cd(2)
    h_vertex_Y.Draw()
    c_vertices.cd(3)
    h_vertex_Z.Draw()
    c_vertices.cd(4)
    h_vertex_3D.Draw()

    c_traj.cd()
    h_traj_multiplicity.Draw()

    c_seg.cd()
    h_seg_detector.Draw()

    c_LAr.cd(1)
    h_LArHit_en_deposit.Draw()
    c_LAr.cd(2)
    h_LArHit_seg_secondary_en_deposit_ratio.Draw()
    c_LAr.cd(3)
    h_LArHit_track_length.Draw()
    c_LAr.cd(4)
    h_LArHit_primary_tot_length.Draw()
    c_LAr.cd(5)
    h_LArHit_primary_tot_en_deposit.Draw()
    c_LAr.cd(6)
    h_LArHit_primary_multiplicity.Draw()


    # Update the canvas to display the histograms
    c_interactions.Update()
    c_interactions.SaveAs("output/interactions.png")

    c_vertices.Update()
    c_vertices.SaveAs("output/vertices.png")

    c_traj.Update()
    c_traj.SaveAs("output/traj.png")

    c_seg.Update()
    c_seg.SaveAs("output/seg.png")

    c_LAr.Update()
    c_LAr.SaveAs("output/LAr.png")

    file.Close()

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

    # Copy the directory from the original file to the new file
    output_file.cd()
    output_file.mkdir("DetSimPassThru") 

    # Copy all contents of the directory
    for t_name in ["InputKinem", "InputFiles", "gRooTracker"]:
        t = file.Get(f"DetSimPassThru/{t_name}")
        output_file.cd("DetSimPassThru")
        t.CloneTree().Write()

    # Copy the geometry from the original file to the new file
    geo_manager = file.Get("EDepSimGeometry")
    output_file.cd()
    geo_manager.Write()

    output_file.Close()
    file.Close()

if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    
    parser.add_argument("input_file", type=str, help="EDepSim input file")
    parser.add_argument("--config_file", type=str, default="edepsim_tree_cuts.json", help="json configuration file")
    parser.add_argument("--output_file", type=str, default="skimmed.edep-sim.root", help="Output ROOT file name")

    args = parser.parse_args()

    input_file = args.input_file
    config_file = args.config_file
    output_file = args.output_file

    plot_edep_tree_info(input_file)
    #create_default_config_file()
    #cuts = read_config_file(config_file)
    #print(cuts)
    #create_skimmed_file(input_file, output_file, cuts)
    #plot_edep_tree_info(output_file)



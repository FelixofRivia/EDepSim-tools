import ROOT
import numpy as np
import argparse
import os

def get_transform_to_local_coord(file_name):
    ROOT.gSystem.Load("libGeom")
    ROOT.TGeoManager.Import(file_name)
    ROOT.gGeoManager.cd('/volWorld_PV/rockBox_lv_PV_0/volDetEnclosure_PV_0/volSAND_PV_0/MagIntVol_volume_PV_0/sand_inner_volume_PV_0/GRAIN_lv_PV_0/GRAIN_LAr_lv_PV_0')
    local = np.array([0.,0.,0.])
    master = np.array([0.,0.,0.])
    ROOT.gGeoManager.LocalToMaster(local, master)
    return master

def plot_edep_tree_info(file_name, output_folder):

    # Disable pop-ups
    ROOT.gROOT.SetBatch(True)

    file = ROOT.TFile.Open(file_name)
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
    c_interactions.SaveAs(os.path.join(output_folder, "interactions.png"))

    c_vertices.Update()
    c_vertices.SaveAs(os.path.join(output_folder, "vertices.png"))

    c_traj.Update()
    c_traj.SaveAs(os.path.join(output_folder, "trajectories.png"))

    c_seg.Update()
    c_seg.SaveAs(os.path.join(output_folder, "segments.png"))

    c_LAr.Update()
    c_LAr.SaveAs(os.path.join(output_folder, "LAr_hits.png"))

    file.Close()

if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument("input_file", type=str, help="EDepSim input file")
    parser.add_argument("--output_folder", type=str, default="output", help="Output folder")
    args = parser.parse_args()

    plot_edep_tree_info(args.input_file, args.output_folder)



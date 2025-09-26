# EDepSim-tools

Python scripts for EDepSim tree manipulation and HTCondor job submissions.

## Scripts

There is no strict order for using these scripts, but a typical workflow could be:

> skim N files → merge → reindex

- **skim_edepsim_tree.py** – Given an input EDepSim file, creates a new one with events passing cuts defined in a JSON configuration file.
- **merge_edepsim_tree.py** – Uses wildcards to select multiple EDepSim files and merges them into one.
- **reindex_edepsim_tree.py** – Given an input EDepSim file, creates a new one where `Event_id = entry_index`.
- **plot_edepsim_tree.py** – Produces plots of interaction vertices and tracks.
- **edep_tree.py** – Utility library for copying geometry and detsim trees between EDepSim files.

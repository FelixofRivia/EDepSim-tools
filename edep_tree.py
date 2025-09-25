def copy_detsim_trees(input_file, output_file):
    """Copy detsim trees from reference input file to output file."""
    directory = "DetSimPassThru"
    tree_names = ["InputKinem", "InputFiles", "gRooTracker"]
    output_file.cd()
    output_file.mkdir(directory)
    for name in tree_names:
        tree = input_file.Get(f"{directory}/{name}")
        if tree:
            output_file.cd(directory)
            tree.CloneTree().Write()
            print(f"Copied tree: {directory}/{name}")
        else:
            print(f"Warning: Tree not found - {directory}/{name}")


def copy_geometry(input_file, output_file):
        geo = input_file.Get("EDepSimGeometry")
        if geo:
            output_file.cd()
            geo.Write()
            print("Geometry copied.")
        else:
            print("Warning: EDepSimGeometry not found.")
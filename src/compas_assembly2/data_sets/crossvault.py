from compas.data import json_load


if __name__ == "__main__":

    meshes = json_load("src/compas_assembly2/data_sets/crossvault.json")

    # arch = Arch(rise=1, span=20, thickness=0.5, depth=10, n=5)
    # model = arch.blocks()
    # print(model)
    # model.print()
    # ViewerModel.run(model, scale_factor=1)

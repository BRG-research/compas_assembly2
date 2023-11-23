from compas_assembly2 import ViewerModel
from compas.data import json_load
from compas_assembly2 import Model, Node

if __name__ == "__main__":
    # ==========================================================================
    # ELEMENTS FROM JSON
    # ==========================================================================
    path = "src/compas_assembly2/data_sets/element/element_compas_timber_0.json"
    elements_json = json_load(path)

    # ==========================================================================
    # CREATE MODEL
    # ==========================================================================
    model = Model("model_1")

    # ==========================================================================
    # CREATE A DICTIONARY OF NODES BASED ON ELEMENT INDEX FOR GROUPING
    # ==========================================================================
    for element in elements_json:
        group_id = "model_1_truss_" + str(element.id[0])
        if not model.contains_node(group_id):
            model.add_node(Node(name=group_id))
        model.hierarchy[group_id].add_element(element)

    # ==========================================================================
    # Methods: prune, graft
    # ==========================================================================
    # model.graft()
    # # model.flatten()
    model.print()

    # ==========================================================================
    # VIEW2
    # ==========================================================================
    ViewerModel.run(model, scale_factor=0.001)

from compas_assembly2 import Model, Node, ViewerModel
from compas.data import json_load

if __name__ == "__main__":

    # ==========================================================================
    # ELEMENTS FROM JSON
    # ==========================================================================
    path = "src/compas_assembly2/data_sets/model/model_hex_barrel_vault.json"
    elements_json = json_load(path)

    # ==========================================================================
    # MODEL
    # ==========================================================================
    # --------------------------------------------------------------------------
    # create the model
    # --------------------------------------------------------------------------
    model = Model("barrel_vault_hex")

    # --------------------------------------------------------------------------
    # add hierarchy
    # --------------------------------------------------------------------------

    structures = Node("structures", elements=[])  # create node
    beams = Node("beams", elements=[])  # create node
    plates = Node("panels", elements=[])  # create node

    model.add_node(structures)  # create hierarchy by adding nodes to nodes
    structures.add_node(beams)  # create hierarchy by adding nodes to nodes
    structures.add_node(plates)  # create hierarchy by adding nodes to nodes

    # --------------------------------------------------------------------------
    # add elements to the hierarchy
    # --------------------------------------------------------------------------
    for element in elements_json:
        if element.name == "BEAM":
            beams.add_element(element)
        elif element.name == "PLATE":
            plates.add_element(element)

    # --------------------------------------------------------------------------
    # add linkages
    # --------------------------------------------------------------------------
    model.add_interaction(elements_json[8], elements_json[13])
    model.add_interaction(elements_json[13], elements_json[11])
    model.add_interaction(elements_json[7], elements_json[10])
    model.add_interaction(elements_json[6], elements_json[12])
    model.add_interaction(elements_json[12], elements_json[9])
    model.add_interaction(elements_json[18], elements_json[15])
    model.add_interaction(elements_json[17], elements_json[14])
    model.add_interaction(elements_json[14], elements_json[16])

    model.add_interaction(elements_json[7], elements_json[8])
    model.add_interaction(elements_json[7], elements_json[13])
    model.add_interaction(elements_json[7], elements_json[6])
    model.add_interaction(elements_json[7], elements_json[12])
    model.add_interaction(elements_json[10], elements_json[11])
    model.add_interaction(elements_json[10], elements_json[9])
    model.add_interaction(elements_json[10], elements_json[12])
    model.add_interaction(elements_json[10], elements_json[13])

    model.add_interaction(elements_json[18], elements_json[17])
    model.add_interaction(elements_json[18], elements_json[6])
    model.add_interaction(elements_json[18], elements_json[14])
    model.add_interaction(elements_json[18], elements_json[12])
    model.add_interaction(elements_json[15], elements_json[16])
    model.add_interaction(elements_json[15], elements_json[9])
    model.add_interaction(elements_json[15], elements_json[14])
    model.add_interaction(elements_json[15], elements_json[12])

    # ==========================================================================
    # VIEW2
    # ==========================================================================
    model.print()
    ViewerModel.run(model=model, scale_factor=0.001)
